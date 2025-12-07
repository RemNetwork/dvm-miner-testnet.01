@echo off
REM ============================================
REM DVM Miner - Windows Starter Script
REM ============================================

REM Change to the script's directory
cd /d "%~dp0"

echo.
echo ============================================
echo   DVM Miner - Clean Version
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install/upgrade dependencies
echo Installing/updating dependencies...
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Start the miner
echo.
echo Starting DVM Miner...
echo.
python entry_point.py start

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo Miner stopped with an error.
    pause
)

