#!/bin/bash
# =====================================================
# 第八周服务器部署脚本
# 功能: 在服务器上拉取代码、初始化数据库、启动服务
# =====================================================

echo "=========================================="
echo "第八周任务 - 服务器部署"
echo "=========================================="
echo ""

# 配置变量
PROJECT_DIR="/root/course-project/week8"
DATA_SERVER_DIR="$PROJECT_DIR/data-server"
GITHUB_REPO="https://github.com/MOONFISH2233/software-design-project.git"
BRANCH="week8"

# 1. 拉取最新代码
echo "[1/7] 拉取最新代码..."
if [ -d "$PROJECT_DIR" ]; then
    cd $PROJECT_DIR
    git pull origin $BRANCH
else
    mkdir -p /root/course-project
    cd /root/course-project
    git clone -b $BRANCH $GITHUB_REPO week8
fi

cd $DATA_SERVER_DIR

# 2. 安装依赖
echo ""
echo "[2/7] 安装Python依赖..."
pip3 install flask flask-sqlalchemy apscheduler pyjwt cryptography pymongo pymysql flask-httpauth flask-limiter gunicorn

# 3. 初始化MySQL数据库
echo ""
echo "[3/7] 初始化MySQL数据库..."
mysql -u root -padmin <<EOF
source $DATA_SERVER_DIR/scripts/init_mysql_week8.sql;
EOF

if [ $? -eq 0 ]; then
    echo "✅ 数据库初始化成功"
else
    echo "❌ 数据库初始化失败，请检查MySQL服务是否运行"
    exit 1
fi

# 4. 验证数据库表
echo ""
echo "[4/7] 验证数据库表..."
TABLE_COUNT=$(mysql -u root -padmin -e "USE software_design; SHOW TABLES;" | wc -l)
echo "数据库表数量: $((TABLE_COUNT - 1))"

if [ $((TABLE_COUNT - 1)) -eq 15 ]; then
    echo "✅ 所有15个表创建成功"
else
    echo "⚠️  表数量不正确，预期15个，实际$((TABLE_COUNT - 1))个"
fi

# 5. 整理项目文件结构
echo ""
echo "[5/7] 整理项目文件结构..."
bash $DATA_SERVER_DIR/scripts/organize_project.sh

# 6. 重启应用服务
echo ""
echo "[6/7] 重启应用服务..."
systemctl restart gunicorn-flask-data-server

if [ $? -eq 0 ]; then
    echo "✅ 应用服务重启成功"
else
    echo "❌ 应用服务重启失败"
    exit 1
fi

# 7. 启动定时任务
echo ""
echo "[7/7] 启动定时任务..."

# 检查是否已有定时任务服务
if systemctl list-unit-files | grep -q "daily-statistics.service"; then
    systemctl restart daily-statistics
    echo "✅ 定时任务服务已重启"
else
    echo "⚠️  定时任务服务未配置，以后台进程方式启动..."
    nohup python3 $DATA_SERVER_DIR/tasks/daily_statistics.py > /var/log/daily_statistics.log 2>&1 &
    echo "✅ 定时任务已后台启动"
fi

# 验证部署
echo ""
echo "=========================================="
echo "验证部署..."
echo "=========================================="

sleep 3

# 检查应用健康状态
HEALTH_CHECK=$(curl -s http://localhost:5000/api/health)
if echo $HEALTH_CHECK | grep -q "ok"; then
    echo "✅ 应用健康检查通过"
else
    echo "❌ 应用健康检查失败"
    echo "响应: $HEALTH_CHECK"
fi

# 检查定时任务日志
if [ -f "/var/log/daily_statistics.log" ]; then
    echo "✅ 定时任务日志文件存在"
    echo "最后10行日志:"
    tail -n 10 /var/log/daily_statistics.log
else
    echo "⚠️  定时任务日志文件不存在"
fi

# 显示服务状态
echo ""
echo "=========================================="
echo "服务状态"
echo "=========================================="
echo ""
echo "Gunicorn服务:"
systemctl status gunicorn-flask-data-server --no-pager -l | head -n 10
echo ""
echo "定时任务进程:"
ps aux | grep daily_statistics | grep -v grep
echo ""

echo "=========================================="
echo "部署完成！"
echo "=========================================="
echo ""
echo "访问地址:"
echo "  - API健康检查: http://47.103.108.47:5000/api/health"
echo "  - API文档: http://47.103.108.47:5000/api/docs"
echo ""
echo "查看日志:"
echo "  - 应用日志: tail -f /root/course-project/logs/server_*.log"
echo "  - 定时任务日志: tail -f /var/log/daily_statistics.log"
echo ""
echo "测试API接口:"
echo "  curl http://47.103.108.47:5000/api/miniprogram/user/register \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"username\":\"test\",\"password\":\"123456\",\"phone\":\"13800138000\"}'"
echo ""
