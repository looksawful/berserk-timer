#!/bin/bash
python3 setup.py

python3 -m src.main 25 -w "$@"