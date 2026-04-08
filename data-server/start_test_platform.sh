#!/bin/bash

echo "========================================"
echo "  数据服务器 - 前端测试平台启动器"
echo "========================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到Python3，请先安装Python3"
    exit 1
fi

echo "[信息] 正在启动数据服务器..."
echo "[信息] 服务器地址: http://localhost:5000"
echo "[信息] 测试页面: http://localhost:5000/test"
echo ""
echo "[提示] 按 Ctrl+C 可停止服务器"
echo "========================================"
echo ""

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 启动Flask应用
python3 app.py
