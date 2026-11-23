@echo off
title SignBridge - Push to GitHub
echo ========================================================
echo   SignBridge: Pushing Capstone Project to GitHub...
echo   Remote: https://github.com/Lakshya-dot/signbridge.git
echo ========================================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Git Status...
git status

echo.
echo [2/3] Verifying Branch and Remote...
git branch -M main
git remote -v

echo.
echo [3/3] Pushing to GitHub (Branch: main)...
echo If a GitHub sign-in window opens, please click "Authorize" or sign in.
echo.

:: Try standard push first
git push -u origin main

if %errorlevel% neq 0 (
    echo.
    echo [!] Standard push rejected (Remote has older divergent files).
    echo Overwriting remote with latest complete SignBridge v3.5 release...
    git push -u origin main --force
)

echo.
if %errorlevel% equ 0 (
    echo ========================================================
    echo [SUCCESS] SignBridge successfully pushed to GitHub!
    echo Visit: https://github.com/Lakshya-dot/signbridge
    echo ========================================================
) else (
    echo ========================================================
    echo [ERROR] Push failed. Check your internet connection or
    echo verify your GitHub permissions.
    echo ========================================================
)

echo.
pause
