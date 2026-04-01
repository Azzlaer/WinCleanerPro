@echo off
title PvPGN Firewall Enterprise

:: -------------------------------------------------
:: Check for admin rights
:: -------------------------------------------------
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo Soliciting Administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:: -------------------------------------------------
:: Set working directory to script location
:: -------------------------------------------------
cd /d "%~dp0"

:: -------------------------------------------------
:: Run Python firewall
:: -------------------------------------------------
echo.
echo ==========================================
echo   PvPGN Firewall Enterprise - STARTING
echo ==========================================
echo.

python main.py

echo.
echo Firewall detenido.
pause
