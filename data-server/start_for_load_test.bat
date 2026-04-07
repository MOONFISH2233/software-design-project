@echo off
chcp 65001 >nul
echo.
echo ============================================================
echo   压力测试模式 - 启动服务器
echo ============================================================
echo.
echo 此模式将放宽请求限流，允许高并发压力测试
echo.

REM 设置环境变量禁用严格的限流
set RATE_LIMIT_ENABLED=false

echo 启动服务器（压力测试模式）...
echo.

python app.py

pause
