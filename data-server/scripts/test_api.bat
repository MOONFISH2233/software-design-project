@echo off
REM ====================================
REM API 自动化测试脚本
REM ====================================

echo.
echo ======================================================================
echo                    Flask API 自动化测试
echo ======================================================================
echo.

REM 检查参数
set SERVER_URL=%1
if "%SERVER_URL%"=="" (
    set SERVER_URL=http://localhost:5000
)

echo 服务器地址：%SERVER_URL%
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python
    pause
    exit /b 1
)

REM 检查 requests 库是否安装
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo [错误] 未安装 requests 库
    echo 请运行：pip install requests
    pause
    exit /b 1
)

echo 正在运行测试...
echo.

REM 执行测试
cd /d %~dp0
python api_auto_test.py %SERVER_URL%

echo.
echo ======================================================================
echo 测试完成
echo ======================================================================
echo.
echo 测试报告已保存到当前目录
echo.
pause
