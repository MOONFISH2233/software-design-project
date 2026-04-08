#!/bin/bash
# =====================================================
# 生产级部署脚本 - Gunicorn + Gevent
# 用途：将 Flask 应用升级为商业级高并发服务
# =====================================================

set -e  # 遇到错误立即退出

echo "============================================================"
echo "🚀 Flask 应用生产级部署脚本"
echo "============================================================"

# 配置变量
PROJECT_DIR="/root/course-project/week5/data-server"
SERVICE_NAME="gunicorn-flask-data-server"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ==================== 步骤 1: 安装依赖 ====================
echo ""
echo -e "${YELLOW}[1/6]${NC} 安装 Gunicorn 和 Gevent..."
pip install gunicorn gevent --upgrade

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 依赖安装成功${NC}"
else
    echo -e "${RED}❌ 依赖安装失败${NC}"
    exit 1
fi

# ==================== 步骤 2: 停止旧服务 ====================
echo ""
echo -e "${YELLOW}[2/6]${NC} 停止旧服务..."

# 停止 Flask 开发服务器
pkill -f "python app.py" 2>/dev/null || true

# 停止旧的 Gunicorn（如果有）
if systemctl is-active --quiet $SERVICE_NAME 2>/dev/null; then
    systemctl stop $SERVICE_NAME
    echo "✅ Systemd 服务已停止"
fi

# 清理 PID 文件
rm -f $PROJECT_DIR/gunicorn.pid

sleep 2
echo -e "${GREEN}✅ 旧服务已清理${NC}"

# ==================== 步骤 3: 配置文件检查 ====================
echo ""
echo -e "${YELLOW}[3/6]${NC} 检查配置文件..."

cd $PROJECT_DIR

# 检查 Gunicorn 配置
if [ ! -f "gunicorn_config.py" ]; then
    echo -e "${RED}❌ gunicorn_config.py 不存在${NC}"
    exit 1
fi

# 检查 app.py
if [ ! -f "app.py" ]; then
    echo -e "${RED}❌ app.py 不存在${NC}"
    exit 1
fi

# 语法检查
python -m py_compile app.py
echo -e "${GREEN}✅ 配置文件检查通过${NC}"

# ==================== 步骤 4: 创建日志目录 ====================
echo ""
echo -e "${YELLOW}[4/6]${NC} 创建日志目录..."

mkdir -p $PROJECT_DIR/logs
chmod 755 $PROJECT_DIR/logs

echo -e "${GREEN}✅ 日志目录已创建${NC}"

# ==================== 步骤 5: 安装 Systemd 服务 ====================
echo ""
echo -e "${YELLOW}[5/6]${NC} 安装 Systemd 服务..."

# 复制服务文件
cp $PROJECT_DIR/gunicorn-flask-data-server.service /etc/systemd/system/

# 重载 systemd
systemctl daemon-reload

# 启用开机自启
systemctl enable $SERVICE_NAME

echo -e "${GREEN}✅ Systemd 服务已安装并启用开机自启${NC}"

# ==================== 步骤 6: 启动服务 ====================
echo ""
echo -e "${YELLOW}[6/6]${NC} 启动 Gunicorn 服务..."

systemctl start $SERVICE_NAME

# 等待服务启动
sleep 3

# 检查服务状态
if systemctl is-active --quiet $SERVICE_NAME; then
    echo -e "${GREEN}✅ Gunicorn 服务启动成功！${NC}"
else
    echo -e "${RED}❌ Gunicorn 服务启动失败${NC}"
    echo "查看日志："
    journalctl -u $SERVICE_NAME -n 20 --no-pager
    exit 1
fi

# ==================== 验证服务 ====================
echo ""
echo "============================================================"
echo "🔍 验证服务..."
echo "============================================================"

# 健康检查
HEALTH_CHECK=$(curl -s http://localhost:5000/api/health)
if echo "$HEALTH_CHECK" | grep -q "healthy"; then
    echo -e "${GREEN}✅ 健康检查通过${NC}"
    echo "$HEALTH_CHECK" | python -m json.tool 2>/dev/null || echo "$HEALTH_CHECK"
else
    echo -e "${RED}❌ 健康检查失败${NC}"
    exit 1
fi

# ==================== 显示服务信息 ====================
echo ""
echo "============================================================"
echo -e "${GREEN}🎉 部署完成！${NC}"
echo "============================================================"
echo ""
echo "📊 服务信息："
echo "   - 服务名称: $SERVICE_NAME"
echo "   - 监听地址: http://0.0.0.0:5000"
echo "   - Worker 数量: $(grep 'workers =' $PROJECT_DIR/gunicorn_config.py | awk '{print $3}')"
echo "   - Worker 类型: gevent (异步)"
echo ""
echo "📝 管理命令："
echo "   - 查看状态:   systemctl status $SERVICE_NAME"
echo "   - 启动服务:   systemctl start $SERVICE_NAME"
echo "   - 停止服务:   systemctl stop $SERVICE_NAME"
echo "   - 重启服务:   systemctl restart $SERVICE_NAME"
echo "   - 查看日志:   journalctl -u $SERVICE_NAME -f"
echo "   - 实时日志:   tail -f $PROJECT_DIR/logs/gunicorn_access.log"
echo ""
echo "📁 日志文件："
echo "   - 访问日志: $PROJECT_DIR/logs/gunicorn_access.log"
echo "   - 错误日志: $PROJECT_DIR/logs/gunicorn_error.log"
echo "   - 系统日志: journalctl -u $SERVICE_NAME"
echo ""
echo "⚙️  性能调优："
echo "   - 编辑配置: vi $PROJECT_DIR/gunicorn_config.py"
echo "   - 修改后重启: systemctl restart $SERVICE_NAME"
echo ""
echo "============================================================"
