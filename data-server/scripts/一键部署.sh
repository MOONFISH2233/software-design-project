#!/bin/bash

# 一键部署脚本
# 在服务器上执行此脚本完成 Flask 数据服务器的部署

echo "=========================================="
echo "  Flask 数据服务器 - 一键部署脚本"
echo "=========================================="
echo ""

# 1. 检查 Python
echo "[检查] Python 环境..."
python3 --version
if [ $? -ne 0 ]; then
    echo "错误：未找到 Python3，请先安装 Python3"
    exit 1
fi
echo "✓ Python 环境正常"
echo ""

# 2. 创建目录
echo "[1/5] 创建目录结构..."
mkdir -p /root/data-server/logs
mkdir -p /root/data-server/data
echo "✓ 目录创建完成"
echo ""

# 3. 安装依赖
echo "[2/5] 安装 Python 依赖..."
cd /root/data-server
pip3 install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✓ 依赖安装完成"
else
    echo "  警告：依赖安装可能有问题，继续执行..."
fi
echo ""

# 4. 停止旧进程
echo "[3/5] 停止旧服务..."
pkill -f "python.*app.py" 2>/dev/null || true
sleep 2
echo "✓ 旧服务已停止"
echo ""

# 5. 启动新服务
echo "[4/5] 启动 Flask 服务..."
nohup python3 /root/data-server/app.py > /root/data-server/server.log 2>&1 &
sleep 3

# 检查进程
if pgrep -f "python.*app.py" > /dev/null; then
    echo "✓ 服务启动成功"
    PID=$(pgrep -f "python.*app.py")
    echo "  进程 ID: $PID"
else
    echo "✗ 服务启动失败"
    echo "查看日志："
    tail -50 /root/data-server/server.log
    exit 1
fi
echo ""

# 6. 健康检查
echo "[5/5] 健康检查..."
sleep 2
RESPONSE=$(curl -s http://localhost:5000/api/health)
if [ $? -eq 0 ]; then
    echo "✓ 健康检查通过"
    echo "  响应：$RESPONSE"
else
    echo "  警告：健康检查失败，但服务可能仍在运行"
fi
echo ""

# 7. 配置防火墙
echo "[配置] 防火墙设置..."
firewall-cmd --zone=public --add-port=5000/tcp --permanent 2>/dev/null || true
firewall-cmd --reload 2>/dev/null || true
echo "✓ 防火墙配置完成（如果支持）"
echo ""

# 完成
echo "=========================================="
echo "  🎉 部署完成！"
echo "=========================================="
echo ""
echo "服务信息:"
echo "  本地访问：http://localhost:5000"
echo "  外网访问：http://47.103.108.47:5000"
echo "  健康检查：http://47.103.108.47:5000/api/health"
echo ""
echo "常用命令:"
echo "  查看日志：tail -f /root/data-server/server.log"
echo "  重启服务：./deploy.sh"
echo "  停止服务：pkill -f app.py"
echo "  查看进程：ps aux | grep app.py"
echo ""
echo "API 接口:"
echo "  POST /api/receive  - 接收数据"
echo "  GET  /api/health   - 健康检查"
echo "  GET  /api/logs     - 查看日志"
echo ""
echo "=========================================="
