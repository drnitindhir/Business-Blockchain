@echo off
echo ============================================
echo   Business Blockchain - First Time Setup
echo ============================================
echo.
echo This will set up the blockchain system on your PC.
echo.
pause

echo [1/3] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment.
    echo Make sure Python 3.8+ is installed.
    pause
    exit /b 1
)

echo [2/3] Installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo [3/3] Running tests...
python test_blockchain.py
if errorlevel 1 (
    echo WARNING: Some tests failed, but you can still use the app.
    echo Please check the output above for details.
) else (
    echo.
    echo All tests passed!
)

echo.
echo ============================================
echo   Setup Complete!
echo ============================================
echo.
echo To use the blockchain:
echo   1. Double-click run.bat to start
echo   2. Use 'init' command to create your first blockchain
echo   3. Store your master password in a safe place!
echo.
echo For quick start, type: run.bat init
echo.
pause
