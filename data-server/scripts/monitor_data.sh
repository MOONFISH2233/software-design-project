#!/bin/bash
# 实时数据监控脚本 - Shell版本
# 用法: ./monitor_data.sh [刷新间隔秒数]

INTERVAL=${1:-2}
DATA_DIR="/root/course-project/week5/data-server/data-server/data"

echo "======================================================================"
echo "  实时数据监控器"
echo "======================================================================"
echo "📁 监控目录: $DATA_DIR"
echo "⏱️  刷新间隔: ${INTERVAL}秒"
echo "📊 按 Ctrl+C 停止"
echo ""

LAST_COUNT=0

while true; do
    # 统计当前文件数量
    CURRENT_COUNT=$(ls "$DATA_DIR"/*.json 2>/dev/null | wc -l)
    
    if [ $CURRENT_COUNT -gt $LAST_COUNT ]; then
        NEW_FILES=$((CURRENT_COUNT - LAST_COUNT))
        TIMESTAMP=$(date '+%H:%M:%S')
        
        echo ""
        echo "✅ [$TIMESTAMP] 新增 $NEW_FILES 条数据 (总计: $CURRENT_COUNT)"
        
        # 显示最新的3个文件内容
        ls -t "$DATA_DIR"/*.json 2>/dev/null | head -3 | while read file; do
            echo "   📄 $(basename $file):"
            python3 -c "
import json
with open('$file', 'r') as f:
    data = json.load(f)
if data.get('sensor_type') == 'skin':
    d = data['data']
    print(f\"      💧水分:{d.get('moisture')}% | 🛢️油分:{d.get('oiliness')}% | 🌡️温度:{d.get('temperature')}°C\")
else:
    print(f\"      类型:{data.get('sensor_type')}\")
" 2>/dev/null
        done
        
        LAST_COUNT=$CURRENT_COUNT
    else
        echo -ne "\r⏳ 已有 $CURRENT_COUNT 条数据，等待新数据... (${INTERVAL}s后刷新)"
    fi
    
    sleep $INTERVAL
done
