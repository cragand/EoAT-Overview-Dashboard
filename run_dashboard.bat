@echo off
title EOAT Overview Dashboard
cd /d "%~dp0"

:: Check for Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Please install Python 3.7+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Create venv if it doesn't exist
if not exist "venv\Scripts\activate.bat" (
    echo Setting up virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

echo.
echo ========================================
echo   EOAT Overview Dashboard
echo ========================================
echo.
echo Starting server...
echo Open http://localhost:5000 in your browser
echo Press Ctrl+C to stop
echo.

python app.py
pause
