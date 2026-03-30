# 🚀 第四周任务 - 快速参考卡片

## 📌 一分钟速览

### 任务完成情况
- ✅ **API 接口管理** - Swagger + Postman + 自动化测试
- ✅ **专用 API 实现** - 每个传感器独立接口和文件
- ✅ **MQ 模拟器** - 带重传机制的消息队列模式
- ✅ **模块化服务器** - 接收、验证、写入、日志四个模块

---

## 🔥 快速开始（3 步）

### Step 1: 安装依赖
```bash
cd data-server
pip install -r requirements.txt
```

### Step 2: 启动 Redis
```bash
docker run -d -p 6379:6379 redis:latest
```

### Step 3: 启动系统
```bash
# 方式 A: 一键启动所有模块
python start_all_modules.py

# 方式 B: 分模块手动启动
python module_receiver.py   # 终端 1
python module_validator.py  # 终端 2
python module_writer.py     # 终端 3
python simulator_mq.py      # 终端 4
```

---

## 📡 API 接口速查

| 接口 | 方法 | 功能 | 示例 |
|------|------|------|------|
| `/api/receive` | POST | 通用数据接收 | `curl -X POST localhost:5000/api/receive -d '{"data":{...}}'` |
| `/api/sensor/skin` | POST | 皮肤传感器 | `curl -X POST localhost:5000/api/sensor/skin -d '{"moisture":65,"oiliness":35}'` |
| `/api/sensor/environment` | POST | 环境传感器 | `curl -X POST localhost:5000/api/sensor/environment -d '{"humidity":55,"light_lux":650}'` |
| `/api/device/status` | POST | 设备状态 | `curl -X POST localhost:5000/api/device/status -d '{"device_id":"dev_001","status":"online"}'` |
| `/api/health` | GET | 健康检查 | `curl localhost:5000/api/health` |
| `/api/logs` | GET | 查看日志 | `curl localhost:5000/api/logs` |
| `/api/stats` | GET | 统计信息 | `curl localhost:5000/api/stats` |

---

## 🧪 测试命令

### 自动化测试
```bash
python api_auto_test.py http://localhost:5000
```

### 手动测试单个接口
```bash
# 皮肤传感器
curl -X POST http://localhost:5000/api/sensor/skin \
  -H "Content-Type: application/json" \
  -d '{"moisture": 65, "oiliness": 35, "device_id": "sensor_001"}'

# 环境传感器
curl -X POST http://localhost:5000/api/sensor/environment \
  -H "Content-Type: application/json" \
  -d '{"humidity": 55, "light_lux": 650, "temperature": 25.5}'
```

### Postman 测试
1. 导入 `postman_collection.json`
2. 设置变量 `base_url = http://localhost:5000`
3. 点击发送

---

## 📂 文件结构速查

```
data-server/
├── app.py                      # Flask 服务器（HTTP 模式）
├── mq_utils.py                 # MQ 工具类
│
├── module_receiver.py          # 接收模块
├── module_validator.py         # 验证模块
├── module_writer.py            # 写入模块
├── module_logger.py            # 日志模块
│
├── simulator_mq.py             # MQ 版模拟器
├── start_all_modules.py        # 一键启动脚本
│
├── swagger.json                # OpenAPI 定义
├── postman_collection.json     # Postman 集合
├── api_auto_test.py            # 自动化测试
│
└── logs/                       # 日志目录
└── data/                       # 数据目录
    ├── skin_sensor/            # 皮肤传感器
    ├── environment/            # 环境传感器
    └── device/                 # 设备状态
```

---

## 🔍 监控和调试

### 查看 Redis Stream
```bash
redis-cli

# 查看流长度
XLEN sensor:raw
XLEN sensor:validated
XLEN sensor:write

# 查看消息
XRANGE sensor:raw - +

# 查看消费者组
XINFO GROUPS sensor:raw
```

