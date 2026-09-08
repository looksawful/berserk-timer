@echo off
setlocal
pushd "%~dp0"

REM Berserk Timer launcher for Windows
REM Usage: brsrk.bat [duration] [flags]
REM Example: brsrk.bat 5 -w

if exist "%~dp0venv\Scripts\python.exe" (
    "%~dp0venv\Scripts\python.exe" -m src.main %*
) else (
    where py >nul 2>nul
    if not errorlevel 1 (
        py -3 -m src.main %*
    ) else (
        python -m src.main %*
    )
)

set "EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %EXIT_CODE%
