#!/usr/bin/env bash
# release.sh — Bump version, commit, tag, and push.
# PyPI publishing is handled by GitHub Actions on tag push.
#
# Source of truth: git tags (hatch-vcs), with __init__.py fallback kept in sync.
#
# Usage:
#   ./scripts/release.sh              # patch bump  (default)
#   ./scripts/release.sh --patch      # patch bump
#   ./scripts/release.sh --minor      # minor bump
#   ./scripts/release.sh --major      # major bump
#   ./scripts/release.sh --message "feat: something"   # custom commit message
#   ./scripts/release.sh --dry-run    # preview without changes
set -euo pipefail

# ── Resolve repo root ────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

PROJECT_NAME="matrx-ai"
GITHUB_REPO="armanisadeghi/matrx-ai"
PYPI_PACKAGE="matrx-ai"
INIT_PY="matrx_ai/__init__.py"
README="README.md"
REMOTE="origin"
BRANCH="main"

# ── Colors ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

info()    { echo -e "${CYAN}[INFO]${NC}  $*"; }
ok()      { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
fail()    { echo -e "${RED}[FAIL]${NC}  $*" >&2; exit 1; }
preview() { echo -e "${YELLOW}[DRY]${NC}   $*"; }

# ── Portable in-place sed ────────────────────────────────────────────────────
sedi() {
    if sed --version 2>/dev/null | grep -q GNU; then
        sed -i "$@"
    else
        sed -i '' "$@"
    fi
}

# ── Parse flags ──────────────────────────────────────────────────────────────
BUMP_TYPE="patch"
CUSTOM_MESSAGE=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --patch)   BUMP_TYPE="patch"; shift ;;
        --minor)   BUMP_TYPE="minor"; shift ;;
        --major)   BUMP_TYPE="major"; shift ;;
        --message|-m)
            [[ -n "${2:-}" ]] || fail "--message requires an argument."
            CUSTOM_MESSAGE="$2"; shift 2 ;;
        --dry-run) DRY_RUN=true; shift ;;
        -h|--help)
            grep '^#' "$0" | head -20 | sed 's/^# \?//'
            exit 0 ;;
        *) fail "Unknown flag: $1. Use --patch, --minor, --major, --message, or --dry-run." ;;
    esac
done

# ── Pre-flight checks ────────────────────────────────────────────────────────
[[ -f "$INIT_PY" ]] || fail "$INIT_PY not found."

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
[[ "$CURRENT_BRANCH" == "$BRANCH" ]] \
    || fail "Not on '$BRANCH' branch (currently on '$CURRENT_BRANCH'). Switch first."

if [[ -n "$(git diff --cached --name-only)" ]]; then
    fail "Staged but uncommitted changes detected. Commit or unstage them first."
fi

if ! git diff --quiet; then
    fail "Uncommitted changes detected. Commit them first."
fi

# ── Read current version from latest git tag (hatch-vcs is source of truth) ──
CURRENT_TAG=$(git tag --list 'v[0-9]*.[0-9]*.[0-9]*' --sort=-version:refname | head -1)
if [[ -z "$CURRENT_TAG" ]]; then
    fail "No version tag found (expected format: vX.Y.Z). Create an initial tag first:
  git tag v0.1.0 && git push origin v0.1.0"
fi

CURRENT_VERSION="${CURRENT_TAG#v}"
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"

# ── Calculate new version ────────────────────────────────────────────────────
case "$BUMP_TYPE" in
    patch) NEW_VERSION="${MAJOR}.${MINOR}.$((PATCH + 1))" ;;
    minor) NEW_VERSION="${MAJOR}.$((MINOR + 1)).0" ;;
    major) NEW_VERSION="$((MAJOR + 1)).0.0" ;;
esac

NEW_TAG="v${NEW_VERSION}"

# ── Check tag doesn't already exist ──────────────────────────────────────────
if git rev-parse "$NEW_TAG" &>/dev/null; then
    fail "Tag $NEW_TAG already exists. Resolve manually or choose a different bump type."
fi

# ── Build commit message ─────────────────────────────────────────────────────
if [[ -n "$CUSTOM_MESSAGE" ]]; then
    COMMIT_MSG="$CUSTOM_MESSAGE"
else
    COMMIT_MSG="release: ${NEW_TAG}"
fi

