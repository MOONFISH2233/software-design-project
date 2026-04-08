@echo off
REM ====================================
REM 推送第四周任务代码到 GitHub
REM ====================================

echo.
echo ======================================================================
echo                    推送第四周任务代码到 GitHub
echo ======================================================================
echo.

set BRANCH_NAME=week4-mq-architecture

echo 当前分支：%BRANCH_NAME%
echo.

REM 检查是否有未提交的更改
git status >nul 2>&1
if errorlevel 1 (
    echo [错误] 当前目录不是 Git 仓库
    echo 请先运行：git init
    pause
    exit /b 1
)

echo [1/5] 添加所有新文件...
git add -A
echo      ✅ 文件已添加到暂存区
echo.

echo [2/5] 提交更改...
git commit -m "feat: 完成第四周任务 - MQ 架构改造和 API 管理

主要更新:
- API 接口管理工具 (Swagger + Postman)
- 专用传感器 API 接口实现
- 模拟器 MQ 改造 + 重传机制
- 服务器 MQ 架构改造 (4 个独立模块)
- 一键启动脚本和测试工具
- 完整的文档和使用指南

新增文件:
- swagger.json, postman_collection.json
- api_auto_test.py, mq_utils.py
- simulator_mq.py
- module_receiver.py, module_validator.py
- module_writer.py, module_logger.py
- start_all.bat, test_api.bat 等工具脚本
- 完整的使用文档

技术栈:
- Redis Stream / RabbitMQ
- 消息队列异步处理
- 消费者组负载均衡
- 自动重试机制"

if errorlevel 1 (
    echo      ⚠️ 没有需要提交的更改或提交失败
) else (
    echo      ✅ 提交成功
)
echo.

echo [3/5] 创建并切换到新分支...
git branch %BRANCH_NAME% 2>nul
git checkout %BRANCH_NAME%
echo      ✅ 已切换到分支 %BRANCH_NAME%
echo.

echo [4/5] 推送到远程仓库...
echo      正在推送到 origin/%BRANCH_NAME%...
git push -u origin %BRANCH_NAME%

if errorlevel 1 (
    echo.
    echo [错误] 推送失败
    echo 请检查网络连接和 GitHub 权限
    pause
    exit /b 1
) else (
    echo      ✅ 推送成功！
)
echo.

echo [5/5] 查看状态...
git status
echo.

echo ======================================================================
echo                         推送完成！
echo ======================================================================
echo.
echo 分支名称：%BRANCH_NAME%
echo.
echo 下一步操作:
echo   1. 在 GitHub 上创建 Pull Request
echo   2. 审查代码变更
echo   3. 合并到主分支
echo.
echo GitHub 仓库：https://github.com/MOONFISH2233/software-design-project
echo.
pause