### 查看实时日志
```bash
# 所有日志
tail -f logs/*.log

# 单个模块日志
tail -f logs/receiver.log
tail -f logs/validator.log
tail -f logs/writer.log
```

### 查看生成的数据
```bash
# 按类型查看
ls -lh data/skin_sensor/
ls -lh data/environment/
ls -lh data/device/

# 查看最新文件内容
cat $(ls -t data/skin_sensor/*.json | head -1)
```

---

## ⚙️ 配置修改

### 修改 MQ 类型
编辑各模块的 `Config` 类：
```python
MQ_TYPE = 'redis'      # 或 'rabbitmq'
MQ_HOST = 'localhost'
MQ_PORT = 6379
```

### 修改重传策略
编辑 `simulator_mq.py`:
```python
MAX_RETRY_COUNT = 3       # 最大重试次数
RETRY_INTERVAL = 30       # 重试间隔（秒）
TIMEOUT_SECONDS = 10      # 超时时间（秒）
```

### 修改采样频率
编辑 `simulator_mq.py`:
```python
SKIN_SENSOR_INTERVAL = 2   # 皮肤传感器间隔（秒）
ENV_SENSOR_INTERVAL = 3    # 环境传感器间隔（秒）
```

---

## 🐛 故障排查

### 问题 1: Redis 连接失败
```bash
# 检查 Redis 是否运行
redis-cli ping
# 应返回 PONG

# 启动 Redis
docker run -d -p 6379:6379 redis:latest
```

### 问题 2: 模块无法消费消息
```bash
# 清空 Redis 流重新开始
redis-cli FLUSHDB

# 重启模块
python module_receiver.py
```

### 问题 3: 数据没有写入文件
```bash
# 检查写入模块日志
tail -f logs/writer.log

# 检查 data 目录权限
ls -ld data/

# 手动创建目录
mkdir -p data/skin_sensor data/environment data/device
```

---

## 📊 性能指标

### 查看模块运行状态
```bash
# 查看运行的模块数量
redis-cli XINFO GROUPS sensor:raw
redis-cli XINFO GROUPS sensor:validated
redis-cli XINFO GROUPS sensor:write
```

### 查看消息处理量
```bash
# 各队列消息数量
redis-cli XLEN sensor:raw           # 待处理
redis-cli XLEN sensor:validated     # 待验证
redis-cli XLEN sensor:write         # 待写入

# 数字应该保持较低或为 0，说明处理及时
```

---

## 🎯 关键特性

### ✅ 高可靠性
- 消息持久化
- 自动重试机制
- 消费者组负载均衡

### ✅ 高可扩展性
- 支持多实例并行
- 模块独立启停
- 水平扩展能力

### ✅ 高可维护性
- 职责单一
- 独立日志
- 易于调试

### ✅ 高可观测性
- 实时监控
- 性能统计
- 告警日志

---

## 📞 常用命令汇总

```bash
# 安装依赖
pip install -r requirements.txt

# 启动 Redis
docker run -d -p 6379:6379 redis:latest

# 启动所有模块
python start_all_modules.py

# 运行 API 测试
python api_auto_test.py http://localhost:5000

# 查看 Redis 状态
redis-cli INFO

# 清空测试数据
redis-cli FLUSHDB
rm -rf data/*/*.json
rm -rf logs/*.log

# 查看帮助
python simulator_mq.py --help
```

---

## 🎓 学习要点

1. **消息队列模式** - 理解 Publish/Subscribe 模型
2. **消费者组** - 掌握负载均衡原理
3. **异步处理** - 提高系统吞吐量
4. **模块化设计** - 单一职责原则
5. **容错机制** - 重试、超时、错误处理
6. **监控运维** - 日志、统计、告警

---

## 📚 相关文档

- `IMPLEMENTATION_SUMMARY.md` - 完整实施指南
- `WEEK4_TASK_GUIDE.md` - 任务详细指南
- `swagger.json` - API 标准定义
- `postman_collection.json` - Postman 测试集

---

**祝学习愉快！** 🚀
