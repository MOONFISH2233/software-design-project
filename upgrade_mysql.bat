@echo off
chcp 65001 >nul
echo ==========================================
echo MySQL 8.0 升级工具
echo ==========================================
echo.
echo 当前MySQL版本检查中...
ssh root@47.103.108.47 "mysql --version"
echo.
echo ==========================================
echo 宝塔面板登录信息:
echo ==========================================
echo 地址: https://47.103.108.47:8888/90a1c9ff
echo 用户名: f151c119
echo 密码: 196f5df06612
echo.
echo ==========================================
echo MySQL升级步骤 (通过宝塔面板):
echo ==========================================
echo.
echo 1. 在浏览器中打开: https://47.103.108.47:8888/90a1c9ff
echo 2. 使用上面的用户名和密码登录
echo 3. 左侧菜单 -^> 数据库 -^> MySQL管理
echo 4. 找到 MySQL 5.7 -^> 点击"设置"
echo 5. 选择"切换版本" -^> 选择 MySQL 8.0.x
echo 6. 确认升级,等待10-20分钟完成
echo.
echo ==========================================
echo 是否打开浏览器访问宝塔面板? (Y/N)
echo ==========================================
set /p choice="请输入选择: "

if /i "%choice%"=="Y" (
    echo 正在打开浏览器...
    start https://47.103.108.47:8888/90a1c9ff
    echo.
    echo 请在宝塔面板中按照上述步骤升级MySQL
    echo 升级完成后,按任意键验证版本...
    pause >nul
    echo.
    echo 验证MySQL版本:
    ssh root@47.103.108.47 "mysql --version"
) else (
    echo.
    echo 你可以稍后手动访问宝塔面板进行升级
)

echo.
echo ==========================================
echo 升级注意事项:
echo ==========================================
echo - 升级前已自动备份数据到 /root/mysql_backup/
echo - 升级期间MySQL服务会重启,应用会短暂不可用
echo - 升级后请测试应用兼容性
echo - 如有问题可查看日志: /www/server/data/*.err
echo.
pause
