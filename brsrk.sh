#!/bin/bash
# Berserk Timer launcher for Linux/MacOS
# Usage: ./brsrk.sh [duration] [flags]
# Example: ./brsrk.sh 5 -w

# Try to use venv Python first, fallback to global python3
if [ -f "venv/bin/python" ]; then
    ./venv/bin/python -m src.main 5 -w "$@"
else
    python3 -m src.main 5 -w "$@"
fi
