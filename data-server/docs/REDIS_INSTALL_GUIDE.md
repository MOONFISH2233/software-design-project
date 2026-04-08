# 🔧 服务器 Redis 安装快速指南

**问题**: `pip: command not found`  
**服务器**: 47.103.108.47

---

## 🎯 快速解决方案（按顺序执行）

### 方法 1：使用 python3 -m pip（最简单）⭐

在服务器终端执行以下命令：

```bash
# 1. 直接使用 python3 -m pip 安装
python3 -m pip install redis

# 2. 验证安装成功
python3 -c "import redis; print('✅ Redis 模块已安装')"

# 3. 检查 Docker 是否可用
docker --version

# 4. 启动 Redis 容器
docker run -d -p 6379:6379 --name redis-server redis:latest

# 5. 验证 Redis 运行
docker ps | grep redis
redis-cli -h localhost ping

# 6. 启动所有模块
cd /root/data-server
python3 start_all_modules.py
```

---

### 方法 2：使用 yum 安装 python3-pip

如果方法 1 不行，执行：

```bash
# 1. 使用 yum 安装 python3-pip
yum install -y python3-pip

# 2. 安装 redis 模块
pip3 install redis

# 3. 启动 Redis
docker run -d -p 6379:6379 --name redis-server redis:latest

# 4. 测试
redis-cli -h localhost ping
```

---

### 方法 3：使用系统 Redis（不依赖 Docker）

如果 Docker 不可用：

```bash
# 1. 安装 Redis
yum install -y redis

# 2. 启动 Redis 服务
systemctl start redis

# 3. 设置开机自启
systemctl enable redis

# 4. 验证
redis-cli ping

# 5. 安装 Python redis 模块
python3 -m pip install redis

# 6. 启动应用
cd /root/data-server
python3 start_all_modules.py
```

---

## 📋 完整的部署检查清单

### 第一步：检查 Python 环境

```bash
# 查看 Python 版本
python3 --version

# 查看 pip 是否可用
python3 -m pip --version

# 查看已安装的包
python3 -m pip list
```

### 第二步：安装依赖

```bash
cd /root/data-server

# 方法 A：使用 requirements.txt
python3 -m pip install -r requirements.txt

# 方法 B：手动安装每个包
python3 -m pip install flask redis pika pyyaml requests
```

### 第三步：启动 Redis

**选项 A：Docker 方式（推荐）**

```bash
# 启动 Redis
docker run -d -p 6379:6379 --name redis-server redis:latest

# 查看容器状态
docker ps

# 测试连接
redis-cli -h localhost ping
```

**选项 B：系统服务方式**

```bash
# 启动 Redis
systemctl start redis

# 查看状态
systemctl status redis

# 测试连接
redis-cli ping
```

### 第四步：启动应用

```bash
cd /root/data-server

# 启动所有 MQ 模块
python3 start_all_modules.py

# 或者单独启动 Flask 应用
python3 app.py
```

---

## 🔍 故障排查

### 问题 1：python3 -m pip 也不可用

**症状**:
```
/usr/bin/python3: No module named pip
```

**解决**:
```bash
# 下载 get-pip.py
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

# 安装 pip
python3 get-pip.py

# 然后安装 redis
python3 -m pip install redis
```

### 问题 2：Docker 未安装

**症状**:
```
-bash: docker: command not found
```

**解决**:
```bash
# 安装 Docker
yum install -y docker

# 启动 Docker
systemctl start docker
systemctl enable docker

# 验证
docker --version

# 然后启动 Redis
docker run -d -p 6379:6379 redis:latest
```

### 问题 3：Redis 服务未运行

**症状**:
```
Could not connect to Redis at 127.0.0.1:6379: Connection refused
```

**解决**:
```bash
# 检查 Redis 状态
systemctl status redis

# 启动 Redis
systemctl start redis

# 或者重启 Redis
systemctl restart redis

# 设置开机自启
systemctl enable redis
```

### 问题 4：端口被占用

**症状**:
```
Address already in use
```

**解决**:
```bash
# 查看谁占用了端口
netstat -tunlp | grep 6379
netstat -tunlp | grep 5000

# 杀死占用端口的进程
kill -9 <PID>

# 或者重启服务
systemctl restart redis
pkill -f "python.*app.py"
```

---

## ✅ 验证部署成功

### 快速验证脚本

在服务器终端执行：

```bash
cat > /tmp/verify_setup.sh << 'EOF'
#!/bin/bash
echo "======================================"
echo "  验证服务器部署"
echo "======================================"

echo ""
echo "[1/5] 检查 Python 版本..."
python3 --version

echo ""
echo "[2/5] 检查 Redis 模块..."
python3 -c "import redis; print('✅ Redis 模块已安装')" 2>/dev/null || echo "❌ Redis 模块未安装"

echo ""
echo "[3/5] 检查 Redis 服务..."
redis-cli -h localhost ping > /dev/null 2>&1 && echo "✅ Redis 服务运行中" || echo "❌ Redis 服务未运行"

echo ""
echo "[4/5] 检查 Docker 容器..."
docker ps | grep redis > /dev/null 2>&1 && echo "✅ Redis Docker 容器运行中" || echo "❌ 未使用 Docker 或 Redis 容器未运行"

echo ""
echo "[5/5] 测试应用启动..."
cd /root/data-server
timeout 5 python3 start_all_modules.py 2>&1 | head -20

echo ""
echo "======================================"
echo "  验证完成"
echo "======================================"
EOF

chmod +x /tmp/verify_setup.sh
/tmp/verify_setup.sh
```

---

## 📊 一键启动脚本

创建一个快速启动脚本：

```bash
cat > /root/start.sh << 'EOF'
#!/bin/bash
echo "======================================"
echo "  启动数据服务器"
echo "======================================"

cd /root/data-server

# 检查 Redis
echo "[1/3] 检查 Redis..."
redis-cli -h localhost ping > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "      ❌ Redis 未运行，正在启动..."
    docker start redis-server 2>/dev/null || systemctl start redis
    sleep 2
fi
echo "      ✅ Redis 运行中"

# 启动应用
echo "[2/3] 启动应用..."
python3 start_all_modules.py

echo "[3/3] 验证服务..."
sleep 3
curl -s http://localhost:5000/api/health | python3 -m json.tool

echo ""
echo "======================================"
echo "  启动完成！"
echo "======================================"
EOF

chmod +x /root/start.sh
```

使用：
```bash
/root/start.sh
```

---

## 🎯 推荐的完整执行流程

在服务器终端依次执行：

```bash
# 1. 安装 redis 模块
python3 -m pip install redis

# 2. 启动 Redis（Docker 方式）
docker run -d -p 6379:6379 --name redis-server redis:latest

# 3. 等待 Redis 启动
sleep 3

# 4. 验证 Redis
redis-cli -h localhost ping

# 5. 进入项目目录
cd /root/data-server

# 6. 启动所有模块
python3 start_all_modules.py

# 7. 测试 API
python3 api_auto_test.py http://localhost:5000
```

---

## 📞 需要帮助？

如果以上方法都不行，请提供以下信息：

```bash
# Python 版本
python3 --version

# pip 是否可用
python3 -m pip --version

# Docker 是否可用
docker --version

# Redis 是否安装
redis-cli --version

# 操作系统版本
cat /etc/redhat-release
```

---

**最后更新**: 2026-03-30  
**目标**: 解决 `pip: command not found` 问题并启动 Redis 服务
