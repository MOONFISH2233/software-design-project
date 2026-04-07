#!/bin/bash
# 压力测试模式启动脚本
# 使用方法：bash start_load_test_mode.sh

echo "============================================================"
echo "  压力测试模式 - 启动服务器"
echo "============================================================"
echo ""
echo "此模式将放宽请求限流，允许高并发压力测试"
echo ""

# 设置环境变量
export RATE_LIMIT_ENABLED=false

echo "启动服务器（压力测试模式）..."
echo ""

# 杀死旧进程
pkill -f "python app.py" 2>/dev/null
sleep 2

# 启动服务器
nohup python app.py > server_load_test.log 2>&1 &

echo ""
echo "✅ 服务器已启动（PID: $!）"
echo "📄 日志文件：server_load_test.log"
echo ""
echo "等待 3 秒让服务器完全启动..."
sleep 3

# 验证服务器
curl -s http://localhost:5000/api/health | python -m json.tool 2>/dev/null || echo "⚠️  服务器可能未完全启动"

echo ""
echo "============================================================"
echo "  现在可以运行压力测试了！"
echo "============================================================"
echo ""
echo "示例命令："
echo "  python jmeter_test.py --url http://localhost:5000 --duration 60 --users 10 --type normal"
echo "  python jmeter_test.py --url http://localhost:5000 --duration 60 --users 10 --username user1 --password user123 --type encrypted"
echo ""
