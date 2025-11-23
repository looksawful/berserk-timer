#!/bin/bash
# Berserk Timer launcher for Linux/MacOS
# Usage: ./brsrk.sh [duration] [flags]
# Example: ./brsrk.sh 25 -w

python3 -m src.main 25 -w "$@"