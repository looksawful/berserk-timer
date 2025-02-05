@echo off
setlocal ENABLEDELAYEDEXPANSION

set SHORTCUTPATH="%userprofile%\Desktop\brsrk.url"
if exist "%userprofile%\Desktop" (
    del "%SHORTCUTPATH%"
    echo [InternetShortcut] >> "%SHORTCUTPATH%"
    echo URL="%CD%\brsrk.bat" >> "%SHORTCUTPATH%"
    echo IconFile="%CD%\src\assets\favicon.ico" >> "%SHORTCUTPATH%"
    echo IconIndex=0 >> "%SHORTCUTPATH%"
)

set SHORTCUTPATH="%userprofile%\Onedrive\Desktop\brsrk.url"
if exist "%userprofile%\Onedrive\Desktop" (
    del "%SHORTCUTPATH%"
    echo [InternetShortcut] >> "%SHORTCUTPATH%"
    echo URL="%CD%\brsrk.bat" >> "%SHORTCUTPATH%"
    echo IconFile="%CD%\src\assets\favicon.ico" >> "%SHORTCUTPATH%"
    echo IconIndex=0 >> "%SHORTCUTPATH%"
)
