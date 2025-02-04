@echo off
REM brsk.bat: Launch Berserk Timer with default settings:
REM  - Duration: 10 minutes
REM  - Witness mode enabled (-w)
REM  - Run in CLI (without -g flag)

python -m src.main 0.1 -w
