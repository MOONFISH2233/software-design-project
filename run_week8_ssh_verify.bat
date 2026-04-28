@echo off
chcp 65001 >nul
REM ============================================
REM 第八周验收 - SSH实时验证（Windows版）
REM ============================================

echo.
echo ========================================
echo   第八周任务验收 - SSH实时验证
echo   皮肤健康监测系统
echo ========================================
echo.
echo [说明] 此脚本将SSH连接到服务器并执行验证
echo        需要输入密码: @Dierzu999
echo.
pause

echo.
echo [正在连接服务器...]
ssh root@47.103.108.47 "bash -s" < data-server\scripts\verify_week8.sh

echo.
echo ========================================
echo   验证完成！
echo ========================================
echo.
echo 提示：如果看到乱码，请在PowerShell中运行以下命令：
echo   chcp 65001
echo   ssh root@47.103.108.47 "bash -s" ^< data-server\scripts\verify_week8.sh
echo.
pause