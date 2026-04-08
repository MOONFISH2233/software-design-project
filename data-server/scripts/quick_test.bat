@echo off
echo ========================================
echo 数据服务器压力测试 - 快速测试
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo [检查] Python 已安装
echo.

REM 安装依赖
echo [1/4] 安装依赖包...
pip install requests flask flask-httpauth flask-limiter cryptography PyJWT -q
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)
echo [成功] 依赖安装完成
echo.

REM 启动服务器
echo [2/4] 启动数据服务器...
start "数据服务器" cmd /k "python app.py"
echo [提示] 服务器启动中...
timeout /t 5 /nobreak >nul
echo.

REM 运行测试
echo [3/4] 运行压力测试（普通模式）...
python jmeter_test.py --url http://localhost:5000 --duration 30 --users 5 --type normal
echo.

echo [4/4] 运行压力测试（JWT 认证模式）...
python jmeter_test.py --url http://localhost:5000 --duration 30 --users 5 --username user1 --password user123 --type encrypted
echo.

echo ========================================
echo 测试完成！
echo ========================================
echo.
echo 查看测试结果：stress_test_results.csv
echo.
pause
