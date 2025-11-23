@echo off
REM Berserk Timer launcher for Windows
REM Usage: brsrk.bat [duration] [flags]
REM Example: brsrk.bat 25 -w

REM Try to use venv Python first, fallback to global Python
if exist "%~dp0venv\Scripts\python.exe" (
    "%~dp0venv\Scripts\python.exe" -m src.main 25 -w %*
) else (
    "C:\Program Files\Python312\python.exe" -m src.main 25 -w %*
)
pause


