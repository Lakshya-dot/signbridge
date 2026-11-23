@echo off
title SignBridge - Interactive Web AI Studio
echo ========================================================
echo   Launching SignBridge Interactive Web Studio...
echo   Opening http://127.0.0.1:5000 in your browser...
echo ========================================================
echo.

cd /d "%~dp0"

:: Try default python command first
where python >nul 2>nul
if %errorlevel% equ 0 (
    python run_web_dashboard.py
    goto end
)

:: Fallback to local user Python paths
if exist "C:\Users\laksh\AppData\Local\Programs\Python\Python310\python.exe" (
    "C:\Users\laksh\AppData\Local\Programs\Python\Python310\python.exe" run_web_dashboard.py
    goto end
)

if exist "C:\Users\laksh\AppData\Local\Programs\Python\Python312\python.exe" (
    "C:\Users\laksh\AppData\Local\Programs\Python\Python312\python.exe" run_web_dashboard.py
    goto end
)

echo [ERROR] Python was not found on your system.
pause

:end
if %errorlevel% neq 0 (
    echo.
    echo Application exited with code %errorlevel%.
    pause
)
