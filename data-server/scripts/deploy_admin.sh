#!/bin/bash

echo "=========================================="
echo "  智能皮肤健康监测系统 - 管理端部署脚本"
echo "=========================================="

# 检查参数
if [ $# -eq 0 ]; then
    echo "用法: $0 <服务器IP> [端口]"
    echo "示例: $0 47.103.108.47 5000"
    exit 1
fi

SERVER_IP="$1"
PORT="${2:-5000}"

echo ""
echo "📦 开始部署到服务器: $SERVER_IP"
echo ""

# 1. 复制静态文件到服务器
echo "1️⃣ 上传静态文件..."
scp -r static/ admin@$SERVER_IP:/home/admin/skin-health-server/static/

# 2. 复制主应用文件
echo "2️⃣ 上传应用代码..."
scp app.py admin@$SERVER_IP:/home/admin/skin-health-server/
scp models.py admin@$SERVER_IP:/home/admin/skin-health-server/
scp wsgi.py admin@$SERVER_IP:/home/admin/skin-health-server/
scp gunicorn_config.py admin@$SERVER_IP:/home/admin/skin-health-server/

# 3. 复制路由文件
echo "3️⃣ 上传路由文件..."
scp -r routes/ admin@$SERVER_IP:/home/admin/skin-health-server/routes/

# 4. 重启服务
echo "4️⃣ 重启服务..."
ssh admin@$SERVER_IP "cd /home/admin/skin-health-server && systemctl restart gunicorn-flask-data-server"

echo ""
echo "✅ 部署完成!"
echo ""
echo "访问地址:"
echo "  - 管理端: http://$SERVER_IP:$PORT/static/admin.html"
echo "  - 用户端: http://$SERVER_IP:$PORT/static/index.html"
echo ""
echo "测试账号:"
echo "  - admin / admin123 (管理员)"
echo "  - user1 / user123 (普通用户)"