from __future__ import annotations

import asyncio
import difflib
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from matrx_ai.tools.vfs.backends.memory import MemoryBackend
from matrx_ai.tools.vfs.commands import VfsCommandRunner, load_all
from matrx_ai.tools.vfs.core import MatrxAsyncFS
from matrx_ai.tools.vfs.shell.env import ShellEnv

# Used to scrub the host-side temp dir prefix from real-mode output.  Both
# stdout and stderr can leak the real path because GNU coreutils echo whatever
# argv we passed in.  We replace it with the empty string so the comparison is
# against the same logical path the virtual run sees ("/foo" vs "/foo").
_TIMESTAMP_RE = re.compile(
    rb"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d+\s+(?:\d{2}:\d{2}|\d{4})"
)
# `ls -l` emits `drwxr-xr-x  1 user user  size <month> <day> <hh:mm> name`
# We strip the user/group/size/date columns down to mode + name to focus on
# what the VFS can actually reproduce.
_LS_LONG_RE = re.compile(
    rb"^([dl\-bcsp][rwxsStTl\-]{9})\.?\s+\d+\s+\S+\s+\S+\s+\d+\s+"
    rb"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d+\s+"
    rb"(?:\d{2}:\d{2}|\d{4})\s+(.*)$",
    re.MULTILINE,
)
_LS_TOTAL_RE = re.compile(rb"^total\s+\d+\n", re.MULTILINE)


@dataclass(slots=True)
class CommandOutcome:
    stdout: bytes
    stderr: bytes
    exit_code: int


def argv_real(argv: list[str], tmpdir: str) -> list[str]:
    # Translate every absolute "/foo" arg to "<tmpdir>/foo".  Args starting with
    # "-" are options and pass through unchanged.  Args that are not absolute
    # (relative names, patterns) also pass through.
    out: list[str] = []
    for a in argv:
        if a.startswith("/") and not a.startswith("//"):
            # Strip leading slash, join with tmpdir.  Use rstrip so "/" maps to
            # the tmpdir itself.
            rel = a.lstrip("/")
            out.append(str(Path(tmpdir) / rel) if rel else tmpdir)
        else:
            out.append(a)
    return out


def argv_virtual(argv: list[str]) -> list[str]:
    return list(argv)


def _build_real_tree(tmpdir: Path, tree: dict[str, Any]) -> None:
    # Pre-create directories first so files can be placed inside them.
    dirs = [p for p, v in tree.items() if p.endswith("/") or v is None]
    files = [(p, v) for p, v in tree.items() if not (p.endswith("/") or v is None)]
    for p in sorted(dirs, key=len):
        rel = p.strip("/").strip()
        if not rel:
            continue
        (tmpdir / rel).mkdir(parents=True, exist_ok=True)
    for p, v in files:
        rel = p.lstrip("/")
        target = tmpdir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(v, bytes):
            target.write_bytes(v)
        elif isinstance(v, str):
            target.write_bytes(v.encode("utf-8"))
        else:
            target.write_bytes(b"")


async def _build_virtual_tree(vfs: MatrxAsyncFS, tree: dict[str, Any]) -> None:
    dirs = [p for p, v in tree.items() if p.endswith("/") or v is None]
    files = [(p, v) for p, v in tree.items() if not (p.endswith("/") or v is None)]
    for p in sorted(dirs, key=len):
        norm = p.rstrip("/")
        if not norm or norm == "/":
            continue
        await vfs._makedirs(norm, exist_ok=True)
    for p, v in files:
        parent = "/".join(p.split("/")[:-1])
        if parent and parent != "/":
            await vfs._makedirs(parent, exist_ok=True)
        if isinstance(v, bytes):
            data = v
        elif isinstance(v, str):
            data = v.encode("utf-8")
        else:
            data = b""
        await vfs._pipe_file(p, data)


