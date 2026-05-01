@echo off
title Business Blockchain - Quick Start
:menu
cls
echo ============================================
echo   Business Blockchain - Quick Start Menu
echo ============================================
echo.
echo Select an option:
echo.
echo   1. Initialize new blockchain (first time only)
echo   2. Add a transaction
echo   3. View all transactions
echo   4. Check blockchain status
echo   5. Verify chain integrity
echo   6. Export transactions to file
echo   7. Exit
echo.
set /p choice="Enter choice (1-7): "

call venv\Scripts\activate.bat

if "%choice%"=="1" goto init
if "%choice%"=="2" goto add
if "%choice%"=="3" goto view
if "%choice%"=="4" goto status
if "%choice%"=="5" goto verify
if "%choice%"=="6" goto export
if "%choice%"=="7" goto end

echo Invalid choice.
pause
goto menu

:init
cls
echo.
echo === Initialize New Blockchain ===
echo WARNING: Store your master password securely!
echo          Without it, your data is permanently lost.
echo.
python cli.py init
if errorlevel 1 (
    echo.
    echo Initialization failed or blockchain already exists.
) else (
    echo.
    echo SUCCESS! Your blockchain is ready.
    echo Remember your master password!
)
echo.
pause
goto menu

:add
cls
echo.
echo === Add Transaction ===
python cli.py add
echo.
pause
goto menu

:view
cls
echo.
echo === View Transactions ===
echo Enter your master password to decrypt and view transactions.
echo.
python cli.py view --decrypt
echo.
pause
goto menu

:status
cls
echo.
echo === Blockchain Status ===
python cli.py status
echo.
pause
goto menu

:verify
cls
echo.
echo === Verify Chain Integrity ===
python cli.py verify
echo.
pause
goto menu

:export
cls
echo.
echo === Export Transactions ===
set /p filename="Enter filename (or press Enter for default): "
if "%filename%"=="" (
    python cli.py export
) else (
    python cli.py export -o %filename%
)
echo.
pause
goto menu

:end
cls
echo.
echo Thank you for using Business Blockchain!
echo.
timeout /t 2
exit
