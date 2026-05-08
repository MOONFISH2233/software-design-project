a#!/bin/bash
# =====================================================
# 项目文件整理脚本 - 第八周
# 功能: 整理data-server目录结构,归类文件到对应文件夹
# =====================================================

echo "=========================================="
echo "开始整理项目文件结构..."
echo "=========================================="

PROJECT_DIR="/root/course-project/week8/data-server"

# 创建必要的目录
echo "1. 创建目录结构..."
mkdir -p $PROJECT_DIR/{config,routes,tasks,tests,scripts,docs,examples,backups,security,static}

# 移动配置文件
echo "2. 整理配置文件..."
mv $PROJECT_DIR/gunicorn_config.py $PROJECT_DIR/config/ 2>/dev/null
mv $PROJECT_DIR/*.json $PROJECT_DIR/config/ 2>/dev/null

# 移动路由文件
echo "3. 整理路由文件..."
find $PROJECT_DIR -maxdepth 1 -name "*routes*.py" -exec mv {} $PROJECT_DIR/routes/ \; 2>/dev/null

# 移动任务文件
echo "4. 整理任务文件..."
find $PROJECT_DIR -maxdepth 1 -name "*statistics*.py" -o -name "*task*.py" | xargs -I {} mv {} $PROJECT_DIR/tasks/ 2>/dev/null

# 移动测试文件
echo "5. 整理测试文件..."
find $PROJECT_DIR -maxdepth 1 -name "*test*.py" -o -name "*verify*.py" -o -name "*check*.py" | xargs -I {} mv {} $PROJECT_DIR/tests/ 2>/dev/null
mv $PROJECT_DIR/jmeter_test.jmx $PROJECT_DIR/tests/ 2>/dev/null

# 移动脚本文件
echo "6. 整理脚本文件..."
find $PROJECT_DIR -maxdepth 1 -name "*.sh" -o -name "*.bat" -o -name "deploy*.py" -o -name "init_*.sql" | xargs -I {} mv {} $PROJECT_DIR/scripts/ 2>/dev/null

# 移动文档文件
echo "7. 整理文档文件..."
find $PROJECT_DIR -maxdepth 1 -name "*.md" -o -name "*.txt" -o -name "*.docx" | xargs -I {} mv {} $PROJECT_DIR/docs/ 2>/dev/null

# 移动示例文件
echo "8. 整理示例文件..."
find $PROJECT_DIR -maxdepth 1 -name "*simulator*.py" -o -name "*example*.py" | xargs -I {} mv {} $PROJECT_DIR/examples/ 2>/dev/null

# 移动备份文件
echo "9. 整理备份文件..."
find $PROJECT_DIR -maxdepth 1 -name "*backup*" -o -name "*fix*.py" -o -name "*old*" | xargs -I {} mv {} $PROJECT_DIR/backups/ 2>/dev/null

# 移动安全相关文件
echo "10. 整理安全文件..."
mv $PROJECT_DIR/api_keys.json $PROJECT_DIR/security/ 2>/dev/null
mv $PROJECT_DIR/users.json $PROJECT_DIR/security/ 2>/dev/null

# 移动静态文件
echo "11. 整理静态文件..."
find $PROJECT_DIR -maxdepth 1 -name "*.html" -o -name "*.css" -o -name "*.js" | xargs -I {} mv {} $PROJECT_DIR/static/ 2>/dev/null

# 删除空文件和无效文件
echo "12. 清理无效文件..."
find $PROJECT_DIR -maxdepth 1 -name "nul" -delete 2>/dev/null
find $PROJECT_DIR -maxdepth 1 -empty -type f -delete 2>/dev/null

echo ""
echo "=========================================="
echo "文件整理完成！"
echo "=========================================="
echo ""
echo "当前目录结构:"
tree -L 2 $PROJECT_DIR -I '__pycache__|*.pyc|.git' || ls -la $PROJECT_DIR

echo ""
echo "建议的后续操作:"
echo "1. 检查移动的文件是否正确"
echo "2. 更新import路径（如有必要）"
echo "3. 测试应用是否正常运行"
echo "4. 提交到Git仓库"
