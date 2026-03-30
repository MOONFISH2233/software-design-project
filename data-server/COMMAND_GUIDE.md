# 🚀 终端命令使用指南

本文档包含所有常用的终端命令，帮助你快速上手和操作整个系统。

---

## 📋 脚本文件列表

已为你创建以下便捷脚本（Windows 批处理）：

| 文件名 | 功能 | 说明 |
|--------|------|------|
| `start_all.bat` | 一键启动所有模块 | 自动检查环境并启动 4 个窗口 |
| `test_api.bat` | API 自动化测试 | 运行完整的 API 测试套件 |
| `start_redis.bat` | 启动 Redis 服务 | 使用 Docker 方式启动 Redis |
| `check_status.bat` | 查看系统状态 | 检查所有组件运行状态 |
| `cleanup.bat` | 清理测试数据 | 清空 Redis、日志和数据文件 |
| `manual_test.bat` | 手动测试 API | 交互式测试各个 API 接口 |

---

## 🎯 快速开始（3 步走）

### 方式一：使用脚本（推荐）

#### Step 1: 启动 Redis
```bash
# 双击运行或在命令行执行
start_redis.bat
```

#### Step 2: 启动所有模块
```bash
# 双击运行或在命令行执行
start_all.bat
```
会自动打开 4 个窗口：
- 数据接收模块
- 数据验证模块
- 数据写入模块
- 模拟器客户端

#### Step 3: 测试系统
```bash
# 方式 A: 自动化测试
test_api.bat http://localhost:5000

# 方式 B: 手动测试
manual_test.bat

# 方式 C: 查看状态
check_status.bat
```

---

### 方式二：手动命令

#### 1. 安装依赖
```bash
cd data-server
pip install -r requirements.txt
```

#### 2. 启动 Redis
```bash
# Docker 方式（推荐）
docker run -d -p 6379:6379 --name redis-server redis:latest

# 验证连接
redis-cli ping
# 应返回：PONG
```

#### 3. 启动各个模块（需要 4 个终端窗口）

**终端 1 - 接收模块:**
```bash
cd d:\学习\软件设计\data-server
python module_receiver.py
```

**终端 2 - 验证模块:**
```bash
cd d:\学习\软件设计\data-server
python module_validator.py
```

**终端 3 - 写入模块:**
```bash
cd d:\学习\软件设计\data-server
python module_writer.py
```

**终端 4 - 模拟器:**
```bash
cd d:\学习\软件设计\data-server
python simulator_mq.py
```

---

## 🔍 常用命令详解

### 1. 启动 Redis

**使用 Docker:**
```bash
# 启动
docker run -d -p 6379:6379 --name redis-server redis:latest

# 查看状态
docker ps | findstr redis

# 停止
docker stop redis-server

# 重启
docker restart redis-server

# 删除容器
docker rm redis-server
```

**使用本地安装:**
```bash
# 启动 Redis 服务器
redis-server

# 连接客户端
redis-cli

# 测试连接
redis-cli ping
```

---

### 2. 查看 MQ 状态

```bash
# 查看各队列消息数量
redis-cli XLEN sensor:raw
redis-cli XLEN sensor:validated
redis-cli XLEN sensor:write

# 查看消费者组信息
redis-cli XINFO GROUPS sensor:raw
redis-cli XINFO GROUPS sensor:validated
redis-cli XINFO GROUPS sensor:write

# 查看流中的消息
redis-cli XRANGE sensor:raw - +

# 查看所有键
redis-cli KEYS *

# 清空数据库
redis-cli FLUSHDB
```

---

### 3. 测试 API 接口

**使用 curl 命令:**
```bash
# 健康检查
curl http://localhost:5000/api/health

# 统计信息
curl http://localhost:5000/api/stats

# 日志查询
curl http://localhost:5000/api/logs

# 上传皮肤传感器数据
curl -X POST http://localhost:5000/api/sensor/skin ^
  -H "Content-Type: application/json" ^
  -d "{\"moisture\":65,\"oiliness\":35}"

# 上传环境传感器数据
curl -X POST http://localhost:5000/api/sensor/environment ^
  -H "Content-Type: application/json" ^
  -d "{\"humidity\":55,\"light_lux\":650,\"temperature\":25.5}"
```

**使用 PowerShell:**
```powershell
# 健康检查
Invoke-RestMethod http://localhost:5000/api/health

# 上传数据
Invoke-RestMethod -Uri http://localhost:5000/api/sensor/skin `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"moisture":65,"oiliness":35}'
```

---

### 4. 查看日志和数据

```bash
# 查看实时日志（Linux/Mac）
tail -f logs/receiver.log
tail -f logs/validator.log
tail -f logs/writer.log
tail -f logs/system.log

# Windows PowerShell
Get-Content logs\receiver.log -Wait -Tail 50
Get-Content logs\system.log -Wait -Tail 50

# 查看最新生成的数据文件
dir data\skin_sensor\*.json /OD
dir data\environment\*.json /OD
dir data\device\*.json /OD

# 查看文件内容
type data\skin_sensor\skin_*.json | more
```

---

### 5. 监控和调试

```bash
# 查看 Redis 内存使用
redis-cli INFO memory

# 查看 Redis 统计
redis-cli INFO stats

# 慢查询日志
redis-cli SLOWLOG GET 10

# 查看进程信息
redis-cli CLIENT LIST

# 监控命令执行
redis-cli MONITOR
```

---

### 6. 性能测试

```bash
# 并发测试（使用 Apache Bench）
ab -n 1000 -c 10 http://localhost:5000/api/health

