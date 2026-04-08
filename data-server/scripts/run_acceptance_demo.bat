@echo off
chcp 65001 >nul
echo ==========================================
echo 第五周任务验收演示 - 一键执行
echo ==========================================
echo.

echo [步骤 1/3] 检查服务器状态...
curl -s http://localhost:5000/api/health >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 服务器未运行！
    echo.
    echo 请先启动服务器：
    echo   python app.py
    echo.
    pause
    exit /b 1
)
echo ✅ 服务器运行正常
echo.

echo [步骤 2/3] 运行验收测试...
echo.
python acceptance_demo.py --url http://localhost:5000
echo.

echo [步骤 3/3] 生成验收报告...
echo.
if exist "acceptance_test_report.json" (
    echo ✅ 验收报告已生成
    echo.
    echo 查看报告：
    echo   acceptance_test_report.json
) else (
    echo ⚠️  未生成验收报告
)

echo.
echo ==========================================
echo 演示完成！
echo ==========================================
echo.
pause
