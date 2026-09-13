@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "BERSERK_TARGET=%SCRIPT_DIR%brsrk.bat"
set "BERSERK_WORKDIR=%SCRIPT_DIR%"
set "BERSERK_ICON=%SCRIPT_DIR%assets\icon.ico"

call :CREATE_SHORTCUT "%USERPROFILE%\Desktop"
if defined OneDrive call :CREATE_SHORTCUT "%OneDrive%\Desktop"
exit /b 0

:CREATE_SHORTCUT
set "DESKTOP_DIR=%~1"
if not exist "%DESKTOP_DIR%" exit /b 0

set "BERSERK_SHORTCUT=%DESKTOP_DIR%\Berserk Timer.lnk"
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ws = New-Object -ComObject WScript.Shell; " ^
  "$shortcut = $ws.CreateShortcut($env:BERSERK_SHORTCUT); " ^
  "$shortcut.TargetPath = $env:BERSERK_TARGET; " ^
  "$shortcut.WorkingDirectory = $env:BERSERK_WORKDIR; " ^
  "$shortcut.IconLocation = $env:BERSERK_ICON + ',0'; " ^
  "$shortcut.Save()"

exit /b %ERRORLEVEL%
