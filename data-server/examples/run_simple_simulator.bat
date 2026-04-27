@echo off
chcp 65001 >nul
echo ========================================
echo   Simple Data Simulator (HTTP Mode)
echo ========================================
echo.
echo This simulator sends data directly to server via HTTP
echo No Redis required!
echo.
echo Press Ctrl+C to stop
echo.

cd /d "%~dp0.."
python examples/simple_simulator.py

echo.
echo Simulator stopped.
pause
