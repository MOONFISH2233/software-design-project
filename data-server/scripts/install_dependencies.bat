@echo off
echo ========================================
echo 安装数据服务器依赖
echo ========================================
echo.

echo [1/2] 安装 Flask 和相关扩展...
pip install flask flask-httpauth flask-limiter -q
if errorlevel 1 (
    echo [错误] Flask 安装失败
    pause
    exit /b 1
)
echo [成功] Flask 安装完成
echo.

echo [2/2] 安装加密和安全库...
pip install cryptography PyJWT -q
if errorlevel 1 (
    echo [错误] 加密库安装失败
    pause
    exit /b 1
)
echo [成功] 加密库安装完成
echo.

echo ========================================
echo 所有依赖安装完成！
echo ========================================
echo.
echo 现在可以运行：python app.py
echo.
pause
