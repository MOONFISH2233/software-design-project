@echo off
REM =====================================================
REM Git提交和推送脚本 - 第八周任务
REM 功能: 提交代码到week8分支并推送到GitHub
REM =====================================================

echo ==========================================
echo 开始提交第八周任务代码...
echo ==========================================
echo.

cd /d "%~dp0"

REM 1. 检查当前分支
echo [1/6] 检查Git状态...
git status

REM 2. 切换到week8分支（如果不存在则创建）
echo.
echo [2/6] 切换到week8分支...
git checkout week8 2>nul
if errorlevel 1 (
    echo 创建week8分支...
    git checkout -b week8
)

REM 3. 添加所有文件
echo.
echo [3/6] 添加文件到暂存区...
git add .

REM 4. 提交变更
echo.
echo [4/6] 提交变更...
git commit -m "feat: 完成第八周任务 - 小程序功能规划、数据库设计、定时任务、Flask接口开发

- 新增小程序功能思维导图 (docs/WEEK8_MINIPROGRAM_PLAN.md)
- 完善数据库设计至15个表 (scripts/init_mysql_week8.sql)
- 更新models.py添加10个新表模型
- 实现miniprogram_routes.py提供14个API接口
- 创建PowerDesigner使用教程 (docs/POWERDESIGNER_TUTORIAL.md)
- 项目文件整理脚本 (scripts/organize_project.sh)
- 第八周任务完成总结 (docs/WEEK8_COMPLETION_SUMMARY.md)"

REM 5. 推送到GitHub
echo.
echo [5/6] 推送到GitHub...
git push origin week8

REM 6. 显示结果
echo.
echo [6/6] 完成！
echo.
echo ==========================================
echo 提交成功！
echo ==========================================
echo.
echo 下一步操作:
echo 1. 在GitHub上创建Pull Request合并到主分支
echo 2. SSH登录服务器同步代码
echo 3. 执行数据库初始化脚本
echo 4. 重启应用服务
echo.
pause
