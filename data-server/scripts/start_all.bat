@echo off
REM ====================================
REM Windows 一键启动脚本（批处理版本）
REM ====================================

echo.
echo ======================================================================
echo                      MQ 数据服务器系统启动
echo ======================================================================
echo.
echo 启动时间: %date% %time%
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python
    pause
    exit /b 1
)

echo [1/5] 检查 Python 环境... OK
echo.

REM 检查 Redis 连接
echo [2/5] 检查 Redis 连接...
redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo [警告] Redis 未启动或无法连接
    echo.
    echo 请手动启动 Redis:
    echo   Docker: docker run -d -p 6379:6379 redis:latest
    echo   或者：redis-server
    echo.
    echo 是否继续？(Y/N)
    set /p choice=
    if /i not "%choice%"=="Y" exit /b 1
) else (
    echo      Redis 连接成功
)
echo.

REM 启动各个模块
echo [3/5] 启动数据接收模块...
start "数据接收模块" cmd /k "cd /d %~dp0 && python module_receiver.py"
timeout /t 1 /nobreak >nul

echo [4/5] 启动数据验证模块...
start "数据验证模块" cmd /k "cd /d %~dp0 && python module_validator.py"
timeout /t 1 /nobreak >nul

echo [5/5] 启动数据写入模块...
start "数据写入模块" cmd /k "cd /d %~dp0 && python module_writer.py"
timeout /t 1 /nobreak >nul

echo.
echo 正在启动模拟器客户端...
timeout /t 2 /nobreak >nul
start "模拟器客户端" cmd /k "cd /d %~dp0 && python simulator_mq.py"

echo.
echo ======================================================================
echo                         系统启动完成
echo ======================================================================
echo.
echo 已启动的窗口:
echo   - 数据接收模块
echo   - 数据验证模块
echo   - 数据写入模块
echo   - 模拟器客户端
echo.
echo 提示:
echo   - 可以直接关闭各个窗口来停止对应模块
echo   - 查看日志：logs\*.log
echo   - 查看数据：data\*\*.json
echo   - 监控 MQ: redis-cli
echo.
pause
