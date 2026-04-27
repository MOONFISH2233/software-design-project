#!/bin/bash
# ============================================================================
# 第七周任务完成验证脚本 - 实时数据流验证
# 用途: 自动化验证MySQL数据库、定时任务、Flask接口等功能
# 执行: bash scripts/verify_week7_tasks.sh
# ============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 服务器配置
SERVER="root@47.103.108.47"
MYSQL_USER="root"
MYSQL_PASS="admin"
DB_NAME="sensor_project"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  第七周任务完成验证 - 实时数据流测试${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 计数器
PASS_COUNT=0
FAIL_COUNT=0

# 验证函数
check_result() {
    if [ $1 -eq 0 ]; then
        echo -e "  ${GREEN}✅ PASS:${NC} $2"
        ((PASS_COUNT++))
    else
        echo -e "  ${RED}❌ FAIL:${NC} $2"
        ((FAIL_COUNT++))
    fi
}

# ============================================================================
# 1. MySQL数据库验证
# ============================================================================
echo -e "${YELLOW}[1/6] 验证MySQL 8.0数据库...${NC}"

# 1.1 检查MySQL版本
VERSION=$(ssh $SERVER "mysql --version 2>/dev/null | grep -oP '8\.\d+\.\d+'" || echo "")
if [[ "$VERSION" =~ ^8\. ]]; then
    check_result 0 "MySQL版本: $VERSION (符合8.0+要求)"
else
    check_result 1 "MySQL版本不符合要求"
fi

# 1.2 检查数据库是否存在
DB_EXISTS=$(ssh $SERVER "mysql -u $MYSQL_USER -p$MYSQL_PASS -e \"SHOW DATABASES LIKE '$DB_NAME';\" 2>/dev/null | grep -c $DB_NAME" || echo "0")
check_result $([ "$DB_EXISTS" -eq 1 ] && echo 0 || echo 1) "数据库 '$DB_NAME' 存在"

# 1.3 检查表数量
TABLE_COUNT=$(ssh $SERVER "mysql -u $MYSQL_USER -p$MYSQL_PASS -e \"USE $DB_NAME; SHOW TABLES;\" 2>/dev/null | tail -n +2 | wc -l" || echo "0")
check_result $([ "$TABLE_COUNT" -eq 8 ] && echo 0 || echo 1) "数据表数量: $TABLE_COUNT/8"

# 1.4 列出所有表
echo -e "  ${BLUE}📋 数据表清单:${NC}"
ssh $SERVER "mysql -u $MYSQL_USER -p$MYSQL_PASS -e \"USE $DB_NAME; SHOW TABLES;\" 2>/dev/null | tail -n +2" | while read table; do
    echo -e "     • $table"
done

echo ""

# ============================================================================
# 2. 定时任务服务验证
# ============================================================================
echo -e "${YELLOW}[2/6] 验证Python定时任务服务...${NC}"

# 2.1 检查服务状态
SERVICE_STATUS=$(ssh $SERVER "systemctl is-active daily-statistics 2>/dev/null" || echo "inactive")
check_result $([ "$SERVICE_STATUS" = "active" ] && echo 0 || echo 1) "定时任务服务状态: $SERVICE_STATUS"

# 2.2 检查APScheduler进程
PROCESS_COUNT=$(ssh $SERVER "ps aux | grep daily_statistics.py | grep -v grep | wc -l" || echo "0")
check_result $([ "$PROCESS_COUNT" -gt 0 ] && echo 0 || echo 1) "定时任务进程运行中: $PROCESS_COUNT个"

# 2.3 查看最近日志
echo -e "  ${BLUE}📝 最近日志记录:${NC}"
ssh $SERVER "tail -5 /var/log/daily_statistics.log 2>/dev/null | tail -3" | while read line; do
    echo -e "     $line"
done

echo ""

# ============================================================================
# 3. Flask API接口验证
# ============================================================================
echo -e "${YELLOW}[3/6] 验证Flask MySQL CRUD接口...${NC}"

# 3.1 健康检查
HEALTH=$(curl -s http://47.103.108.47:5000/api/health 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','error'))" 2>/dev/null || echo "error")
check_result $([ "$HEALTH" = "healthy" ] && echo 0 || echo 1) "Flask服务健康状态: $HEALTH"

# 3.2 测试设备列表接口
DEVICES_RESPONSE=$(curl -s -w "%{http_code}" http://47.103.108.47:5000/api/mysql/devices 2>/dev/null)
DEVICES_CODE=${DEVICES_RESPONSE: -3}
check_result $([ "$DEVICES_CODE" = "200" ] && echo 0 || echo 1) "GET /api/mysql/devices 返回码: $DEVICES_CODE"

# 3.3 测试统计数据接口
STATS_RESPONSE=$(curl -s -w "%{http_code}" http://47.103.108.47:5000/api/mysql/statistics 2>/dev/null)
STATS_CODE=${STATS_RESPONSE: -3}
check_result $([ "$STATS_CODE" = "200" ] && echo 0 || echo 1) "GET /api/mysql/statistics 返回码: $STATS_CODE"

# 3.4 显示接口响应示例
echo -e "  ${BLUE}📡 接口响应示例:${NC}"
echo -e "     GET /api/mysql/devices:"
curl -s http://47.103.108.47:5000/api/mysql/devices 2>/dev/null | python3 -m json.tool 2>/dev/null | head -10 | sed 's/^/       /'

echo ""

# ============================================================================
# 4. 实时数据写入测试
# ============================================================================
echo -e "${YELLOW}[4/6] 实时数据写入测试...${NC}"

# 4.1 插入测试数据到MongoDB
echo -e "  ${BLUE}🔧 步骤1: 向MongoDB插入测试数据...${NC}"
TEST_DATA='{"device_id": "TEST_DEVICE_001", "moisture": 45.5, "oiliness": 32.1, "temperature": 36.5, "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}'
ssh $SERVER "mongosh sensor_data --eval \"db.skin_sensor.insertOne($TEST_DATA)\" 2>/dev/null" > /dev/null 2>&1
check_result $? "测试数据已写入MongoDB skin_sensor集合"

# 4.2 手动触发统计任务(模拟每日定时任务)
echo -e "  ${BLUE}🔧 步骤2: 手动触发统计计算...${NC}"
ssh $SERVER "cd /root/course-project/week5/data-server/data-server && python3 tasks/daily_statistics.py <<EOF
from tasks.daily_statistics import DailyStatisticsTask
task = DailyStatisticsTask()
result = task.calculate_daily_statistics()
print(f'Statistics calculation result: {result}')
task.close()
EOF" 2>&1 | grep -E "(开始计算|总记录数|✅|❌)" | tail -5 | while read line; do
    echo -e "     $line"
done

# 4.3 验证MySQL中是否有统计数据
STATS_COUNT=$(ssh $SERVER "mysql -u $MYSQL_USER -p$MYSQL_PASS -e \"USE $DB_NAME; SELECT COUNT(*) FROM daily_statistics;\" 2>/dev/null | tail -1" || echo "0")
check_result $([ "$STATS_COUNT" -gt 0 ] && echo 0 || echo 1) "MySQL daily_statistics表记录数: $STATS_COUNT"

# 4.4 显示最新统计记录
echo -e "  ${BLUE}📊 最新统计记录:${NC}"
ssh $SERVER "mysql -u $MYSQL_USER -p$MYSQL_PASS -e \"USE $DB_NAME; SELECT stat_date, total_records, active_devices, avg_moisture FROM daily_statistics ORDER BY calculated_at DESC LIMIT 1;\" 2>/dev/null" | column -t | sed 's/^/     /'

echo ""

# ============================================================================
# 5. 完整数据流演示
# ============================================================================
echo -e "${YELLOW}[5/6] 完整数据流演示 (传感器→MongoDB→统计→MySQL→API)...${NC}"

# 5.1 模拟传感器上传数据
echo -e "  ${BLUE}📤 步骤1: 模拟传感器数据上传...${NC}"
for i in {1..3}; do
    DEVICE_ID="SENSOR_$i"
    MOISTURE=$((RANDOM % 100))
    curl -s -X POST http://47.103.108.47:5000/api/receive \
         -H "Content-Type: application/json" \
         -d "{\"device_id\": \"$DEVICE_ID\", \"type\": \"skin\", \"data\": {\"moisture\": $MOISTURE}}" \
         > /dev/null 2>&1
    echo -e "     ✅ 设备 $DEVICE_ID 数据已上传 (水分: $MOISTURE%)"
done

# 5.2 等待数据写入MongoDB
sleep 2
echo -e "  ${BLUE}⏳ 等待数据写入MongoDB...${NC}"
MONGO_COUNT=$(ssh $SERVER "mongosh sensor_data --quiet --eval \"db.skin_sensor.countDocuments({device_id: {\$in: ['SENSOR_1', 'SENSOR_2', 'SENSOR_3']}})\" 2>/dev/null" || echo "0")
check_result $([ "$MONGO_COUNT" -ge 3 ] && echo 0 || echo 1) "MongoDB中新增记录数: $MONGO_COUNT"

# 5.3 通过API查询MySQL数据
echo -e "  ${BLUE}📥 步骤2: 通过API查询MySQL统计数据...${NC}"
curl -s http://47.103.108.47:5000/api/mysql/statistics/latest 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data.get('code') == 200:
        stats = data['data']
        print(f'     ✅ 最新统计日期: {stats.get(\"stat_date\", \"N/A\")}')
        print(f'     ✅ 总记录数: {stats.get(\"total_records\", 0)}')
        print(f'     ✅ 活跃设备: {stats.get(\"active_devices\", 0)}')
    else:
        print(f'     ⚠️ 暂无统计数据 (code: {data.get(\"code\")})')
except:
    print('     ⚠️ 解析响应失败')
"

echo ""

# ============================================================================
# 6. 性能测试
# ============================================================================
echo -e "${YELLOW}[6/6] API接口性能测试...${NC}"

# 6.1 并发请求测试
echo -e "  ${BLUE}⚡ 发送50个并发请求测试...${NC}"
START_TIME=$(date +%s%N)
for i in {1..50}; do
    curl -s http://47.103.108.47:5000/api/mysql/devices > /dev/null 2>&1 &
done
wait
END_TIME=$(date +%s%N)
ELAPSED=$(( (END_TIME - START_TIME) / 1000000 ))
AVG_TIME=$(( ELAPSED / 50 ))
check_result $([ "$AVG_TIME" -lt 1000 ] && echo 0 || echo 1) "平均响应时间: ${AVG_TIME}ms (目标: <1000ms)"

# 6.2 成功率测试
SUCCESS_COUNT=0
for i in {1..20}; do
    CODE=$(curl -s -o /dev/null -w "%{http_code}" http://47.103.108.47:5000/api/mysql/devices 2>/dev/null)
    if [ "$CODE" = "200" ]; then
        ((SUCCESS_COUNT++))
    fi
done
SUCCESS_RATE=$(( SUCCESS_COUNT * 100 / 20 ))
check_result $([ "$SUCCESS_RATE" -ge 95 ] && echo 0 || echo 1) "请求成功率: ${SUCCESS_RATE}% (20次测试)"

echo ""

# ============================================================================
# 总结报告
# ============================================================================
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}           验证结果汇总${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "  ${GREEN}✅ 通过: $PASS_COUNT 项${NC}"
echo -e "  ${RED}❌ 失败: $FAIL_COUNT 项${NC}"
echo ""

TOTAL=$((PASS_COUNT + FAIL_COUNT))
if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "  ${GREEN}🎉 恭喜! 所有验证项全部通过!${NC}"
    echo -e "  ${GREEN}   第七周任务完成度: 100%${NC}"
elif [ $FAIL_COUNT -le 2 ]; then
    echo -e "  ${YELLOW}⚠️  大部分验证通过,建议修复失败项${NC}"
    echo -e "  ${YELLOW}   当前完成度: $(( PASS_COUNT * 100 / TOTAL ))%${NC}"
else
    echo -e "  ${RED}❌ 存在较多问题,请检查失败项${NC}"
    echo -e "  ${RED}   当前完成度: $(( PASS_COUNT * 100 / TOTAL ))%${NC}"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  详细报告已保存至:${NC}"
echo -e "${BLUE}  WEEK7_VERIFICATION_REPORT.md${NC}"
echo -e "${BLUE}========================================${NC}"

# 生成Markdown报告
cat > WEEK7_VERIFICATION_REPORT.md <<EOF
# 第七周任务验证报告

**验证时间**: $(date '+%Y-%m-%d %H:%M:%S')  
**验证人**: 自动化验证脚本  
**服务器**: 47.103.108.47

## 验证结果

- **总测试项**: $TOTAL
- **通过**: $PASS_COUNT ✅
- **失败**: $FAIL_COUNT ❌
- **通过率**: $(( PASS_COUNT * 100 / TOTAL ))%

## 验证详情

### 1. MySQL数据库
- 版本: $VERSION
- 数据库: $DB_NAME
- 表数量: $TABLE_COUNT/8

### 2. 定时任务
- 服务状态: $SERVICE_STATUS
- 进程数: $PROCESS_COUNT

### 3. Flask API
- 健康状态: $HEALTH
- 设备接口: $DEVICES_CODE
- 统计接口: $STATS_CODE

### 4. 数据流测试
- MongoDB记录: $MONGO_COUNT
- MySQL统计: $STATS_COUNT

### 5. 性能测试
- 平均响应: ${AVG_TIME}ms
- 成功率: ${SUCCESS_RATE}%

## 结论

$(if [ $FAIL_COUNT -eq 0 ]; then echo "✅ 所有功能正常运行,可以交付验收"; elif [ $FAIL_COUNT -le 2 ]; then echo "⚠️ 基本功能正常,建议优化失败项"; else echo "❌ 存在关键问题,需要修复后重新验证"; fi)
EOF

echo ""
echo -e "${GREEN}报告已生成: WEEK7_VERIFICATION_REPORT.md${NC}"
