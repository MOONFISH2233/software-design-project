@echo off
chcp 65001 >nul
echo ========================================
echo   React前端项目 - 一键安装和启动
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] 检查Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到Node.js，请先安装Node.js
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)
echo ✅ Node.js已安装

echo.
echo [2/3] 安装依赖包（这可能需要几分钟）...
call npm install
if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)
echo ✅ 依赖安装完成

echo.
echo [3/3] 启动开发服务器...
echo.
echo 🚀 正在启动Vite开发服务器...
echo 📱 访问地址: http://localhost:3000
echo.
start "" "http://localhost:3000"
npm run dev

pause
