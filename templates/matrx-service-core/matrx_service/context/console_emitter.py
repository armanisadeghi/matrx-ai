from __future__ import annotations

import datetime
import json
import os
from pathlib import Path
from typing import Any

from matrx_utils import vcprint

from matrx_service.context.events import (
    BrokerPayload,
    CompletionPayload,
    ToolEventPayload,
)

TEMP_DIR = Path(__file__).resolve().parent.parent.parent.parent / "temp"
DEFAULT_SAVE_DIR = TEMP_DIR / "emitter_responses"


class ConsoleEmitter:
    def __init__(
        self,
        label: str = "console",
        debug: bool = False,
        accumulate: bool = True,
    ):
        self.label = label
        self.debug = debug
        self.accumulate = accumulate
        self.cancelled = False

        if self.accumulate:
            self._accumulated: dict[str, list[Any]] = {
                "chunks": [],
                "status_updates": [],
                "data": [],
                "completions": [],
                "errors": [],
                "tool_events": [],
                "brokers": [],
            }
            self._full_text = ""

    async def send_chunk(self, text: str) -> None:
        vcprint(data=text, verbose=True, color="green", chunks=True)
        if self.accumulate:
            self._full_text += text
            self._accumulated["chunks"].append(text)

    async def send_status_update(
        self,
        status: str,
        system_message: str | None = None,
        user_message: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        info = {
            "status": status,
            "system_message": system_message,
            "user_message": user_message,
            "metadata": metadata,
        }
        vcprint(data=info, verbose=True, title=f"[{self.label}] status_update", color="cyan")
        if self.accumulate:
            self._accumulated["status_updates"].append(info)

    async def send_data(self, data: Any) -> None:
        vcprint(data=data, verbose=True, title=f"[{self.label}] data", color="green")
        if self.accumulate:
            self._accumulated["data"].append(data)

    async def send_completion(self, payload: CompletionPayload) -> None:
        dump = payload.model_dump()
        vcprint(data=dump, verbose=True, title=f"[{self.label}] completion", color="green")
        if self.accumulate:
            self._accumulated["completions"].append(dump)

    async def send_error(
        self,
        error_type: str,
        message: str,
        user_message: str | None = None,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        error = {
            "error_type": error_type,
            "message": message,
            "user_message": user_message or "Sorry. An error occurred.",
            "code": code,
            "details": details,
        }
        vcprint(data=error, verbose=True, title=f"[{self.label}] error", color="red")
        if self.accumulate:
            self._accumulated["errors"].append(error)

    async def send_tool_event(self, event_data: ToolEventPayload | dict[str, Any]) -> None:
        if isinstance(event_data, dict):
            dump = event_data
        else:
            dump = event_data.model_dump()
        vcprint(data=dump, verbose=True, title=f"[{self.label}] tool_event", color="cyan")
        if self.accumulate:
            self._accumulated["tool_events"].append(dump)

    async def send_broker(self, broker: BrokerPayload) -> None:
        dump = broker.model_dump()
        vcprint(data=dump, verbose=True, title=f"[{self.label}] broker", color="green")
        if self.accumulate:
            self._accumulated["brokers"].append(dump)

    async def send_end(self, reason: str = "complete") -> None:
        vcprint(
            data=f"End of transmission (reason={reason})",
            verbose=True,
            title=f"[{self.label}] end",
            color="green",
        )
        if self.accumulate:
            await self._save_accumulated()

    async def send_cancelled(self) -> None:
        await self.send_error(
            error_type="task_cancelled",
            message="Task was cancelled.",
            user_message="Your request was cancelled.",
        )
        await self.send_end(reason="cancelled")

    async def fatal_error(
        self,
        error_type: str,
        message: str,
        user_message: str | None = None,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        await self.send_error(error_type, message, user_message, code, details)
        await self.send_end()

    async def _save_accumulated(self) -> None:
        if not self.accumulate:
            return

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"{self.label}_{timestamp}.json"
        filepath = DEFAULT_SAVE_DIR / filename

        os.makedirs(DEFAULT_SAVE_DIR, exist_ok=True)

        output = {
            "metadata": {
                "label": self.label,
                "timestamp": datetime.datetime.now().isoformat(),
                "text_length": len(self._full_text),
                "counts": {k: len(v) for k, v in self._accumulated.items()},
            },
            "text": self._full_text,
            "events": self._accumulated,
        }

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(output, f, indent=2, ensure_ascii=False, default=str)
            vcprint(f"[ConsoleEmitter] Saved to {filepath}", color="pink")
        except Exception as e:
            vcprint(f"[ConsoleEmitter] Failed to save: {e}", color="red")
