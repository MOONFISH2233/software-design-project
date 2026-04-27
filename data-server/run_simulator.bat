@echo off
chcp 65001 >nul
echo ========================================
echo   System Verification Tool
echo ========================================
echo.

echo [1/5] Checking Python environment...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)
echo OK
echo.

echo [2/5] Checking project directory...
cd /d "%~dp0data-server"
if not exist "mq_utils.py" (
    echo ERROR: mq_utils.py not found!
    pause
    exit /b 1
)
echo OK - Current directory: %CD%
echo.

echo [3/5] Checking required modules...
python -c "import redis; import json; import threading" 2>nul
if errorlevel 1 (
    echo WARNING: Some modules may be missing
    echo Please run: pip install redis
) else (
    echo OK - All modules available
)
echo.

echo [4/5] Checking Redis connection...
python -c "import redis; r = redis.Redis(host='localhost', port=6379, db=0); r.ping(); print('Redis connected')" 2>nul
if errorlevel 1 (
    echo WARNING: Cannot connect to Redis
    echo Please start Redis server first
) else (
    echo OK - Redis is running
)
echo.

echo [5/5] Checking simulator file...
if exist "examples\simulator_mq.py" (
    echo OK - Simulator found
) else (
    echo ERROR: examples\simulator_mq.py not found!
    pause
    exit /b 1
)
echo.

echo ========================================
echo   All checks passed!
echo ========================================
echo.
echo Ready to run simulator?
echo Press any key to start, or Ctrl+C to cancel...
pause >nul

echo.
echo Starting simulator...
echo.
python examples/simulator_mq.py
