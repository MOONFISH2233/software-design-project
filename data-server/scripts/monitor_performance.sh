#!/bin/bash
# =====================================================
# Gunicorn 性能监控脚本
# 用途：实时监控服务性能和资源使用
# =====================================================

SERVICE_NAME="gunicorn-flask-data-server"
PROJECT_DIR="/root/course-project/week5/data-server"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "============================================================"
echo -e "${BLUE}📊 Gunicorn 性能监控面板${NC}"
echo "============================================================"
echo ""

# ==================== 1. 服务状态 ====================
echo -e "${YELLOW}[1] 服务状态${NC}"
if systemctl is-active --quiet $SERVICE_NAME; then
    echo -e "   ${GREEN}✅ 运行中${NC}"
else
    echo -e "   ${RED}❌ 已停止${NC}"
    exit 1
fi
echo ""

# ==================== 2. Worker 信息 ====================
echo -e "${YELLOW}[2] Worker 进程${NC}"
ps aux | grep "[g]unicorn" | grep -v grep | while read line; do
    PID=$(echo "$line" | awk '{print $2}')
    CPU=$(echo "$line" | awk '{print $3}')
    MEM=$(echo "$line" | awk '{print $4}')
    echo -e "   PID: $PID  |  CPU: ${CPU}%  |  内存: ${MEM}%"
done
echo ""

# ==================== 3. 系统资源 ====================
echo -e "${YELLOW}[3] 系统资源使用${NC}"
TOTAL_WORKERS=$(ps aux | grep "[g]unicorn: worker" | wc -l)
TOTAL_CPU=$(ps aux | grep "[g]unicorn" | awk '{sum+=$3} END {print sum}')
TOTAL_MEM=$(ps aux | grep "[g]unicorn" | awk '{sum+=$4} END {print sum}')

echo -e "   Worker 数量: $TOTAL_WORKERS"
echo -e "   总 CPU 使用: ${TOTAL_CPU}%"
echo -e "   总内存使用: ${TOTAL_MEM}%"
echo ""

# ==================== 4. 连接统计 ====================
echo -e "${YELLOW}[4] 网络连接统计${NC}"
ESTABLISHED=$(netstat -an | grep ":5000" | grep "ESTABLISHED" | wc -l)
TIME_WAIT=$(netstat -an | grep ":5000" | grep "TIME_WAIT" | wc -l)
LISTEN=$(netstat -an | grep ":5000" | grep "LISTEN" | wc -l)

echo -e "   活跃连接 (ESTABLISHED): $ESTABLISHED"
echo -e "   等待关闭 (TIME_WAIT): $TIME_WAIT"
echo -e "   监听端口 (LISTEN): $LISTEN"
echo ""

# ==================== 5. 最近请求统计 ====================
echo -e "${YELLOW}[5] 最近请求统计（最后 100 条）${NC}"
if [ -f "$PROJECT_DIR/logs/gunicorn_access.log" ]; then
    TOTAL_REQUESTS=$(tail -100 "$PROJECT_DIR/logs/gunicorn_access.log" | wc -l)
    SUCCESS_200=$(tail -100 "$PROJECT_DIR/logs/gunicorn_access.log" | grep '" 200 ' | wc -l)
    ERROR_4XX=$(tail -100 "$PROJECT_DIR/logs/gunicorn_access.log" | grep '" 4[0-9][0-9] ' | wc -l)
    ERROR_5XX=$(tail -100 "$PROJECT_DIR/logs/gunicorn_access.log" | grep '" 5[0-9][0-9] ' | wc -l)
    
    echo -e "   总请求数: $TOTAL_REQUESTS"
    echo -e "   成功 (200): $SUCCESS_200"
    echo -e "   客户端错误 (4xx): $ERROR_4XX"
    echo -e "   服务器错误 (5xx): $ERROR_5XX"
else
    echo -e "   ${RED}日志文件不存在${NC}"
fi
echo ""

# ==================== 6. 响应时间统计 ====================
echo -e "${YELLOW}[6] 响应时间统计（最后 100 条）${NC}"
if [ -f "$PROJECT_DIR/logs/gunicorn_access.log" ]; then
    # 提取响应时间（最后一列，单位微秒）
    RESPONSE_TIMES=$(tail -100 "$PROJECT_DIR/logs/gunicorn_access.log" | awk '{print $NF}' | grep -E '^[0-9]+$')
    
    if [ ! -z "$RESPONSE_TIMES" ]; then
        AVG_TIME=$(echo "$RESPONSE_TIMES" | awk '{sum+=$1; count++} END {if(count>0) printf "%.2f", sum/count/1000; else print 0}')
        MAX_TIME=$(echo "$RESPONSE_TIMES" | sort -n | tail -1)
        MAX_TIME_MS=$(echo "scale=2; $MAX_TIME / 1000" | bc)
        
        echo -e "   平均响应时间: ${AVG_TIME}ms"
        echo -e "   最大响应时间: ${MAX_TIME_MS}ms"
    else
        echo -e "   暂无数据"
    fi
else
    echo -e "   ${RED}日志文件不存在${NC}"
fi
echo ""

# ==================== 7. 磁盘使用 ====================
echo -e "${YELLOW}[7] 磁盘使用${NC}"
DATA_SIZE=$(du -sh "$PROJECT_DIR/data" 2>/dev/null | cut -f1 || echo "N/A")
LOG_SIZE=$(du -sh "$PROJECT_DIR/logs" 2>/dev/null | cut -f1 || echo "N/A")

echo -e "   数据目录: $DATA_SIZE"
echo -e "   日志目录: $LOG_SIZE"
echo ""

# ==================== 8. 快速操作菜单 ====================
echo "============================================================"
echo -e "${BLUE}⚡ 快速操作${NC}"
echo "============================================================"
echo "   1. 查看实时日志:     tail -f $PROJECT_DIR/logs/gunicorn_access.log"
echo "   2. 查看错误日志:     tail -f $PROJECT_DIR/logs/gunicorn_error.log"
echo "   3. 重启服务:         systemctl restart $SERVICE_NAME"
echo "   4. 停止服务:         systemctl stop $SERVICE_NAME"
echo "   5. 查看完整状态:     systemctl status $SERVICE_NAME"
echo "   6. 运行压力测试:     python $PROJECT_DIR/jmeter_test.py --url http://localhost:5000 --duration 60 --users 10 --username user1 --password user123 --type encrypted"
echo "============================================================"
