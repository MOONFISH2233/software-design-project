@echo off
REM ====================================
REM 清理测试数据
REM ====================================

echo.
echo ======================================================================
echo                         清理测试数据
echo ======================================================================
echo.
echo 警告：此操作将删除所有测试数据！
echo.
echo 将要删除:
echo   - Redis 中的所有数据
echo   - logs\*.log 日志文件
echo   - data\*\*.json 数据文件
echo.
echo 是否继续？(Y/N)
set /p choice=
if /i not "%choice%"=="Y" exit /b 0

echo.
echo [1/3] 清空 Redis...
redis-cli FLUSHDB >nul 2>&1
if errorlevel 1 (
    echo      Redis 连接失败，跳过
) else (
    echo      ✅ Redis 已清空
)
echo.

echo [2/3] 删除日志文件...
del /q logs\*.log 2>nul
echo      ✅ 日志文件已删除
echo.

echo [3/3] 删除数据文件...
del /q data\skin_sensor\*.json 2>nul
del /q data\environment\*.json 2>nul
del /q data\device\*.json 2>nul
echo      ✅ 数据文件已删除
echo.

echo ======================================================================
echo 清理完成
echo ======================================================================
echo.
pause

