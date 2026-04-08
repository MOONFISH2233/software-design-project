# 第四周任务完成指南

## 📋 任务概述

本周任务主要包含以下四个部分：

1. ✅ **API 接口管理工具** - 录入 API 文档并测试
2. ✅ **数据服务器扩展** - 基于 AI 实现多个独立接口
3. 🔄 **模拟器 MQ 改造** - 面向消息队列模式 + 重传机制
4. 🏗️ **服务器架构改造** - 模块化 MQ 架构

---

## 🎯 已完成的工作

### 1. API 接口管理工具

#### 生成的文件：
- `swagger.json` - OpenAPI 3.0 标准定义文件
- `postman_collection.json` - Postman 集合文件
- `api_auto_test.py` - 自动化测试脚本

#### 使用方法：

##### 方法 1：导入到 Postman
1. 打开 Postman
2. 点击 "Import"
3. 选择 `postman_collection.json`
4. 在 Collection 中找到 "Flask 数据服务器 API"
5. 修改环境变量 `base_url` 为你的服务器地址
6. 逐个点击接口进行测试

##### 方法 2：导入到 Swagger UI
1. 访问 https://editor.swagger.io/
2. 点击 "Import URL or File"
3. 上传 `swagger.json`
4. 在线查看和测试 API

##### 方法 3：运行自动化测试脚本
```bash
# 测试本地服务器
python api_auto_test.py http://localhost:5000

# 测试远程服务器
python api_auto_test.py http://47.103.108.47:5000
```

测试报告会保存为 `api_test_report_YYYYMMDD_HHMMSS.json`

---

### 2. 消息队列基础设施

#### 生成的文件：
- `mq_utils.py` - 消息队列工具类（支持 Redis 和 RabbitMQ）
- `requirements.txt` - 已添加依赖

#### 安装依赖：
```bash
pip install -r requirements.txt
```

#### 选择消息队列：

**方案 A：Redis（推荐）**
- 优点：轻量级、易部署、性能好
- 安装：https://redis.io/download
- Windows 可用 WSL 或 Docker 运行

**方案 B：RabbitMQ**
- 优点：功能强大、可靠性高
- 安装：https://www.rabbitmq.com/download.html

---

## 📝 下一步实施计划

### 第 3 步：扩展数据服务器 API（进行中）

将创建以下专用接口：
- `/api/sensor/skin` - 皮肤传感器数据
- `/api/sensor/environment` - 环境传感器数据
- `/api/device/status` - 设备状态数据

每个接口的数据会写入独立的文件目录。

### 第 4 步：改造模拟器为 MQ 客户端

改造 `simulator.py`：
- 引入消息队列发布功能
- 添加重传机制（失败重试队列）
- 实现超时检测和错误处理

### 第 5 步：实现服务器端 MQ 模块

创建 4 个独立模块：

1. **接收模块** (`module_receiver.py`)
   - 从 MQ 读取数据
   - 初步格式检查
   - 发布到验证队列

2. **验证模块** (`module_validator.py`)
   - 验证数据合理性
   - 过滤无效数据
   - 发布到写入队列

3. **写入模块** (`module_writer.py`)
   - 按传感器类型写入不同文件
   - 支持并发写入
   - 文件轮转

4. **日志模块** (`module_logger.py`)
   - 记录所有操作
   - 异常告警
   - 性能统计

---

## 🚀 快速开始

### 1. 安装依赖
```bash
cd data-server
pip install -r requirements.txt
```

### 2. 启动 Redis（以 Redis 为例）
```bash
# Windows (使用 WSL 或 Docker)
docker run -d -p 6379:6379 redis:latest

# 或使用 Windows 版本
redis-server.exe
```

### 3. 测试当前服务器
```bash
# 启动 Flask 服务器
python app.py

# 新开一个终端，运行自动化测试
python api_auto_test.py http://localhost:5000
```

### 4. 使用 Postman 测试
1. 打开 Postman
2. 导入 `postman_collection.json`
3. 发送请求测试各个接口

---

## 📊 架构图

### 当前架构（HTTP 直连）
```
┌─────────────┐      HTTP       ┌──────────────┐
│  Simulator  │ ───────────────→ │  Flask App   │
│  (客户端)    │                 │  (单体应用)   │
└─────────────┘                 └──────────────┘
```

