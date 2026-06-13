@echo off
:: ============================================================
::  ClinicCare Pro — One-Click Launcher (Windows)
::  Run this file to start the application.
:: ============================================================

title ClinicCare Pro
color 0B

echo.
echo   =====================================================
echo     ClinicCare Pro — Smarter Health Connection
echo   =====================================================
echo.

:: Try virtual environment first (preferred)
if exist ".venv\Scripts\python.exe" (
    echo   [INFO] Using virtual environment (.venv)
    ".venv\Scripts\python.exe" main.py
    goto :done
)

if exist "venv\Scripts\python.exe" (
    echo   [INFO] Using virtual environment (venv)
    "venv\Scripts\python.exe" main.py
    goto :done
)

:: Fall back to system Python
echo   [INFO] Using system Python
python main.py

:done
if %errorlevel% neq 0 (
    echo.
    echo   [ERROR] The application exited with an error.
    echo   Run setup.bat first if this is your first time.
    echo.
    pause
)
