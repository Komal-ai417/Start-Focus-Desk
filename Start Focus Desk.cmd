@echo off
setlocal
title Focus Desk
cd /d "%~dp0"
set "YOLO_CONFIG_DIR=%CD%\.yolo"

if not exist ".venv\Scripts\python.exe" (
    py -3 -m venv .venv
    if errorlevel 1 goto failed
)
if not exist ".venv\setup.done" (
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto failed
    type nul > ".venv\setup.done"
)
".venv\Scripts\python.exe" app.py %*
if errorlevel 1 goto failed
exit /b 0

:failed
echo.
echo Focus Desk could not start. See the error above.
pause
exit /b 1
