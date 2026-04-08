# 🚀 服务器部署和运行指南

**服务器地址**: 47.103.108.47  
**用户名**: root  
**密码**: @Dierzu999

---

## 📋 快速开始（按顺序执行）

### 步骤 1: 登录服务器

```bash
# Windows PowerShell
ssh root@47.103.108.47
# 输入密码：@Dierzu999
```

### 步骤 2: 安装 Python 依赖

```bash
cd /root/data-server
pip install -r requirements.txt
```

**requirements.txt 包含:**
```txt
flask==3.0.0
redis==5.0.1
pika==1.3.2
pyyaml==6.0.1
requests==2.31.0
```

### 步骤 3: 安装并启动 Redis

#### 方法 A: 使用 Docker（推荐）

```bash
# 检查 Docker 是否安装
docker --version

# 启动 Redis 容器
docker run -d -p 6379:6379 --name redis-server redis:latest

# 验证 Redis 运行
docker ps | grep redis
```

#### 方法 B: 使用 yum 安装

```bash
# 安装 Redis
yum install -y redis

# 启动 Redis
systemctl start redis
systemctl enable redis

# 验证 Redis
redis-cli ping
# 应该返回：PONG
```

### 步骤 4: 启动 MQ 数据服务器

```bash
# 一键启动所有模块（推荐）
python start_all_modules.py

# 或者单独启动 Flask 服务器
python app.py
```

### 步骤 5: 测试 API

```bash
# 运行自动化测试
python api_auto_test.py http://localhost:5000

# 或者手动测试
curl http://localhost:5000/api/health
```

---

## 🔧 常见问题解决

### 问题 1: Redis 连接失败

**错误信息:**
```
❌ Redis 连接失败：No module named 'redis'
```

**解决方案:**
```bash
# 安装 redis 模块
pip install redis

# 如果已经安装，检查 Redis 服务是否运行
redis-cli ping
# 如果不通，启动 Redis
systemctl start redis
# 或者使用 Docker
docker run -d -p 6379:6379 redis:latest
```

### 问题 2: 端口被占用

**错误信息:**
```
Address already in use
```

**解决方案:**
```bash
# 查看占用端口的进程
netstat -tunlp | grep 5000
netstat -tunlp | grep 6379

# 杀死占用端口的进程
kill -9 <PID>

# 或者重启 Flask 服务
pkill -f "python app.py"
python app.py
```

### 问题 3: 权限问题

**错误信息:**
```
Permission denied
```

**解决方案:**
```bash
# 给脚本执行权限
chmod +x *.sh
chmod +x *.bat

# 或者使用 python 直接运行
python module_receiver.py
python module_validator.py
python module_writer.py
python module_logger.py
```

---

## 📊 系统状态检查

### 检查 Redis 状态

```bash
# 检查 Redis 是否运行
redis-cli ping
# 返回 PONG 表示正常

# 查看 Redis 信息
redis-cli info

# 查看 Redis 内存使用
redis-cli info memory
```

### 检查 Python 进程

```bash
# 查看所有 Python 进程
ps aux | grep python

# 查看 MQ 模块进程
ps aux | grep module_
```

### 检查端口监听

```bash
# 查看 5000 端口（Flask）
netstat -tunlp | grep 5000

# 查看 6379 端口（Redis）
netstat -tunlp | grep 6379
```

### 检查日志

```bash
# 查看应用日志
tail -f server_*.log

# 查看最近的错误
grep ERROR server_*.log | tail -20
```

---

## 🎯 完整的启动流程示例

### 首次部署（从零开始）

```bash
# 1. 登录服务器
ssh root@47.103.108.47

# 2. 进入目录
cd /root/data-server

# 3. 安装 Python 依赖
pip install -r requirements.txt

# 4. 安装 Docker（如果没有）
yum install -y docker
systemctl start docker
systemctl enable docker

# 5. 启动 Redis
docker run -d -p 6379:6379 --name redis-server redis:latest

# 6. 验证 Redis
docker ps | grep redis
redis-cli ping -h localhost

# 7. 启动所有 MQ 模块
python start_all_modules.py

# 8. 测试 API
python api_auto_test.py http://localhost:5000
```

