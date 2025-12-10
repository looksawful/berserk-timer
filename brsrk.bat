@echo off
REM Berserk Timer launcher for Windows
REM Usage: brsrk.bat [duration] [flags]
REM Example: brsrk.bat 5 -w

REM Try to use venv Python first, fallback to global Python
if exist "%~dp0venv\Scripts\python.exe" (
    "%~dp0venv\Scripts\python.exe" -m src.main -w %*
) else (
    "C:\Program Files\Python312\python.exe" -m src.main -w %*
)
pause


