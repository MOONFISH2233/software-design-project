@echo off
echo ========================================
echo 数据服务器 - 完整压力测试套件
echo ========================================
echo.

REM 检查服务器是否运行
echo [检查] 服务器状态...
curl -s http://localhost:5000/api/health >nul 2>&1
if errorlevel 1 (
    echo [警告] 服务器未运行，正在启动...
    start "数据服务器" cmd /k "python app.py"
    timeout /t 5 /nobreak >nul
)
echo [成功] 服务器运行正常
echo.

echo [测试 1/3] 普通模式测试...
echo ========================================
python jmeter_test.py --url http://localhost:5000 --duration 60 --users 10 --type normal
echo.
echo [完成] 普通模式测试完成
echo.

echo [测试 2/3] JWT 认证模式测试...
echo ========================================
python jmeter_test.py --url http://localhost:5000 --duration 60 --users 10 --username user1 --password user123 --type encrypted
echo.
echo [完成] JWT 认证模式测试完成
echo.

echo [测试 3/3] API Key 模式测试...
echo ========================================
python jmeter_test.py --url http://localhost:5000 --duration 60 --users 10 --apikey key_user1_001 --type apikey
echo.
echo [完成] API Key 模式测试完成
echo.

echo ========================================
echo 所有测试完成！
echo ========================================
echo.
echo 测试结果已保存到：stress_test_results.csv
echo.
echo 生成测试报告...
python generate_report.py
echo.
pause
