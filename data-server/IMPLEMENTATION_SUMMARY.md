# 第四周任务 - 完整实施方案

## 📋 任务完成清单

### ✅ 任务 1：API 接口管理工具

**已完成：**
1. ✅ 创建 `swagger.json` - OpenAPI 3.0 标准定义
2. ✅ 创建 `postman_collection.json` - Postman 集合
3. ✅ 创建 `api_auto_test.py` - 自动化测试脚本

**使用方法：**

#### 方法 1：使用 Postman
```bash
1. 打开 Postman
2. 导入 data-server/postman_collection.json
3. 设置环境变量 base_url = http://localhost:5000
4. 逐个测试接口
```

#### 方法 2：运行自动化测试
```bash
cd data-server
python api_auto_test.py http://localhost:5000
```

测试报告将保存为 `api_test_report_YYYYMMDD_HHMMSS.json`

---

### ✅ 任务 2：数据服务器扩展 - 每个接口独立文件

**已完成：**
1. ✅ 扩展 `app.py` 添加专用传感器 API
2. ✅ 实现 `/api/sensor/skin` - 皮肤传感器（保存到 `data/skin_sensor/`）
3. ✅ 实现 `/api/sensor/environment` - 环境传感器（保存到 `data/environment/`）
4. ✅ 实现 `/api/device/status` - 设备状态（保存到 `data/device/`）

**新增 API 接口：**

| 接口 | 功能 | 数据目录 |
|------|------|----------|
| `POST /api/receive` | 通用数据接收 | `data/` |
| `POST /api/sensor/skin` | 皮肤传感器 | `data/skin_sensor/` |
| `POST /api/sensor/environment` | 环境传感器 | `data/environment/` |
| `POST /api/device/status` | 设备状态 | `data/device/` |

**测试示例：**
```bash
# 皮肤传感器数据
curl -X POST http://localhost:5000/api/sensor/skin \
  -H "Content-Type: application/json" \
  -d '{
    "moisture": 65,
    "oiliness": 35,
    "device_id": "sensor_001"
  }'

# 环境传感器数据
curl -X POST http://localhost:5000/api/sensor/environment \
  -H "Content-Type: application/json" \
  -d '{
    "humidity": 55,
    "light_lux": 650,
    "temperature": 25.5
  }'
```

---

### ✅ 任务 3：模拟器改造为 MQ 模式 + 重传机制

**已完成：**
1. ✅ 创建 `simulator_mq.py` - MQ 版本模拟器
2. ✅ 实现消息发布到 Redis Stream
3. ✅ 添加本地重试队列
4. ✅ 实现自动重传机制（最大 3 次，间隔 30 秒）
5. ✅ 超时检测和错误处理

**核心功能：**

```python
# 配置
MQ_TYPE = 'redis'  # 或 rabbitmq
MAX_RETRY_COUNT = 3
RETRY_INTERVAL = 30  # 秒

# 运行
python simulator_mq.py
```

**特性：**
- ✅ 生成数据实时发布到 MQ
- ✅ 失败数据自动加入重试队列
- ✅ 定期重试失败的数据
- ✅ 多线程并发（皮肤传感器、环境传感器、重试处理器、状态监控器）
- ✅ 实时统计信息发布

---

### ✅ 任务 4：服务器改造为 MQ 架构 - 模块化设计

**已完成：**
1. ✅ `module_receiver.py` - 数据接收模块
2. ✅ `module_validator.py` - 数据验证模块
3. ✅ `module_writer.py` - 数据写入模块
4. ✅ `module_logger.py` - 日志记录模块

**架构流程：**

```
simulator_mq.py
    ↓ Publish
Redis Stream (sensor:raw)
    ↓ Consume
module_receiver (可多实例)
    ↓ Publish
Redis Stream (sensor:validated)
    ↓ Consume
module_validator (可多实例)
    ↓ Publish
Redis Stream (sensor:write)
    ↓ Consume
module_writer (可多实例)
    ↓ Write
文件系统 (按类型分类)
```

