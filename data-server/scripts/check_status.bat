@echo off
REM ====================================
REM 查看系统状态
REM ====================================

echo.
echo ======================================================================
echo                         系统状态检查
echo ======================================================================
echo.

REM 检查 Python
echo [1/6] 检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo      ❌ Python 未安装
) else (
    python --version
    echo      ✅ Python 已安装
)
echo.

REM 检查 Redis
echo [2/6] 检查 Redis 连接...
redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo      ❌ Redis 未连接
) else (
    echo      ✅ Redis 已连接
    redis-cli INFO server | findstr redis_version
)
echo.

REM 检查 Redis Stream
echo [3/6] 检查 MQ 流状态...
redis-cli XLEN sensor:raw
redis-cli XLEN sensor:validated
redis-cli XLEN sensor:write
echo.

REM 检查消费者组
echo [4/6] 检查消费者组...
redis-cli XINFO GROUPS sensor:raw 2>nul
echo.

REM 检查日志文件
echo [5/6] 检查日志文件...
dir /b logs\*.log 2>nul
if errorlevel 1 (
    echo      暂无日志文件
)
echo.

REM 检查数据文件
echo [6/6] 检查数据文件...
echo 皮肤传感器：
dir /b data\skin_sensor\*.json 2>nul | find /c ".json"
echo 环境传感器：
dir /b data\environment\*.json 2>nul | find /c ".json"
echo 设备状态：
dir /b data\device\*.json 2>nul | find /c ".json"
echo.

echo ======================================================================
echo 状态检查完成
echo ======================================================================
echo.
pause