class FidelityHarness:
    def __init__(self, tree: dict[str, Any]) -> None:
        self._tmpdir_obj = tempfile.TemporaryDirectory(prefix="vfs-fidelity-")
        self.tmpdir = Path(self._tmpdir_obj.name)
        self.tree = tree

        load_all()

        self.backend = MemoryBackend()
        self.workspace_id = "fidelity"
        self.vfs = MatrxAsyncFS(
            backend=self.backend, workspace_id=self.workspace_id, asynchronous=True
        )
        self.runner = VfsCommandRunner(self.vfs)
        self._built = False

    async def setup(self) -> None:
        if self._built:
            return
        await self.backend.ensure_workspace_root(self.workspace_id)
        _build_real_tree(self.tmpdir, self.tree)
        await _build_virtual_tree(self.vfs, self.tree)
        self._built = True

    def cleanup(self) -> None:
        try:
            self._tmpdir_obj.cleanup()
        except OSError:
            pass

    async def __aenter__(self) -> FidelityHarness:
        await self.setup()
        return self

    async def __aexit__(self, *exc: Any) -> None:
        self.cleanup()

    # ------------------------------------------------------------------
    # Runners
    # ------------------------------------------------------------------

    async def run_real(
        self,
        argv: list[str],
        cwd: str | None = None,
    ) -> CommandOutcome:
        translated = argv_real(argv, str(self.tmpdir))
        # Use basename argv[0] so error messages say "ls: ..." not "/usr/bin/ls: ..."
        run_cwd = str(self.tmpdir) if cwd is None else cwd
        # Run subprocess in a thread to keep the test loop free.
        return await asyncio.to_thread(self._run_real_sync, translated, run_cwd)

    def _run_real_sync(self, argv: list[str], cwd: str) -> CommandOutcome:
        try:
            res = subprocess.run(
                argv,
                cwd=cwd,
                capture_output=True,
                timeout=10,
                env={"LC_ALL": "C", "LANG": "C", "PATH": "/usr/bin:/bin"},
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            return CommandOutcome(
                stdout=exc.stdout or b"",
                stderr=(exc.stderr or b"") + b"timeout\n",
                exit_code=124,
            )
        return CommandOutcome(stdout=res.stdout, stderr=res.stderr, exit_code=res.returncode)

    async def run_virtual(
        self,
        argv: list[str],
        cwd: str | None = None,
    ) -> CommandOutcome:
        translated = argv_virtual(argv)
        env = ShellEnv(cwd=cwd or "/")
        result = await self.runner.run(translated, env, b"", env.cwd)
        return CommandOutcome(
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.exit_code,
        )

    # ------------------------------------------------------------------
    # Normalization helpers
    # ------------------------------------------------------------------

    def normalize_real(self, data: bytes) -> bytes:
        # Strip the temp dir prefix so paths read identically to the virtual side.
        # Substitution rules:
        #   - "<tmpdir>/<rest>" -> "/<rest>"      (preserves the leading slash)
        #   - "<tmpdir>"        -> "/"            (the tmpdir alone IS the root)
        # We do these in two steps: first replace "<tmpdir>/" with "/", then
        # replace the bare tmpdir with "/".
        prefix = str(self.tmpdir).encode()
        out = data.replace(prefix + b"/", b"/")
        out = out.replace(prefix, b"/")
        return out

    def diff_outcomes(
        self,
        real: CommandOutcome,
        virt: CommandOutcome,
        *,
        normalize_paths: bool = True,
        strip_timestamps: bool = False,
    ) -> list[str]:
        real_out = self.normalize_real(real.stdout) if normalize_paths else real.stdout
        real_err = self.normalize_real(real.stderr) if normalize_paths else real.stderr
        virt_out = virt.stdout
        virt_err = virt.stderr
        if strip_timestamps:
            real_out = strip_ls_timestamps(real_out)
            virt_out = strip_ls_timestamps(virt_out)
        diffs: list[str] = []
        if real.exit_code != virt.exit_code:
            diffs.append(f"exit: real={real.exit_code} virtual={virt.exit_code}")
        if real_out != virt_out:
            diffs.append("stdout differs:\n" + _udiff(real_out, virt_out, "stdout"))
        if real_err != virt_err:
            diffs.append("stderr differs:\n" + _udiff(real_err, virt_err, "stderr"))
        return diffs


def _udiff(a: bytes, b: bytes, label: str) -> str:
    sa = a.decode("utf-8", errors="replace").splitlines(keepends=True)
    sb = b.decode("utf-8", errors="replace").splitlines(keepends=True)
    return "".join(
        difflib.unified_diff(sa, sb, fromfile=f"real.{label}", tofile=f"virtual.{label}")
    )


def strip_ls_timestamps(text: bytes) -> bytes:
    # Replace `total NN` lines with `total *` and any month/day/time triplet
    # with `<DATE>`.  The two implementations don't agree on block totals;
    # collapsing them keeps the test focused on file presence + mode.
    out = _LS_TOTAL_RE.sub(b"total *\n", text)
    out = _TIMESTAMP_RE.sub(b"<DATE>", out)
    return out


def assert_outcomes_equal(
    harness: FidelityHarness,
    real: CommandOutcome,
    virt: CommandOutcome,
    argv: list[str],
    *,
    normalize_paths: bool = True,
    strip_timestamps: bool = False,
) -> None:
    diffs = harness.diff_outcomes(
        real, virt, normalize_paths=normalize_paths, strip_timestamps=strip_timestamps
    )
    if not diffs:
        return
    msg_lines = [
        f"COMMAND: {' '.join(argv)}",
        f"REAL:    exit={real.exit_code} stdout={real.stdout!r} stderr={real.stderr!r}",
        f"VIRTUAL: exit={virt.exit_code} stdout={virt.stdout!r} stderr={virt.stderr!r}",
        "DIFFERENCES:",
        *diffs,
    ]
    raise AssertionError("\n".join(msg_lines))
