# syntax=docker/dockerfile:1.7
#
# Multi-stage build for matrx-ai.
#
# Why split into builder/runtime:
#   - Build deps (build-essential, libpq-dev, git) are only needed to compile
#     wheels and run hatch-vcs. Keeping them out of the runtime image saves
#     ~300 MB and reduces the attack surface.
#
# Why split `uv sync` into two passes:
#   - `[tool.hatch.version]` is `source = "vcs"`, so installing matrx-ai
#     itself requires a git working tree. We sync deps first with
#     `--no-install-project` (cheap, cacheable, no source needed), then COPY
#     the full source + .git, then install the project on top. This avoids
#     the historical hatchling.build.build_editable failure that was caused
#     by uv trying to install matrx-ai before .git was in the image.

ARG PYTHON_BASE=python:3.13-slim

# -----------------------------------------------------------------------------
# Stage 1: builder
# -----------------------------------------------------------------------------
FROM ${PYTHON_BASE} AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    rm -f /etc/apt/apt.conf.d/docker-clean \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        git \
        curl

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir uv

WORKDIR /app

# Pass 1: install dependencies only (no source needed). Cached unless
# pyproject.toml or uv.lock changes.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --extra server --no-install-project

# Pass 2: install matrx-ai itself. Needs the full source + .git so
# hatch-vcs can resolve the version.
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --extra server

# -----------------------------------------------------------------------------
# Stage 2: runtime
# -----------------------------------------------------------------------------
FROM ${PYTHON_BASE} AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PROJECT_DIR=/app \
    PATH="/app/.venv/bin:$PATH"

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    rm -f /etc/apt/apt.conf.d/docker-clean \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5 \
        curl \
        ca-certificates

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app /app

RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -fsS http://localhost:8000/api/health >/dev/null || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
