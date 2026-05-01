@echo off
title Business Blockchain - Encrypted Transaction Ledger
echo ============================================
echo   Business Blockchain - Encrypted Ledger
echo ============================================
echo.

REM Activate virtual environment and start CLI
call venv\Scripts\activate.bat
python cli.py %*

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo Press any key to exit...
    pause >nul
)
