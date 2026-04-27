#!/bin/bash
# MySQL 8.0 自动升级脚本 (Alibaba Cloud Linux 3 / CentOS)
# 此脚本将自动卸载MySQL 5.7并安装MySQL 8.0

set -e  # 遇到错误立即退出

echo "=========================================="
echo "MySQL 8.0 自动升级脚本"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}请使用root用户执行此脚本${NC}"
    exit 1
fi

# 步骤1: 备份数据
echo -e "${YELLOW}[步骤 1/6] 备份现有MySQL数据...${NC}"
BACKUP_DIR="/root/mysql_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# 获取MySQL root密码
MYSQL_ROOT_PASSWORD=$(grep 'mysql_root' /www/server/panel/data/default.sql 2>/dev/null | grep -oP "'\K[^']+" | tail -1)

if [ -z "$MYSQL_ROOT_PASSWORD" ]; then
    echo -e "${YELLOW}未找到MySQL密码,尝试从配置文件读取...${NC}"
    MYSQL_ROOT_PASSWORD=$(cat /etc/my.cnf 2>/dev/null | grep password | head -1 | awk -F'=' '{print $2}' | tr -d ' ')
fi

if [ -n "$MYSQL_ROOT_PASSWORD" ]; then
    echo "正在备份数据库..."
    mysqldump -u root -p"$MYSQL_ROOT_PASSWORD" --all-databases --single-transaction --quick > $BACKUP_DIR/all_databases.sql 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 数据库备份成功: $BACKUP_DIR/all_databases.sql${NC}"
        ls -lh $BACKUP_DIR/all_databases.sql
    else
        echo -e "${RED}✗ 数据库备份失败${NC}"
        read -p "是否继续升级? (y/n): " CONTINUE
        if [ "$CONTINUE" != "y" ]; then
            exit 1
        fi
    fi
    
    # 备份配置文件
    cp /etc/my.cnf $BACKUP_DIR/my.cnf.backup 2>/dev/null || true
    echo -e "${GREEN}✓ 配置文件已备份${NC}"
else
    echo -e "${RED}✗ 无法获取MySQL密码${NC}"
    echo "请手动提供MySQL root密码:"
    read -s MYSQL_ROOT_PASSWORD
fi

echo ""

# 步骤2: 停止MySQL服务
echo -e "${YELLOW}[步骤 2/6] 停止MySQL服务...${NC}"
systemctl stop mysqld
sleep 2
echo -e "${GREEN}✓ MySQL服务已停止${NC}"
echo ""

# 步骤3: 卸载MySQL 5.7
echo -e "${YELLOW}[步骤 3/6] 卸载MySQL 5.7...${NC}"
yum remove -y mysql-community-server mysql-community-client mysql-community-common mysql-community-libs 2>&1 | tail -5
echo -e "${GREEN}✓ MySQL 5.7已卸载${NC}"
echo ""

# 步骤4: 安装MySQL 8.0仓库
echo -e "${YELLOW}[步骤 4/6] 配置MySQL 8.0仓库...${NC}"

# 下载MySQL 8.0仓库配置
yum install -y https://dev.mysql.com/get/mysql80-community-release-el7-9.noarch.rpm 2>&1 | tail -3

# 禁用MySQL 5.7仓库,启用8.0仓库
yum-config-manager --disable mysql57-community 2>/dev/null || true
yum-config-manager --enable mysql80-community 2>/dev/null || true

echo -e "${GREEN}✓ MySQL 8.0仓库配置完成${NC}"
echo ""

# 步骤5: 安装MySQL 8.0
echo -e "${YELLOW}[步骤 5/6] 安装MySQL 8.0...${NC}"
echo "这可能需要几分钟时间,请耐心等待..."
yum install -y mysql-community-server 2>&1 | tail -10

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ MySQL 8.0安装成功${NC}"
else
    echo -e "${RED}✗ MySQL 8.0安装失败${NC}"
    exit 1
fi
echo ""

# 步骤6: 启动MySQL 8.0
echo -e "${YELLOW}[步骤 6/6] 启动MySQL 8.0...${NC}"
systemctl start mysqld
sleep 5

# 检查服务状态
if systemctl is-active --quiet mysqld; then
    echo -e "${GREEN}✓ MySQL 8.0服务已启动${NC}"
else
    echo -e "${RED}✗ MySQL 8.0服务启动失败${NC}"
    journalctl -u mysqld -n 20 --no-pager
    exit 1
fi

# 获取临时密码
TEMP_PASSWORD=$(grep 'temporary password' /var/log/mysqld.log | tail -1 | awk '{print $NF}')

echo ""
echo "=========================================="
echo -e "${GREEN}MySQL 8.0 安装完成!${NC}"
echo "=========================================="
echo ""
echo "当前版本:"
mysql --version
echo ""

if [ -n "$TEMP_PASSWORD" ]; then
    echo -e "${YELLOW}临时密码: ${TEMP_PASSWORD}${NC}"
    echo ""
    echo "请使用以下命令修改root密码:"
    echo "mysql -u root -p'$TEMP_PASSWORD'"
    echo "ALTER USER 'root'@'localhost' IDENTIFIED BY '你的新密码';"
    echo "FLUSH PRIVILEGES;"
    echo ""
    
    # 自动设置密码
    echo "是否自动设置root密码? (y/n):"
    read -p "" SET_PASSWORD
    
    if [ "$SET_PASSWORD" = "y" ]; then
        NEW_PASSWORD="${MYSQL_ROOT_PASSWORD:-YourNewPassword123!}"
        echo "使用密码: $NEW_PASSWORD"
        
        # 修改密码
        mysql -u root -p"$TEMP_PASSWORD" --connect-expired-password <<EOF
ALTER USER 'root'@'localhost' IDENTIFIED BY '$NEW_PASSWORD';
FLUSH PRIVILEGES;
EOF
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ 密码设置成功${NC}"
            
            # 更新宝塔面板的MySQL密码
            if [ -f /www/server/panel/data/default.sql ]; then
                sed -i "s/'mysql_root', '[^']*'/'mysql_root', '$NEW_PASSWORD'/" /www/server/panel/data/default.sql 2>/dev/null || true
                echo -e "${GREEN}✓ 已更新宝塔面板配置${NC}"
            fi
        else
            echo -e "${RED}✗ 密码设置失败${NC}"
        fi
    fi
fi

echo ""
echo "=========================================="
echo "验证信息"
echo "=========================================="
echo "MySQL版本: $(mysql --version)"
echo "服务状态: $(systemctl is-active mysqld)"
echo ""

if [ -f "$BACKUP_DIR/all_databases.sql" ]; then
    echo "数据备份位置: $BACKUP_DIR/all_databases.sql"
    echo ""
    echo "如需恢复数据,请执行:"
    echo "mysql -u root -p < $BACKUP_DIR/all_databases.sql"
fi

echo ""
echo -e "${GREEN}升级完成!${NC}"
echo ""
