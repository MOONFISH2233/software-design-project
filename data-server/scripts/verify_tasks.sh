#!/bin/bash
# 第四周任务验证脚本
# 功能：验证所有任务是否完成

echo "======================================================================"
echo "                    第四周任务完成情况验证"
echo "======================================================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 计数器
TOTAL=0
PASSED=0
FAILED=0

# 检查函数
check_item() {
    TOTAL=$((TOTAL + 1))
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅${NC} $2"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}❌${NC} $2"
        FAILED=$((FAILED + 1))
    fi
}

echo "【1】检查 API 接口管理工具..."
echo "----------------------------------------------------------------------"

# 检查 Swagger 文件
if [ -f "swagger.json" ]; then
    check_item 0 "Swagger JSON 文件存在"
else
    check_item 1 "Swagger JSON 文件不存在"
fi

# 检查 Postman Collection
if [ -f "postman_collection.json" ]; then
    check_item 0 "Postman Collection 文件存在"
else
    check_item 1 "Postman Collection 文件不存在"
fi

# 检查自动化测试脚本
if [ -f "api_auto_test.py" ]; then
    check_item 0 "API 自动化测试脚本存在"
else
    check_item 1 "API 自动化测试脚本不存在"
fi

echo ""
echo "【2】检查 MQ 基础设施..."
echo "----------------------------------------------------------------------"

# 检查 MQ 工具类
if [ -f "mq_utils.py" ]; then
    check_item 0 "MQ 工具类文件存在"
else
    check_item 1 "MQ 工具类文件不存在"
fi

# 检查 Redis 依赖
if grep -q "redis" requirements.txt 2>/dev/null; then
    check_item 0 "Redis 依赖已添加"
else
    check_item 1 "Redis 依赖未添加"
fi

echo ""
echo "【3】检查专用传感器 API 接口..."
echo "----------------------------------------------------------------------"

# 检查 app.py 中是否有新的 API 路由
if grep -q "/api/sensor/skin" app.py 2>/dev/null; then
    check_item 0 "皮肤传感器 API 路由存在"
else
    check_item 1 "皮肤传感器 API 路由不存在"
fi

if grep -q "/api/sensor/environment" app.py 2>/dev/null; then
    check_item 0 "环境传感器 API 路由存在"
else
    check_item 1 "环境传感器 API 路由不存在"
fi

if grep -q "/api/device/status" app.py 2>/dev/null; then
    check_item 0 "设备状态 API 路由存在"
else
    check_item 1 "设备状态 API 路由不存在"
fi

# 检查数据目录结构
if [ -d "data/skin_sensor" ] || grep -q "sensor_dir = os.path.join" app.py 2>/dev/null; then
    check_item 0 "独立数据目录支持"
else
    check_item 1 "独立数据目录不支持"
fi

echo ""
echo "【4】检查 MQ 版模拟器..."
echo "----------------------------------------------------------------------"

# 检查模拟器文件
if [ -f "simulator_mq.py" ]; then
    check_item 0 "MQ 版模拟器文件存在"
else
    check_item 1 "MQ 版模拟器文件不存在"
fi

# 检查重传机制
if grep -q "retry" simulator_mq.py 2>/dev/null; then
    check_item 0 "重传机制已实现"
else
    check_item 1 "重传机制未实现"
fi

# 检查 MQ 发布
if grep -q "publish" simulator_mq.py 2>/dev/null; then
    check_item 0 "MQ 发布功能已实现"
else
    check_item 1 "MQ 发布功能未实现"
fi

echo ""
echo "【5】检查服务器 MQ 模块..."
echo "----------------------------------------------------------------------"

# 检查接收模块
if [ -f "module_receiver.py" ]; then
    check_item 0 "数据接收模块存在"
else
    check_item 1 "数据接收模块不存在"
fi

# 检查验证模块
if [ -f "module_validator.py" ]; then
    check_item 0 "数据验证模块存在"
else
    check_item 1 "数据验证模块不存在"
fi

# 检查写入模块
if [ -f "module_writer.py" ]; then
    check_item 0 "数据写入模块存在"
else
    check_item 1 "数据写入模块不存在"
fi

# 检查日志模块
if [ -f "module_logger.py" ]; then
    check_item 0 "日志记录模块存在"
else
    check_item 1 "日志记录模块不存在"
fi

echo ""
echo "【6】检查启动和测试工具..."
echo "----------------------------------------------------------------------"

# 检查一键启动脚本
if [ -f "start_all.bat" ]; then
    check_item 0 "Windows 一键启动脚本存在"
else
    check_item 1 "Windows 一键启动脚本不存在"
fi

if [ -f "start_all_modules.py" ]; then
    check_item 0 "Python 启动脚本存在"
else
    check_item 0 "Python 启动脚本不存在"
fi

# 检查测试脚本
if [ -f "test_api.bat" ]; then
    check_item 0 "API 测试脚本存在"
else
    check_item 1 "API 测试脚本不存在"
fi

if [ -f "manual_test.bat" ]; then
    check_item 0 "手动测试脚本存在"
else
    check_item 1 "手动测试脚本不存在"
fi

echo ""
echo "【7】检查文档..."
echo "----------------------------------------------------------------------"

# 检查文档文件
DOC_FILES=("IMPLEMENTATION_SUMMARY.md" "QUICK_REFERENCE.md" "WEEK4_TASK_GUIDE.md" "COMMAND_GUIDE.md")
for doc in "${DOC_FILES[@]}"; do
    if [ -f "$doc" ]; then
        check_item 0 "文档 $doc 存在"
    else
        check_item 1 "文档 $doc 不存在"
    fi
done

echo ""
echo "======================================================================"
echo "                         验证结果汇总"
echo "======================================================================"
echo ""
echo "总检查项：$TOTAL"
echo -e "通过：${GREEN}$PASSED${NC}"
echo -e "失败：${RED}$FAILED${NC}"
echo "完成率：$(echo "scale=2; $PASSED * 100 / $TOTAL" | bc)%"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 所有任务已完成！${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  还有 $FAILED 项任务未完成${NC}"
    exit 1
fi
