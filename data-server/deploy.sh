#!/bin/bash

# Jenkins 部署脚本
# 实现云端服务器代码一键更新和重启

echo "=========================================="
echo "  Flask 数据服务器 - 自动化部署脚本"
echo "=========================================="

# 1. 进入项目目录
cd /root/data-server || exit 1

# 2. 拉取最新代码（如果使用 Git）
echo "[1/4] 拉取最新代码..."
if [ -d ".git" ]; then
    git pull origin main
    echo "✓ 代码更新完成"
else
    echo "  非 Git 项目，跳过代码拉取"
fi

# 3. 安装依赖
echo ""
echo "[2/4] 安装 Python 依赖..."
pip3 install -r requirements.txt
echo "✓ 依赖安装完成"

# 4. 停止旧进程
echo ""
echo "[3/4] 停止旧服务..."
pkill -f "python.*app.py" || true
sleep 2
echo "✓ 旧服务已停止"

# 5. 启动新服务
echo ""
echo "[4/4] 启动新服务..."
nohup python3 app.py > deploy.log 2>&1 &

# 6. 等待启动并检查
sleep 3
if pgrep -f "python.*app.py" > /dev/null; then
    echo "✓ 服务启动成功"
    echo ""
    echo "=========================================="
    echo "  部署完成！"
    echo "  服务地址：http://47.103.108.47:5000"
    echo "  健康检查：http://47.103.108.47:5000/api/health"
    echo "=========================================="
else
    echo "✗ 服务启动失败，请查看 deploy.log"
    exit 1
fi
