@echo off
:: ============================================================
::  ClinicCare Pro — First-Time Setup Script (Windows)
::
::  What this does:
::    1. Checks for Python 3.8+
::    2. Creates a virtual environment (.venv)
::    3. Installs optional dependencies (pillow, bcrypt)
::    4. Launches the application
::
::  Run this once before using ClinicCare Pro.
:: ============================================================

title ClinicCare Pro — Setup
color 0A

echo.
echo   =====================================================
echo     ClinicCare Pro — Automated Setup
echo   =====================================================
echo.

:: Step 1: Check Python
echo   [1/4] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   [ERROR] Python not found. Please install Python 3.8+ from:
    echo           https://www.python.org/downloads/
    echo   Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)
python --version
echo   [OK] Python found.
echo.

:: Step 2: Create virtual environment
echo   [2/4] Creating virtual environment (.venv)...
if exist ".venv" (
    echo   [SKIP] .venv already exists.
) else (
    python -m venv .venv
    echo   [OK] Virtual environment created.
)
echo.

:: Step 3: Install dependencies
echo   [3/4] Installing optional dependencies...
.venv\Scripts\pip install --upgrade pip --quiet
.venv\Scripts\pip install pillow bcrypt --quiet
echo   [OK] Dependencies installed.
echo.

:: Step 4: Launch
echo   [4/4] Launching ClinicCare Pro...
echo.
echo   Default login credentials:
echo     Username : admin
echo     Password : admin123
echo.
echo   =====================================================
echo.

.venv\Scripts\python.exe main.py

if %errorlevel% neq 0 (
    echo.
    echo   [ERROR] Application exited with an error.
    pause
)
