@echo off
chcp 65001 >nul
REM ============================================
REM 第八周验收演示 - 一键启动脚本
REM ============================================

echo.
echo ========================================
echo   第八周任务验收演示系统
echo   皮肤健康监测系统
echo ========================================
echo.

REM 检查Python环境
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 未找到Python，请先安装Python 3.6+
    pause
    exit /b 1
)

echo [1/3] 启动HTML验收演示页面...
start docs\WEEK8_ACCEPTANCE_DEMO.html
timeout /t 2 >nul

echo [2/3] 运行Python自动化验证脚本...
python data-server\tests\week8_acceptance_demo.py --remote

echo.
echo [3/3] 验证完成！
echo.
echo ========================================
echo   验收材料清单：
echo ========================================
echo.
echo   1. HTML演示页面 (docs\WEEK8_ACCEPTANCE_DEMO.html)
echo   2. Python验证脚本 (data-server\tests\week8_acceptance_demo.py)
echo   3. 数据库设计文档 (docs\DATABASE_DESIGN_COMPLETE_GUIDE.md)
echo   4. 小程序功能规划 (docs\WEEK8_MINIPROGRAM_PLAN.md)
echo   5. PowerDesigner模型 (docs\powerdesigner_models\)
echo   6. SQL建表脚本 (data-server\scripts\init_mysql_week8.sql)
echo   7. 定时任务代码 (data-server\tasks\daily_statistics.py)
echo   8. Flask接口代码 (data-server\routes\mysql_routes.py)
echo.
echo ========================================
echo   演示流程建议 (5-8分钟)：
echo ========================================
echo.
echo   1. 打开HTML演示页面 - 展示思维导图和任务概览 (1分钟)
echo   2. 点击"验证数据库"按钮 - 展示15个表已创建 (1分钟)
echo   3. 点击"执行定时任务" - 展示数据统计流程 (1分钟)
echo   4. 点击"测试Flask接口" - 展示CRUD操作 (1分钟)
echo   5. 点击"实时监控" - 展示数据上传过程 (1分钟)
echo   6. 总结演示 - 展示验收报告 (1分钟)
echo.
echo ========================================
pause