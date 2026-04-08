# 长期记忆

## 项目信息

- **项目**：软件设计课程作业，位于 `d:\学习\软件设计\`
- **GitHub 仓库**：https://github.com/MOONFISH2233/software-design-project
- **服务器 IP**：47.103.108.47，端口 5000（Flask）
- **MQ（Redis）地址**：47.103.108.47:6379

## 项目结构要点

- `data-server/app.py`：Flask 服务器，含3个传感器专用接口（skin/environment/device），各自写入独立子目录
- `data-server/swagger.json`：OpenAPI 3.0 API 文档，含7个路由
- `data-server/postman_collection.json`：Postman 集合，8个请求，分组整理
- `data-server/api_auto_test.py`：自动化测试脚本，含全部7个接口测试
- `data-server/mq_utils.py`：MQ工具类，支持Redis和RabbitMQ
- `data-server/module_receiver/validator/writer/logger.py`：MQ四模块，支持独立启停
- `data-server/simulator_mq.py`：MQ版模拟器，含重传机制（RetryThread）
- `data-server/start_all_modules.py`：一键启动脚本，支持 --host/--port/--no-simulator
- `data-server/verify_local.py`：本地验证脚本，73项检查，98.6%通过率

## 第四周任务完成情况（2026-04-01）

- 任务1（API接口管理工具）：✅ 完成
- 任务2（数据服务器独立接口，AI读文档实现）：✅ 完成
- 任务3（模拟器MQ改造+重传机制）：✅ 完成
- 任务4（服务器MQ模块化架构）：✅ 完成

## 技术约定

- Windows 环境，PowerShell，使用 `python -X utf8` 运行脚本避免编码问题
- 数据写入路径：`data/skin_sensor/`、`data/environment/`、`data/device/`