### 目标架构（MQ 异步）
```
┌─────────────┐      Publish      ┌──────────────┐
│  Simulator  │ ─────────────────→│     MQ       │
│  + 重传机制  │                   │ (Redis/RabbitMQ)│
└─────────────┘                   └──────┬───────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
              Subscribe            Subscribe            Subscribe
                    │                    │                    │
                    ▼                    ▼                    ▼
         ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
         │  接收模块        │ │  验证模块        │ │  写入模块        │
         │  (Receiver)      │ │  (Validator)     │ │  (Writer)        │
         │  ×N 实例         │ │  ×N 实例         │ │  ×N 实例         │
         └──────────────────┘ └──────────────────┘ └──────────────────┘
```

---

## 🔧 配置文件说明

### MQ 配置示例（config.yaml）
```yaml
mq:
  type: redis  # 或 rabbitmq
  host: localhost
  port: 6379
  db: 0

streams:
  raw_data: "sensor:raw"           # 原始数据流
  validated_data: "sensor:validated"  # 验证后数据流
  
queues:
  retry_queue: "retry"             # 重传队列
  log_queue: "logs"                # 日志队列

server:
  modules:
    receiver:
      enabled: true
      instances: 2
    validator:
      enabled: true
      instances: 1
    writer:
      enabled: true
      instances: 2
    logger:
      enabled: true
      instances: 1
```

---

## 📁 项目结构

```
data-server/
├── app.py                      # Flask 主应用（当前版本）
├── mq_utils.py                 # MQ 工具类 ✨ 新增
├── api_auto_test.py            # API 自动化测试 ✨ 新增
├── swagger.json                # OpenAPI 定义 ✨ 新增
├── postman_collection.json     # Postman 集合 ✨ 新增
├── requirements.txt            # 依赖包（已更新）
├── module_receiver.py          # 接收模块 ⏳ 待创建
├── module_validator.py         # 验证模块 ⏳ 待创建
├── module_writer.py            # 写入模块 ⏳ 待创建
├── module_logger.py            # 日志模块 ⏳ 待创建
├── simulator_mq.py             # MQ 版模拟器 ⏳ 待创建
├── config.yaml                 # 配置文件 ⏳ 待创建
├── logs/                       # 日志目录
└── data/                       # 数据目录
    ├── skin_sensor/            # 皮肤传感器数据 ⏳ 待创建
    ├── environment/            # 环境传感器数据 ⏳ 待创建
    └── device/                 # 设备状态数据 ⏳ 待创建
```

---

## ✅ 验收标准

### 任务 1：API 接口管理
- [x] 生成 Swagger JSON 文件
- [x] 生成 Postman Collection
- [x] 创建自动化测试脚本
- [ ] 完成所有接口测试（需先启动服务器）

### 任务 2：数据服务器扩展
- [x] 设计新的 API 路由
- [ ] 实现专用传感器接口
- [ ] 每个接口数据写入独立文件

### 任务 3：模拟器 MQ 改造
- [ ] 改造成 MQ 发布模式
- [ ] 实现重传机制
- [ ] 添加超时和错误处理

### 任务 4：服务器 MQ 架构
- [ ] 实现接收模块
- [ ] 实现验证模块
- [ ] 实现写入模块
- [ ] 实现日志模块
- [ ] 模块可独立启停
- [ ] 可启动多个实例

---

## 💡 提示

1. **开发顺序建议**：
   - 先测试当前 HTTP 版本确保基础功能正常
   - 逐步添加 MQ 功能
   - 最后切换到纯 MQ 架构

2. **调试技巧**：
   - 使用 Redis Desktop Manager 查看 Redis Stream
   - 开启详细日志记录
   - 分模块测试，确保每个模块独立工作

3. **性能优化**：
   - 调整 MQ 预取数量控制并发
   - 使用连接池减少连接开销
   - 批量写入提高 I/O 效率

---

## 📞 需要帮助？

如果在实施过程中遇到问题：
1. 检查日志输出
2. 查看测试报告
3. 确认 MQ 服务正常运行
4. 验证配置文件参数

继续下一步实施，请告诉我！ 🚀
