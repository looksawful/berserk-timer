@echo off
REM Berserk Timer launcher for Windows
REM Usage: brsrk.bat [duration] [flags]
REM Example: brsrk.bat 25 -w

python -m src.main 25 -w %*
pause


