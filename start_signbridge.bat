@echo off
title SignBridge - ISL Recognition System
echo ========================================================
echo   Launching SignBridge Live Recognition System...
echo ========================================================
echo.

cd /d "%~dp0"

:: Try default python command first
where python >nul 2>nul
if %errorlevel% equ 0 (
    python run_signbridge.py
    goto end
)

:: Fallback to local user Python paths if needed
if exist "C:\Users\laksh\AppData\Local\Programs\Python\Python312\python.exe" (
    "C:\Users\laksh\AppData\Local\Programs\Python\Python312\python.exe" run_signbridge.py
    goto end
)

if exist "C:\Users\laksh\AppData\Local\Programs\Python\Python310\python.exe" (
    "C:\Users\laksh\AppData\Local\Programs\Python\Python310\python.exe" run_signbridge.py
    goto end
)

echo [ERROR] Python was not found on your system.
echo Please install Python 3.10 or 3.12 and add it to your PATH.
pause

:end
if %errorlevel% neq 0 (
    echo.
    echo Application exited with code %errorlevel%.
    pause
)
