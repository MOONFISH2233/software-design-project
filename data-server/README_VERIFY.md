# 第四周任务验证指南

> 本文档说明如何验证第四周的每项任务是否完成。

---

## 快速验证（推荐）

在 `data-server/` 目录下运行一键验证脚本：

```bash
cd data-server
python verify_local.py
```

该脚本**不需要连接远程服务器**，会自动检查代码实现、启动Flask测试客户端、模拟重传机制，输出每项任务的通过情况。

---

## 任务1：API接口管理工具

### 验证方法一：查看已生成的文件

```bash
ls swagger.json postman_collection.json api_auto_test.py
```

预期输出：三个文件均存在。

### 验证方法二：导入 Postman 测试

1. 打开 Postman → Import → 选择 `postman_collection.json`
2. 修改集合变量 `base_url` 为 `http://47.103.108.47:5000`
3. 逐个点击接口发送请求，观察返回结果

### 验证方法三：运行自动化测试脚本

```bash
# 测试远程服务器（需服务器在线）
python api_auto_test.py http://47.103.108.47:5000

# 测试本地服务器
python app.py          # 先启动服务器（新窗口）
python api_auto_test.py http://localhost:5000
```

**预期结果**：测试报告显示 7 个接口全部通过，并生成 `api_test_report_*.json` 文件。

### 验证截图要点
- Postman 中能看到完整的接口集合列表
- 每个接口返回 `status: success`
- 自动测试脚本输出 `成功率: 100%`

---

## 任务2：数据服务器每个接口独立写文件

### 验证方法一：代码检查

```bash
grep -n "sensor/skin\|sensor/environment\|device/status" app.py
grep -n "save_sensor_data\|skin_sensor\|environment\|device" app.py
```

### 验证方法二：启动服务器发送请求

```bash
# 启动服务器
python app.py

# 新开终端，发送请求
# 皮肤传感器
curl -X POST http://localhost:5000/api/sensor/skin \
  -H "Content-Type: application/json" \
  -d '{"moisture": 65, "oiliness": 35, "device_id": "test_001"}'

# 环境传感器
curl -X POST http://localhost:5000/api/sensor/environment \
  -H "Content-Type: application/json" \
  -d '{"humidity": 55, "light_lux": 600, "temperature": 25.0}'

# 设备状态
curl -X POST http://localhost:5000/api/device/status \
  -H "Content-Type: application/json" \
  -d '{"device_id": "mirror_001", "status": "online"}'
```

### 验证方法三：查看数据文件

```bash
# 查看是否生成了独立目录和文件
ls data/skin_sensor/
ls data/environment/
ls data/device/
```

**预期结果**：
- `data/skin_sensor/` 下有 `skin_sensor_*.json` 文件
- `data/environment/` 下有 `environment_*.json` 文件  
- `data/device/` 下有 `device_*.json` 文件
- 每个文件内容只包含对应传感器的数据

### 验证截图要点
- 3个接口各自返回不同的 `sensor_type` 字段
- `data/` 目录下有3个独立子目录
- 每个子目录中有独立的 JSON 数据文件

---

## 任务3：模拟器改造为MQ模式 + 重传机制

### 验证方法一：代码走读

```bash
# 查看MQ发布相关代码
grep -n "publish\|retry\|RETRY_INTERVAL\|MAX_RETRY" simulator_mq.py
```

### 验证方法二：本地运行（连接远程Redis）

```bash
# simulator_mq.py 中 Config.MQ_HOST = '47.103.108.47'
python simulator_mq.py
```

**预期输出**：
```
✅ MQ 连接成功 - redis
✅ 线程 SkinThread 已启动
✅ 线程 EnvThread 已启动
✅ 线程 RetryThread 已启动
✅ 线程 MonitorThread 已启动
[2026-...] 💧 皮肤传感器已记录 -> 水分度:72% | 油亮度:28%
    📤 已发布到 MQ: skin - 2026-...
```

### 验证方法三：验证重传机制

断开网络或关闭Redis后运行，观察失败数据加入重试队列：

```
⚠️  发布失败：...
    💾 已加入重试队列，将在 30 秒后重试
📊 模拟器统计信息：失败: 3 条，等待重传: 3 条
```

恢复连接后，看到：
```
🔄 正在重传：skin (第 1 次)
📤 已发布到 MQ: skin
```

### 验证截图要点
- 控制台显示"已发布到 MQ"日志
- 统计信息面板展示发布数量
- 断网后自动入队，恢复后自动重传

---

## 任务4：服务器MQ模块化架构

### 验证方法一：查看4个模块文件

```bash
ls module_receiver.py module_validator.py module_writer.py module_logger.py
```

### 验证方法二：一键启动所有模块

```bash
# 连接远程服务器（默认）
python start_all_modules.py

# 连接本地Redis
python start_all_modules.py --host localhost

# 只启动服务端（不启动模拟器）
python start_all_modules.py --no-simulator
```

**预期输出**：
```
✅ Redis 连接成功
✅ module_receiver.py 已启动 (PID: 12345)
✅ module_validator.py 已启动 (PID: 12346)
✅ module_writer.py 已启动 (PID: 12347)
✅ module_logger.py 已启动 (PID: 12348)
✅ simulator_mq.py 已启动 (PID: 12349)
```

### 验证方法三：启动多个相同模块实例

```bash
# 启动2个写入模块（演示水平扩展）
python module_writer.py   # 终端1
python module_writer.py   # 终端2
```

**预期结果**：两个写入模块各有不同的PID，同时消费写入队列，数据不重复写入。

### 验证方法四：独立停止某个模块

在运行时按 `Ctrl+C` 停止某个模块，其他模块继续运行，验证模块独立性。

### 验证方法五：查看日志文件

```bash
# 查看各模块日志
cat logs/receiver.log
cat logs/validator.log
cat logs/writer.log
cat logs/system.log    # 日志模块的系统日志
cat logs/alerts.log    # 告警日志
```

### 验证截图要点
- 4个模块分别在不同终端/进程运行
- `logs/` 目录下有各模块独立的日志文件
- 启动2个 module_writer.py 时，日志中有2个不同的PID

---

## 完整流水线验证

同时运行所有组件，观察完整的数据流：

```
模拟器客户端
  ↓ 发布数据
Redis Stream (sensor:raw)
  ↓ 消费
接收模块 (module_receiver.py)
  ↓ 格式检查 → 转发
Redis Stream (sensor:validated)
  ↓ 消费
验证模块 (module_validator.py)
  ↓ 数值校验 → 转发
Redis Stream (sensor:write)
  ↓ 消费
写入模块 (module_writer.py)
  ↓ 按类型写入
data/skin_sensor/*.json
data/environment/*.json
data/device/*.json
```

验证数据流通：

```bash
# 查看Redis中的消息（需要redis-cli）
redis-cli -h 47.103.108.47 xlen sensor:raw
redis-cli -h 47.103.108.47 xlen sensor:validated
redis-cli -h 47.103.108.47 xlen sensor:write

# 查看写入的数据文件数量
ls data/skin_sensor/ | wc -l
ls data/environment/ | wc -l
```

---

## 常见问题

| 问题 | 解决方法 |
|------|----------|
| Redis连接失败 | 检查远程服务器 47.103.108.47 是否在线，或改用本地Redis |
| 模块找不到mq_utils | 确保在 `data-server/` 目录下运行 |
| 数据目录不存在 | 首次运行app.py或模块后会自动创建 |
| 验证脚本报错 | 先安装依赖：`pip install flask redis requests` |