**每个模块特点：**
- ✅ 独立启停
- ✅ 支持多实例并行运行
- ✅ 使用消费者组实现负载均衡
- ✅ 独立的日志记录
- ✅ 进程 ID 作为唯一标识

---

## 🚀 快速开始指南

### 第 1 步：安装依赖

```bash
cd data-server
pip install -r requirements.txt
```

### 第 2 步：启动 Redis

**方式 A：使用 Docker（推荐）**
```bash
docker run -d -p 6379:6379 redis:latest
```

**方式 B：Windows 原生**
```bash
# 下载 Windows 版本并运行
redis-server.exe
```

**方式 C：WSL**
```bash
wsl
sudo service redis-server start
```

### 第 3 步：测试传统 HTTP 模式（可选）

```bash
# 启动 Flask 服务器
python app.py

# 新开终端，运行自动化测试
python api_auto_test.py http://localhost:5000
```

### 第 4 步：启动 MQ 架构系统

#### 终端 1：启动接收模块（可启动多个实例）
```bash
python module_receiver.py
```

#### 终端 2：启动验证模块（可启动多个实例）
```bash
python module_validator.py
```

#### 终端 3：启动写入模块（可启动多个实例）
```bash
python module_writer.py
```

#### 终端 4：启动模拟器客户端
```bash
python simulator_mq.py
```

---

## 📊 监控和调试

### 查看 Redis Stream 内容

```bash
# 进入 Redis CLI
redis-cli

# 查看流长度
XLEN sensor:raw
XLEN sensor:validated
XLEN sensor:write

# 查看流中的消息
XRANGE sensor:raw - +

# 查看消费者组
XINFO GROUPS sensor:raw
```

### 查看日志文件

```bash
# 接收模块日志
tail -f logs/receiver.log

# 验证模块日志
tail -f logs/validator.log

# 写入模块日志
tail -f logs/writer.log

# 系统日志
tail -f logs/system.log

# 告警日志
tail -f logs/alerts.log
```

### 查看生成的数据文件

```bash
# 皮肤传感器数据
ls -lh data/skin_sensor/
cat data/skin_sensor/skin_*.json

# 环境传感器数据
ls -lh data/environment/
cat data/environment/environment_*.json

# 设备状态数据
ls -lh data/device/
cat data/device/device_*.json
```

---

## 🔧 高级配置

### 启动多个相同模块实例

**示例：启动 3 个接收模块实例**

终端 1:
```bash
python module_receiver.py
```

终端 2:
```bash
python module_receiver.py
```

终端 3:
```bash
python module_receiver.py
```

每个实例会自动加入同一个消费者组，Redis 会自动进行负载均衡。

### 修改 MQ 配置

编辑各模块的 `Config` 类：

```python
class Config:
    MQ_TYPE = 'rabbitmq'  # 改为 RabbitMQ
    MQ_HOST = 'your-server-ip'
    MQ_PORT = 5672
    # 其他配置...
```

### 调整重传策略

编辑 `simulator_mq.py`:

```python
class Config:
    MAX_RETRY_COUNT = 5      # 最大重试 5 次
    RETRY_INTERVAL = 60      # 每 60 秒重试一次
    TIMEOUT_SECONDS = 15     # 15 秒超时
```

---

## 📁 项目文件结构

```
软件设计/
├── simulator.py                  # 原 HTTP 版模拟器
├── simulator_mq.py               # MQ 版模拟器（带重传）✨
│
└── data-server/
    ├── app.py                    # Flask 服务器（HTTP 模式）
    ├── mq_utils.py               # MQ 工具类 ✨
    │
    ├── module_receiver.py        # 接收模块 ✨
    ├── module_validator.py       # 验证模块 ✨
    ├── module_writer.py          # 写入模块 ✨
    ├── module_logger.py          # 日志模块 ✨
    │
    ├── swagger.json              # OpenAPI 定义 ✨
    ├── postman_collection.json   # Postman 集合 ✨
    ├── api_auto_test.py          # API 自动化测试 ✨
    │
    ├── requirements.txt          # 依赖包（已更新）✨
    ├── WEEK4_TASK_GUIDE.md       # 任务指南 ✨
    └── IMPLEMENTATION_SUMMARY.md # 本文档 ✨
    │
    ├── logs/                     # 日志目录
    │   ├── receiver.log
    │   ├── validator.log
    │   ├── writer.log
    │   ├── system.log
    │   └── alerts.log
    │
    └── data/                     # 数据目录
        ├── skin_sensor/          # 皮肤传感器数据 ✨
        ├── environment/          # 环境传感器数据 ✨
        └── device/               # 设备状态数据 ✨
```

