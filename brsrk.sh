#!/bin/sh
# Berserk Timer launcher for Linux/macOS
# Usage: ./brsrk.sh [duration] [flags]
# Example: ./brsrk.sh 5 -w

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR" || exit 1

if [ -x "$SCRIPT_DIR/venv/bin/python" ]; then
    exec "$SCRIPT_DIR/venv/bin/python" -m src.main "$@"
fi

exec python3 -m src.main "$@"
