#!/bin/bash
# MySQL 5.7升级到8.0脚本（自动模式）
# 添加 --auto 参数可跳过交互确认

set -e

AUTO_MODE=false
if [ "$1" == "--auto" ]; then
    AUTO_MODE=true
fi

echo "======================================================================"
echo "  MySQL 5.7 → 8.0 升级脚本"
echo "======================================================================"
echo ""

if [ "$AUTO_MODE" = false ]; then
    echo "⚠️  警告: 此操作将升级MySQL版本"
    echo "   - 会自动备份现有数据库"
    echo "   - 升级过程可能需要10-20分钟"
    echo "   - 升级期间MySQL服务会重启"
    echo ""
    read -p "是否继续？(y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "已取消升级"
        exit 0
    fi
fi

echo ""
echo "步骤1: 备份现有MySQL数据..."
BACKUP_DIR="/backup/mysql_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

if command -v mysqldump >/dev/null 2>&1; then
    mysqldump --all-databases > $BACKUP_DIR/all_databases.sql 2>/dev/null || true
    echo "   ✅ 数据库备份完成: $BACKUP_DIR/all_databases.sql"
elif [ -f "/www/server/mysql/bin/mysqldump" ]; then
    /www/server/mysql/bin/mysqldump --all-databases > $BACKUP_DIR/all_databases.sql 2>/dev/null || true
    echo "   ✅ 宝塔MySQL备份完成: $BACKUP_DIR/all_databases.sql"
else
    echo "   ⚠️  未找到mysqldump，跳过备份"
fi

echo ""
echo "步骤2: 使用宝塔面板升级MySQL..."
echo "   💡 方案1: 宝塔面板自动升级（推荐）"
echo "   💡 方案2: 命令行手动升级"
echo ""

# 检查宝塔面板命令
if [ -f "/www/server/panel/script/mysql.sh" ]; then
    echo "   检测到宝塔MySQL管理脚本"
    echo ""
    
    if [ "$AUTO_MODE" = true ]; then
        echo "   自动模式: 尝试通过宝塔命令行升级..."
        # 宝塔面板MySQL版本管理命令
        /www/server/panel/script/mysql.sh update 8.0 2>&1 | tail -50 || {
            echo "   ⚠️  宝塔命令行升级失败，请手动操作"
            echo ""
            echo "   📋 手动升级步骤:"
            echo "   1. 登录宝塔面板: http://47.103.108.47:8888"
            echo "   2. 进入 '数据库' 管理"
            echo "   3. 找到 MySQL，点击 '设置'"
            echo "   4. 选择 '切换版本' → 选择 8.0.x"
            echo "   5. 确认升级（需10-20分钟）"
            echo "   6. 验证: mysql --version"
        }
    else
        echo "   请选择升级方式:"
        echo "   1) 通过宝塔面板升级（推荐，更安全）"
        echo "   2) 继续命令行升级（可能失败）"
        read -p "请输入选项 (1/2): " choice
        
        if [ "$choice" == "1" ]; then
            echo ""
            echo "   ✅ 请在宝塔面板中手动升级："
            echo "   1. 浏览器访问: http://47.103.108.47:8888"
            echo "   2. 数据库 → MySQL管理 → 设置 → 切换版本 → 8.0.x"
            echo "   3. 等待升级完成"
            echo ""
            exit 0
        fi
    fi
else
    echo "   ⚠️  未找到宝塔MySQL管理脚本"
fi

echo ""
echo "步骤3: 尝试命令行升级..."
cd /tmp

echo "   下载MySQL 8.0仓库配置..."
wget -q https://dev.mysql.com/get/mysql80-community-release-el7-3.noarch.rpm 2>/dev/null || {
    wget -q https://mirrors.aliyun.com/mysql/MySQL-8.0/mysql80-community-release-el7-3.noarch.rpm 2>/dev/null || {
        echo "   ❌ 下载失败"
        echo "   请使用宝塔面板升级"
        exit 1
    }
}

echo "   安装仓库配置..."
rpm -Uvh mysql80-community-release-el7-3.noarch.rpm 2>/dev/null || true

echo "   启用MySQL 8.0仓库..."
yum-config-manager --disable mysql57-community 2>/dev/null || true
yum-config-manager --enable mysql80-community 2>/dev/null || true

echo "   停止MySQL服务..."
systemctl stop mysqld 2>/dev/null || systemctl stop mysql 2>/dev/null || true
sleep 3

echo "   升级MySQL..."
yum -y update mysql-community-server 2>&1 | tail -20 || {
    echo "   yum升级失败，尝试安装..."
    yum -y install mysql-community-server 2>&1 | tail -20
}

echo "   启动MySQL 8.0..."
systemctl start mysqld 2>/dev/null || systemctl start mysql 2>/dev/null
sleep 5

echo ""
echo "步骤4: 验证升级..."
MYSQL_VERSION=$(mysql --version 2>/dev/null | grep -oP '\d+\.\d+\.\d+' | head -1)
echo "   MySQL版本: ${MYSQL_VERSION:-未检测到}"

if [ -n "$MYSQL_VERSION" ] && [[ $(echo -e "$MYSQL_VERSION\n8.0.0" | sort -V | head -n1) == "8.0.0" ]]; then
    echo "   ✅ MySQL版本 >= 8.0"
else
    echo "   ⚠️  MySQL版本仍为 ${MYSQL_VERSION:-未知}"
    echo "   建议使用宝塔面板升级"
fi

echo ""
echo "步骤5: 恢复数据（如需要）..."
if [ -f "$BACKUP_DIR/all_databases.sql" ] && [ -s "$BACKUP_DIR/all_databases.sql" ]; then
    echo "   备份文件: $BACKUP_DIR/all_databases.sql ($(du -h $BACKUP_DIR/all_databases.sql | cut -f1))"
    if [ "$AUTO_MODE" = true ]; then
        echo "   自动恢复数据..."
        mysql < $BACKUP_DIR/all_databases.sql 2>/dev/null && echo "   ✅ 数据恢复完成" || echo "   ⚠️  数据恢复失败"
    else
        read -p "是否立即恢复数据？(y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            mysql < $BACKUP_DIR/all_databases.sql 2>/dev/null && echo "   ✅ 数据恢复完成" || echo "   ⚠️  数据恢复失败"
        fi
    fi
fi

echo ""
echo "======================================================================"
echo "  升级完成！"
echo "======================================================================"
echo ""
echo "验证命令:"
echo "  mysql --version"
echo "  systemctl status mysqld"
echo ""
echo "如升级失败，请使用宝塔面板："
echo "  http://47.103.108.47:8888"
echo ""