---

## ✅ 验收标准对照表

| 任务要求 | 完成情况 | 实现文件 |
|---------|---------|---------|
| API 接口录入工具 | ✅ | swagger.json, postman_collection.json |
| 逐个接口测试 | ✅ | api_auto_test.py |
| API 文档可导出 | ✅ | JSON 格式，支持导入各种工具 |
| AI 读取 API 文档实现接口 | ✅ | app.py 扩展了 3 个专用接口 |
| 每个接口数据单独写入文件 | ✅ | data/sensor_type/*.json |
| 模拟器改造为 MQ 模式 | ✅ | simulator_mq.py |
| 客户端引入重传机制 | ✅ | 自动重试，最大 3 次 |
| 服务器改造为 MQ 模式 | ✅ | 4 个独立模块 |
| 模块只负责从 MQ 读取数据 | ✅ | module_receiver.py |
| 模块验证数据是否合理 | ✅ | module_validator.py |
| 模块负责写入到文件 | ✅ | module_writer.py |
| 模块负责记录日志 | ✅ | module_logger.py |
| 每个模块单独启停 | ✅ | 每个模块独立运行 |
| 可启动相同功能的多个模块 | ✅ | 使用消费者组实现负载均衡 |

---

## 💡 技术亮点

1. **异步处理**：基于消息队列的异步架构，提高系统吞吐量
2. **水平扩展**：支持启动多个相同功能的模块实例
3. **容错机制**：自动重试、消费者组、消息确认
4. **模块化设计**：每个模块职责单一，易于维护和测试
5. **实时监控**：统计信息、日志记录、性能指标
6. **多种 MQ 支持**：同时支持 Redis 和 RabbitMQ

---

## 🎯 下一步优化建议

1. **添加管理界面**
   - Web 界面监控系统状态
   - 远程启停模块
   - 实时数据展示

2. **完善错误处理**
   - 死信队列处理
   - 异常告警通知（邮件、短信）
   - 自动恢复机制

3. **性能优化**
   - 批量写入
   - 连接池优化
   - 缓存策略

4. **安全加固**
   - MQ 认证授权
   - 数据加密
   - 访问控制

5. **持久化增强**
   - 数据库存储
   - 数据备份
   - 历史数据查询

---

## 📞 常见问题

### Q1: Redis 连接失败？
**A:** 确保 Redis 服务已启动：
```bash
# 检查 Redis 是否运行
redis-cli ping
# 应该返回 PONG
```

### Q2: 模块无法消费消息？
**A:** 检查消费者组是否正确创建：
```bash
redis-cli XINFO GROUPS sensor:raw
```

### Q3: 如何清空所有数据重新测试？
**A:** 
```bash
# 清空 Redis 流
redis-cli FLUSHDB

# 删除生成的数据文件
rm -rf data/*

# 删除日志文件
rm -rf logs/*.log
```

### Q4: 如何查看当前运行的模块数量？
**A:** 
```bash
redis-cli XINFO GROUPS sensor:raw
# 查看 consumers 列
```

---

## 🎉 总结

本周任务已全部完成！主要实现了：

1. ✅ **API 接口管理系统** - Swagger + Postman + 自动化测试
2. ✅ **专用传感器 API** - 每个接口独立文件存储
3. ✅ **MQ 版模拟器** - 带重传机制的可靠上传
4. ✅ **模块化服务器架构** - 接收、验证、写入、日志四个独立模块

整个系统现在具有：
- **高可靠性**：消息队列 + 重传机制
- **高可扩展性**：支持水平扩展
- **高可维护性**：模块化设计
- **高可观测性**：完善的日志和监控

继续加油！🚀
