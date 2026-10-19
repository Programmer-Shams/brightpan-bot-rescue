#!/usr/bin/env bash
# Serve both builds for the chat page and the eval:
#   broken  (tag broken, checked out in .worktrees/broken)  http://127.0.0.1:8003/chat
#   current (this working tree)                             http://127.0.0.1:8004/chat
# Ctrl+C stops both; if either server exits, the other is stopped too.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="$ROOT/.venv/bin"
WT="$ROOT/.worktrees/broken"

[ -d "$WT" ] || git -C "$ROOT" worktree add --detach "$WT" broken
ln -sf "$ROOT/.env" "$WT/.env"
# The broken build has no automatic re-ingest: build its (v1) index once. The marker is written only after
# a successful ingest, so a failed first attempt is retried on the next start.
if [ ! -f "$WT/chroma/.built" ]; then
  rm -rf "$WT/chroma"
  (cd "$WT" && "$PY/python" bot/ingest.py)
  touch "$WT/chroma/.built"
fi

trap 'kill 0' EXIT INT TERM
(cd "$WT" && exec "$PY/uvicorn" bot.app:app --host 127.0.0.1 --port 8003) &
broken=$!
(cd "$ROOT" && exec "$PY/uvicorn" bot.app:app --host 127.0.0.1 --port 8004) &
current=$!
# macOS ships bash 3.2 (no `wait -n`), so poll until either server exits.
while kill -0 "$broken" 2>/dev/null && kill -0 "$current" 2>/dev/null; do sleep 2; done
echo "A server stopped; shutting down both." >&2
