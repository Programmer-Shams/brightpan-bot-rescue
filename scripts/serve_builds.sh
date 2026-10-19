#!/usr/bin/env bash
# Serve both builds for the chat page and the eval:
#   broken  (tag broken, checked out in .worktrees/broken)  http://127.0.0.1:8003/chat
#   current (this working tree)                             http://127.0.0.1:8004/chat
# Ctrl+C stops both.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="$ROOT/.venv/bin"
WT="$ROOT/.worktrees/broken"

[ -d "$WT" ] || git -C "$ROOT" worktree add --detach "$WT" broken
ln -sf "$ROOT/.env" "$WT/.env"
# The broken build has no automatic re-ingest: build its (v1) index once.
[ -d "$WT/chroma" ] || (cd "$WT" && "$PY/python" bot/ingest.py)

trap 'kill 0' EXIT INT TERM
(cd "$WT" && exec "$PY/uvicorn" bot.app:app --host 127.0.0.1 --port 8003) &
(cd "$ROOT" && exec "$PY/uvicorn" bot.app:app --host 127.0.0.1 --port 8004) &
wait
