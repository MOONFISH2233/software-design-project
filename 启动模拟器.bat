@echo off
chcp 65001 >nul
echo ========================================
echo   Data Generator Simulator - MQ Version
echo ========================================
echo.
echo Location: examples/simulator_mq.py
echo Function: Simulate sensor data and send to server via Redis
echo.
echo Starting simulator...
echo.

cd /d "%~dp0data-server"
python examples/simulator_mq.py

pause