# 使用 curl 进行压力测试
for /L %i in (1,1,100) do curl -s http://localhost:5000/api/health >nul

# 查看处理延迟
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:5000/api/health
```

---

## 🛠️ 故障排查命令

### 问题 1: 无法连接 Redis
```bash
# 检查 Redis 是否运行
docker ps | findstr redis

# 检查端口占用
netstat -ano | findstr :6379

# 测试连接
redis-cli ping
```

### 问题 2: 模块启动失败
```bash
# 检查 Python 版本
python --version

# 检查依赖包
pip list | findstr redis
pip list | findstr pika

# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

### 问题 3: 消息不消费
```bash
# 查看消费者组
redis-cli XINFO GROUPS sensor:raw

# 查看未确认消息
redis-cli XPENDING sensor:raw receiver_group

# 强制删除消费者组
redis-cli XGROUP DESTROY sensor:raw receiver_group
```

---

## 📊 运维命令

### 备份数据
```bash
# 备份 Redis 数据
redis-cli BGSAVE

# 导出 RDB 文件
copy "C:\Program Files\Redis\dump.rdb" backup\dump_%date%.rdb

# 导出数据
redis-cli --rdb backup.dump --type stream sensor:raw
```

### 恢复数据
```bash
# 停止 Redis
docker stop redis-server

# 替换 RDB 文件
copy backup\dump.rdb "C:\Program Files\Redis\dump.rdb"

# 重启 Redis
docker start redis-server
```

### 日志轮转
```bash
# 压缩旧日志
powershell Compress-Archive -Path logs\*.log -DestinationPath logs\logs_%date%.zip

# 删除 7 天前的日志
forfiles /p logs /s /m *.log /d -7 /c "cmd /c del @path"
```

---

## 🎯 完整工作流程示例

### 场景 1: 全新启动系统
```bash
# 1. 启动 Redis
start_redis.bat

# 2. 等待 Redis 启动完成
timeout /t 3

# 3. 启动所有模块
start_all.bat

# 4. 等待系统就绪
timeout /t 5

# 5. 运行测试
test_api.bat

# 6. 查看状态
check_status.bat
```

### 场景 2: 开发和调试
```bash
# 1. 清理之前的数据
cleanup.bat

# 2. 启动 Redis
start_redis.bat

# 3. 单独启动某个模块（调试用）
python module_receiver.py

# 4. 新开窗口启动模拟器
python simulator_mq.py

# 5. 手动测试 API
manual_test.bat

# 6. 查看实时日志
Get-Content logs\receiver.log -Wait
```

### 场景 3: 性能测试
```bash
# 1. 启动系统
start_all.bat

# 2. 运行压力测试
for /L %i in (1,1,1000) do curl -X POST http://localhost:5000/api/sensor/skin -H "Content-Type: application/json" -d "{\"moisture\":%i,\"oiliness\":50}"

# 3. 查看 MQ 积压
redis-cli XLEN sensor:raw
redis-cli XLEN sensor:validated
redis-cli XLEN sensor:write

# 4. 查看统计
curl http://localhost:5000/api/stats
```

### 场景 4: 日常运维
```bash
# 1. 早上启动系统
start_all.bat

# 2. 中午检查状态
check_status.bat

# 3. 下午查看日志
Get-Content logs\system.log -Tail 100

# 4. 晚上停止系统
# 直接关闭各个窗口即可

# 5. 定期清理（每周一次）
cleanup.bat
```

---

## 📝 自定义脚本示例

### 创建自己的启动脚本
```batch
@echo off
REM 自定义启动脚本

echo 启动我的系统...

REM 启动 Redis
docker start redis-server

REM 等待
timeout /t 2

REM 启动特定模块
start python module_receiver.py
start python module_validator.py

REM 启动模拟器
python simulator_mq.py
```

### 批量测试脚本
```batch
@echo off
REM 批量测试所有接口

set URL=http://localhost:5000

echo 测试开始...

for /L %%i in (1,1,100) do (
    curl -X POST %URL%/api/sensor/skin ^
      -H "Content-Type: application/json" ^
      -d "{\"moisture\":%%i,\"oiliness\":50}" >nul
)

echo 测试完成！
```

---

## 💡 小贴士

1. **使用 Tab 补全**: 输入命令时按 Tab 可以自动补全路径和文件名
2. **使用历史记录**: 上下箭头可以查看之前执行过的命令
3. **多窗口管理**: 给每个窗口起个好记的名字
4. **日志查看**: 使用 `Get-Content -Wait` 可以实时查看日志
5. **后台运行**: 使用 `start /B` 可以在后台运行程序

---

## 🆘 常见问题

### Q: 脚本无法运行？
**A:** 右键 → "以管理员身份运行"，或修改 PowerShell 执行策略：
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Q: Docker 无法启动？
**A:** 确保 Docker Desktop 已启动，并在系统托盘中显示绿色图标

### Q: 端口被占用？
**A:** 查看占用端口的进程：
```bash
netstat -ano | findstr :6379
taskkill /F /PID <进程 ID>
```

### Q: 中文乱码？
**A:** 在脚本开头添加：
```batch
chcp 65001
```

---

## 📚 相关文档

- `QUICK_REFERENCE.md` - 快速参考卡片
- `IMPLEMENTATION_SUMMARY.md` - 完整实施指南
- `TASK_COMPLETION_SUMMARY.md` - 任务总结

---

**祝你使用愉快！** 🎉