# ── Preview ──────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}  ${PROJECT_NAME} release${NC}"
echo -e "  ─────────────────────────────────────────────"
echo -e "  Bump type  : ${CYAN}${BUMP_TYPE}${NC}"
echo -e "  Old version: ${YELLOW}${CURRENT_VERSION}${NC}  (from tag ${CURRENT_TAG})"
echo -e "  New version: ${GREEN}${NEW_VERSION}${NC}"
echo -e "  Tag        : ${GREEN}${NEW_TAG}${NC}"
echo -e "  Commit msg : ${CYAN}${COMMIT_MSG}${NC}"
$DRY_RUN && echo -e "  Mode       : ${YELLOW}DRY RUN — nothing will be changed${NC}"
echo -e "  ─────────────────────────────────────────────"
echo ""

if $DRY_RUN; then
    preview "Would update fallback __version__ in $INIT_PY: $CURRENT_VERSION → $NEW_VERSION"
    [[ -f "$README" ]] && preview "Would update $README version history"
    preview "Would commit: '$COMMIT_MSG'"
    preview "Would create annotated tag: $NEW_TAG"
    preview "Would push to $REMOTE/$BRANCH"
    echo ""
    preview "Dry run complete. No changes made."
    exit 0
fi

# ── Update __init__.py fallback version ──────────────────────────────────────
info "Bumping fallback __version__ in $INIT_PY..."
sedi "s/^__version__ = \"${CURRENT_VERSION}\"/__version__ = \"${NEW_VERSION}\"/" "$INIT_PY"

INIT_VERSION=$(grep '^__version__ = ' "$INIT_PY" | head -1 | sed 's/__version__ = "\(.*\)"/\1/')
[[ "$INIT_VERSION" == "$NEW_VERSION" ]] \
    || fail "Version write failed — $INIT_PY still shows $INIT_VERSION."
ok "$INIT_PY → $NEW_VERSION"

# ── Update README version history (if table exists) ──────────────────────────
FILES_TO_ADD=("$INIT_PY")

if [[ -f "$README" ]] && grep -q '^| Version | Highlights |' "$README"; then
    info "Inserting v${NEW_VERSION} entry in $README..."
    if [[ -n "$CUSTOM_MESSAGE" ]]; then
        README_ENTRY="| **v${NEW_VERSION}** | ${CUSTOM_MESSAGE} |"
    else
        case "$BUMP_TYPE" in
            patch) README_ENTRY="| **v${NEW_VERSION}** | Patch release |" ;;
            minor) README_ENTRY="| **v${NEW_VERSION}** | Minor release |" ;;
            major) README_ENTRY="| **v${NEW_VERSION}** | Major release |" ;;
        esac
    fi
    ESCAPED_ENTRY=$(printf '%s\n' "$README_ENTRY" | sed 's/[\/&]/\\&/g')
    sedi "/^| Version | Highlights |/{
        n
        n
        i\\${ESCAPED_ENTRY}
    }" "$README"
    ok "$README → added $NEW_VERSION"
    FILES_TO_ADD+=("$README")
fi

# ── Commit ───────────────────────────────────────────────────────────────────
info "Committing..."
git add "${FILES_TO_ADD[@]}"
git add -u
git commit -m "$COMMIT_MSG"
ok "Committed: '$COMMIT_MSG'"

# ── Tag (annotated so hatch-vcs resolves a clean exact version) ──────────────
info "Creating annotated tag $NEW_TAG..."
git tag -a "$NEW_TAG" -m "Release $NEW_VERSION"
ok "Tag $NEW_TAG created"

# ── Push ─────────────────────────────────────────────────────────────────────
info "Pushing to $REMOTE/$BRANCH..."
git push "$REMOTE" "$BRANCH"
git push "$REMOTE" "$NEW_TAG"
ok "Pushed to $REMOTE/$BRANCH with tag $NEW_TAG"

# ── Done ─────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  Released ${PROJECT_NAME} ${NEW_VERSION}${NC}"
echo -e "${GREEN}  GitHub Actions will now build and publish to PyPI.${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  Monitor : ${CYAN}https://github.com/${GITHUB_REPO}/actions${NC}"
echo -e "  PyPI    : ${CYAN}https://pypi.org/project/${PYPI_PACKAGE}/${NEW_VERSION}/${NC}"
echo -e "  Install : ${CYAN}uv add ${PYPI_PACKAGE}@${NEW_VERSION}${NC}"
echo ""
