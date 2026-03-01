#!/usr/bin/env bash
# publish.sh — Bump version, update README, commit, tag, and push.
#
# Usage (run from anywhere inside the repo):
#   ./scripts/publish.sh              # patch bump  0.1.0 → 0.1.1  (default)
#   ./scripts/publish.sh --patch      # patch bump  0.1.0 → 0.1.1
#   ./scripts/publish.sh --minor      # minor bump  0.1.0 → 0.2.0
#   ./scripts/publish.sh --major      # major bump  0.1.0 → 1.0.0
#   ./scripts/publish.sh --message "feat: something"   # custom commit message
#   ./scripts/publish.sh --minor --message "feat: new provider"
#   ./scripts/publish.sh --dry-run    # preview changes without committing

set -euo pipefail

# ── Resolve repo root ────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

PYPROJECT="pyproject.toml"
README="README.md"
REMOTE="origin"
BRANCH="main"

# ── Colors ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

info()    { echo -e "${CYAN}[INFO]${NC}  $*"; }
ok()      { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
fail()    { echo -e "${RED}[FAIL]${NC}  $*" >&2; exit 1; }
preview() { echo -e "${YELLOW}[DRY]${NC}   $*"; }

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
[[ -f "$PYPROJECT" ]] || fail "$PYPROJECT not found. Cannot continue."
[[ -f "$README"    ]] || fail "$README not found. Cannot continue."

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
[[ "$CURRENT_BRANCH" == "$BRANCH" ]] \
    || fail "Not on '$BRANCH' branch (currently on '$CURRENT_BRANCH'). Switch first."

if [[ -n "$(git diff --cached --name-only)" ]]; then
    fail "Staged but uncommitted changes detected. Commit or unstage them first."
fi

if [[ -n "$(git diff --name-only HEAD)" ]]; then
    warn "Unstaged changes in tracked files — they will be committed with the version bump."
fi

# ── Read current version ─────────────────────────────────────────────────────
CURRENT_VERSION=$(grep '^version = ' "$PYPROJECT" | sed 's/version = "\(.*\)"/\1/')
[[ -n "$CURRENT_VERSION" ]] || fail "Could not read version from $PYPROJECT."

IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"

# ── Calculate new version ────────────────────────────────────────────────────
case "$BUMP_TYPE" in
    patch) NEW_VERSION="${MAJOR}.${MINOR}.$((PATCH + 1))" ;;
    minor) NEW_VERSION="${MAJOR}.$((MINOR + 1)).0" ;;
    major) NEW_VERSION="$((MAJOR + 1)).0.0" ;;
esac

NEW_TAG="v${NEW_VERSION}"

# ── Check tag doesn't already exist ─────────────────────────────────────────
if git rev-parse "$NEW_TAG" &>/dev/null; then
    fail "Tag $NEW_TAG already exists. Resolve manually or choose a different bump type."
fi

# ── Build commit message ─────────────────────────────────────────────────────
if [[ -n "$CUSTOM_MESSAGE" ]]; then
    COMMIT_MSG="$CUSTOM_MESSAGE"
else
    COMMIT_MSG="chore: release v${NEW_VERSION}"
fi

# ── Preview ──────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}  matrx-ai release${NC}"
echo -e "  ─────────────────────────────────────────────"
echo -e "  Bump type  : ${CYAN}${BUMP_TYPE}${NC}"
echo -e "  Old version: ${YELLOW}${CURRENT_VERSION}${NC}"
echo -e "  New version: ${GREEN}${NEW_VERSION}${NC}"
echo -e "  Tag        : ${GREEN}${NEW_TAG}${NC}"
echo -e "  Commit msg : ${CYAN}${COMMIT_MSG}${NC}"
$DRY_RUN && echo -e "  Mode       : ${YELLOW}DRY RUN — nothing will be changed${NC}"
echo -e "  ─────────────────────────────────────────────"
echo ""

if $DRY_RUN; then
    preview "Would update version in $PYPROJECT:  $CURRENT_VERSION → $NEW_VERSION"
    preview "Would prepend entry in $README version history table"
    preview "Would commit: '$COMMIT_MSG'"
    preview "Would create tag: $NEW_TAG"
    preview "Would push: git push $REMOTE $BRANCH --tags"
    echo ""
    preview "Dry run complete. No changes made."
    echo ""
    exit 0
fi

# ── Update pyproject.toml ────────────────────────────────────────────────────
info "Bumping version in $PYPROJECT..."
sed -i "s/^version = \"${CURRENT_VERSION}\"/version = \"${NEW_VERSION}\"/" "$PYPROJECT"

WRITTEN_VERSION=$(grep '^version = ' "$PYPROJECT" | sed 's/version = "\(.*\)"/\1/')
[[ "$WRITTEN_VERSION" == "$NEW_VERSION" ]] \
    || fail "Version write failed — $PYPROJECT still shows $WRITTEN_VERSION."
ok "pyproject.toml → $NEW_VERSION"

# ── Update README version history table ──────────────────────────────────────
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

# Insert the new row immediately after the "| Version | Highlights |" header row.
ESCAPED_ENTRY=$(printf '%s\n' "$README_ENTRY" | sed 's/[\/&]/\\&/g')
sed -i "/^| Version | Highlights |/{
    n        # skip the separator row
    n        # now on the first data row
    i\\${ESCAPED_ENTRY}
}" "$README"

ok "README.md → added $NEW_VERSION to version history"

# ── Commit ───────────────────────────────────────────────────────────────────
info "Staging changed files..."
git add "$PYPROJECT" "$README"
git add -u

info "Committing..."
git commit -m "$COMMIT_MSG"
ok "Committed: '$COMMIT_MSG'"

# ── Tag ──────────────────────────────────────────────────────────────────────
info "Creating tag $NEW_TAG..."
git tag "$NEW_TAG"
ok "Tag $NEW_TAG created"

# ── Push ─────────────────────────────────────────────────────────────────────
info "Pushing commits and tag to $REMOTE/$BRANCH..."
git push "$REMOTE" "$BRANCH" --tags
ok "Pushed to $REMOTE/$BRANCH with tag $NEW_TAG"

# ── Done ─────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  Released matrx-ai ${NEW_VERSION}${NC}"
echo -e "${GREEN}  GitHub Actions will now build and publish to PyPI.${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  Monitor : ${CYAN}https://github.com/armanisadeghi/matrx-ai/actions${NC}"
echo -e "  PyPI    : ${CYAN}https://pypi.org/project/matrx-ai/${NEW_VERSION}/${NC}"
echo -e "  Install : ${CYAN}uv add matrx-ai@${NEW_VERSION}${NC}"
echo ""