### 日常启动

```bash
# 1. 登录服务器
ssh root@47.103.108.47

# 2. 进入目录
cd /root/data-server

# 3. 检查 Redis 状态
redis-cli ping

# 4. 如果 Redis 没运行，启动它
docker start redis-server
# 或者
systemctl start redis

# 5. 启动应用
python start_all_modules.py
```

---

## 🔍 故障排查命令

### 查看系统资源

```bash
# CPU 和内存使用
top

# 磁盘空间
df -h

# 内存使用
free -h
```

### 查看进程信息

```bash
# 查看特定进程
ps aux | grep python
ps aux | grep redis

# 查看进程详细信息
ps -p <PID> -o pid,ppid,user,%cpu,%mem,cmd
```

### 网络检查

```bash
# 查看监听的端口
netstat -tunlp

# 测试本地连接
telnet localhost 6379
telnet localhost 5000
```

---

## 📁 目录结构

```
/root/
├── simulator_mq.py              # MQ 模拟器
└── data-server/                 # 数据服务器目录
    ├── app.py                   # Flask 主应用
    ├── module_receiver.py       # 接收模块
    ├── module_validator.py      # 验证模块
    ├── module_writer.py         # 写入模块
    ├── module_logger.py         # 日志模块
    ├── mq_utils.py              # MQ 工具类
    ├── api_auto_test.py         # API 测试脚本
    ├── start_all_modules.py     # 一键启动脚本
    ├── requirements.txt         # Python 依赖
    ├── swagger.json             # API 文档
    ├── postman_collection.json  # Postman 集合
    ├── data/                    # 数据存储目录
    │   ├── skin_sensor/        # 皮肤传感器数据
    │   ├── environment/        # 环境传感器数据
    │   └── device/             # 设备状态数据
    └── logs/                    # 日志目录
        └── server_*.log
```

---

## 🎊 验证部署成功

运行以下命令验证一切正常：

```bash
# 1. 检查 Redis
redis-cli ping
# 应该返回：PONG

# 2. 检查 Python 进程
ps aux | grep python
# 应该看到 app.py 和 4 个 module_*.py 进程

# 3. 检查端口
netstat -tunlp | grep -E '5000|6379'
# 应该看到 5000 和 6379 端口在监听

# 4. 测试 API
curl http://localhost:5000/api/health
# 应该返回：{"status": "healthy"}

# 5. 运行完整测试
python api_auto_test.py http://localhost:5000
# 应该看到大部分测试通过
```

---

## 🚀 一键部署脚本

创建一个快速部署脚本：

```bash
cat > /root/deploy.sh << 'EOF'
#!/bin/bash
echo "========================================"
echo "  一键部署数据服务器"
echo "========================================"

cd /root/data-server

echo "[1/4] 安装 Python 依赖..."
pip install -r requirements.txt

echo "[2/4] 启动 Redis..."
docker run -d -p 6379:6379 --name redis-server redis:latest || docker start redis-server

echo "[3/4] 等待 Redis 启动..."
sleep 3

echo "[4/4] 启动所有服务..."
python start_all_modules.py &

echo ""
echo "========================================"
echo "  部署完成！"
echo "========================================"
echo ""
echo "测试 API: python api_auto_test.py http://localhost:5000"
echo "查看日志：tail -f server_*.log"
EOF

chmod +x /root/deploy.sh
```

运行一键部署：
```bash
/root/deploy.sh
```

---

## 📞 需要帮助？

如果遇到其他问题：

1. **查看日志文件** - 包含详细的错误信息
2. **检查系统资源** - 确保有足够的内存和磁盘空间
3. **重启服务** - 很多时候重启能解决问题
4. **查看文档** - `COMMAND_GUIDE.md` 包含所有命令详解

---

**最后更新**: 2026-03-30  
**服务器**: 47.103.108.47
