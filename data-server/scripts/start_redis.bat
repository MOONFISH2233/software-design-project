@echo off
REM ====================================
REM 启动 Redis (Docker 方式)
REM ====================================

echo.
echo ======================================================================
echo                      启动 Redis 服务 (Docker)
echo ======================================================================
echo.

REM 检查 Docker 是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Docker
    echo.
    echo 请先安装 Docker Desktop:
    echo https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)

echo 正在检查 Redis 容器...
docker ps | findstr redis >nul 2>&1
if not errorlevel 1 (
    echo Redis 已经在运行中
    echo.
    docker ps | findstr redis
    echo.
    echo 是否需要重启？(Y/N)
    set /p choice=
    if /i not "%choice%"=="Y" exit /b 0
)

echo 正在启动 Redis 容器...
docker run -d -p 6379:6379 --name redis-server redis:latest

if errorlevel 1 (
    echo.
    echo [错误] Redis 启动失败
    echo 可能原因：
    echo   1. Docker 未启动
    echo   2. 端口 6379 已被占用
    echo.
    pause
    exit /b 1
)

echo.
echo Redis 启动成功！
echo.
echo 验证连接：redis-cli ping
echo 应返回：PONG
echo.
echo 停止命令：docker stop redis-server
echo 删除命令：docker rm redis-server
echo.
timeout /t 2 /nobreak >nul
redis-cli ping

echo.
pause
