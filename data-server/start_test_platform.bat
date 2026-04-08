@echo off
chcp 65001 >nul
echo ========================================
echo   数据服务器 - 前端测试平台启动器
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python
    pause
    exit /b 1
)

echo [信息] 正在启动数据服务器...
echo [信息] 服务器地址: http://localhost:5000
echo [信息] 测试页面: http://localhost:5000/test
echo.
echo [提示] 按 Ctrl+C 可停止服务器
echo ========================================
echo.

REM 启动Flask应用
cd /d "%~dp0"
python app.py

pause
