@echo off
chcp 65001 >nul
echo ========================================
echo   远程服务器部署脚本
echo ========================================
echo.
echo [信息] 正在连接到服务器并部署代码...
echo [提示] 请在提示时输入密码: @Dierzu999
echo.

REM 使用plink或直接SSH
ssh root@47.103.108.47 "cd /root/course-project && git fetch origin week5 && git merge origin/week5 && echo '部署成功！' && systemctl restart data-server"

echo.
echo ========================================
echo   部署完成！
echo ========================================
pause
