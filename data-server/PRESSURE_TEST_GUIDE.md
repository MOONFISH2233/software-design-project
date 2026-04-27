# 压力测试使用指南

## 📌 问题修复说明

之前遇到的两个问题已修复：
1. ✅ **jmeter_test.py 文件损坏** - 已重新创建完整的文件
2. ✅ **load_test.py 的 percentile 导入错误** - 已移除 Python 3.6 不支持的导入

---

## 🚀 快速开始

### 前置条件

确保服务器已在运行：

```bash
# SSH 登录服务器
ssh root@47.103.108.47

# 进入项目目录
cd /root/course-project/week5/data-server

# 检查服务器是否在运行
ps aux | grep "python app.py" | grep -v grep
```

**如果服务器未运行，先启动：**

```bash
# 启动服务器（后台运行）
nohup python app.py > server.log 2>&1 &

# 等待 2 秒
sleep 2

# 验证服务器是否启动成功
curl http://localhost:5000/api/health
```

---

## 📊 压力测试方法

### 方法一：使用 jmeter_test.py（推荐）

这是最简单、最强大的压力测试工具。

#### 1️⃣ 测试普通模式（无认证）

```bash
cd /root/course-project/week5/data-server

# 快速测试（10秒，5并发）
python jmeter_test.py --url http://localhost:5000 --duration 10 --users 5 --type normal

# 标准测试（60秒，10并发）
python jmeter_test.py --url http://localhost:5000 --duration 60 --users 10 --type normal

# 高强度测试（120秒，20并发）
python jmeter_test.py --url http://localhost:5000 --duration 120 --users 20 --type normal
```

#### 2️⃣ 测试 JWT 认证模式

```bash
# 使用 user1 账号测试
python jmeter_test.py --url http://localhost:5000 --duration 60 --users 10 --username user1 --password user123 --type encrypted

# 使用 admin 账号测试
python jmeter_test.py --url http://localhost:5000 --duration 60 --users 10 --username admin --password admin123 --type encrypted
```

#### 3️⃣ 测试 API Key 模式

```bash
python jmeter_test.py --url http://localhost:5000 --duration 60 --users 10 --apikey key_user1_001 --type apikey
```

#### 4️⃣ 参数说明

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `--url` | 服务器地址 | `http://localhost:5000` | `http://47.103.108.47:5000` |
| `--duration` | 测试持续时间（秒） | `60` | `30`, `60`, `120` |
| `--users` | 并发用户数 | `10` | `5`, `10`, `20`, `30` |
| `--username` | 用户名（JWT模式） | - | `user1`, `admin` |
| `--password` | 密码（JWT模式） | - | `user123`, `admin123` |
| `--apikey` | API Key（API Key模式） | - | `key_user1_001` |
| `--type` | 测试类型 | `normal` | `normal`, `encrypted`, `apikey` |

---

### 方法二：使用 auto_test.py（一键测试）

自动启动服务器并运行完整测试：

```bash
cd /root/course-project/week5/data-server

# 一键运行所有测试
python auto_test.py
```

---

### 方法三：使用 acceptance_demo.py（验收演示）

包含功能测试和性能测试的完整演示：

```bash
cd /root/course-project/week5/data-server

# 运行验收演示
python acceptance_demo.py --url http://localhost:5000
```

---

## 📈 解读测试结果

运行测试后，你会看到类似这样的输出：

```
============================================================
开始压力测试 - ENCRYPTED 模式
持续时间：60秒
并发用户：10
============================================================

工作线程 0 开始测试
工作线程 1 开始测试
...

测试进行中，请稍候 60 秒...

============================================================
压力测试结果
============================================================
总请求数：29870
成功请求：29750
失败请求：120
成功率：99.60%
总耗时：60.00秒
QPS (每秒请求数): 497.83

响应时间统计:
  平均：76.20ms
  中位数：68.50ms
  最小：12.30ms
  最大：245.80ms
  95 百分位：125.80ms
============================================================

测试结果已保存到：stress_test_results_20260408_004500.csv
```

### 关键指标解读

| 指标 | 含义 | 优秀标准 | 良好标准 | 说明 |
|------|------|----------|----------|------|
| **QPS** | 每秒处理请求数 | > 500 | > 300 | 越高越好，反映吞吐量 |
| **成功率** | 成功请求占比 | > 99.5% | > 99% | 反映系统稳定性 |
| **平均响应时间** | 平均处理时间 | < 50ms | < 100ms | 越低越好 |
| **P95 响应时间** | 95%请求的响应时间 | < 150ms | < 250ms | 反映长尾延迟 |
| **最大响应时间** | 最慢请求的响应时间 | < 300ms | < 500ms | 极端情况 |

---

## 🎯 推荐的测试方案

### 方案 A：快速验证（2分钟）

```bash
# 1. 普通模式快速测试
python jmeter_test.py --url http://localhost:5000 --duration 10 --users 5 --type normal

# 2. JWT 认证模式快速测试
python jmeter_test.py --url http://localhost:5000 --duration 10 --users 5 --username user1 --password user123 --type encrypted

# 3. API Key 模式快速测试
python jmeter_test.py --url http://localhost:5000 --duration 10 --users 5 --apikey key_user1_001 --type apikey
```

### 方案 B：标准测试（10分钟）

```bash
# 1. 普通模式标准测试
python jmeter_test.py --url http://localhost:5000 --duration 60 --users 10 --type normal

# 2. JWT 认证模式标准测试
python jmeter_test.py --url http://localhost:5000 --duration 60 --users 10 --username user1 --password user123 --type encrypted

# 3. API Key 模式标准测试
python jmeter_test.py --url http://localhost:5000 --duration 60 --users 10 --apikey key_user1_001 --type apikey
```

### 方案 C：完整验收测试（30分钟）

```bash
# 1. 逐步增加并发数（普通模式）
python jmeter_test.py --url http://localhost:5000 --duration 30 --users 5 --type normal
python jmeter_test.py --url http://localhost:5000 --duration 30 --users 10 --type normal
python jmeter_test.py --url http://localhost:5000 --duration 30 --users 20 --type normal
python jmeter_test.py --url http://localhost:5000 --duration 30 --users 30 --type normal

# 2. JWT 认证模式压力测试
python jmeter_test.py --url http://localhost:5000 --duration 60 --users 10 --username user1 --password user123 --type encrypted

# 3. 长时间稳定性测试（5分钟）
python jmeter_test.py --url http://localhost:5000 --duration 300 --users 10 --username user1 --password user123 --type encrypted
```

---

## 📁 测试结果文件

测试完成后会生成 CSV 文件：

```bash
# 查看生成的测试结果文件
ls -lh stress_test_results_*.csv

# 查看最近的文件
ls -lt stress_test_results_*.csv | head -5

# 查看 CSV 文件内容（前20行）
head -20 stress_test_results_*.csv
```

CSV 文件包含以下列：
- `worker_id` - 工作线程 ID
- `success` - 请求是否成功（True/False）
- `elapsed` - 响应时间（秒）
- `status_code` - HTTP 状态码
- `auth_method` - 认证方式
- `timestamp` - 请求时间戳
- `error` - 错误信息（如果有）

---

## 🔍 调试技巧

### 1. 查看服务器实时日志

```bash
# 在另一个终端查看日志
tail -f /root/course-project/week5/data-server/logs/server_*.log
```

### 2. 检查服务器状态

```bash
# 查看服务器进程
ps aux | grep "python app.py" | grep -v grep

# 查看端口占用
netstat -tlnp | grep 5000

# 查看服务器资源使用
top -p $(pgrep -f "python app.py")
```

### 3. 如果测试失败

```bash
# 1. 检查服务器是否在运行
curl http://localhost:5000/api/health

# 2. 查看最近的错误日志
tail -100 /root/course-project/week5/data-server/logs/server_*.log

# 3. 重启服务器
pkill -f "python app.py"
sleep 2
nohup python app.py > server.log 2>&1 &

# 4. 重新运行测试
python jmeter_test.py --url http://localhost:5000 --duration 10 --users 5 --type normal
```

---

## 📊 性能优化建议

如果 QPS 低于预期（< 300），可以尝试：

### 1. 减少日志写入频率

编辑 `app.py`，调整日志级别：

```python
# 将 DEBUG 改为 INFO 或 WARNING
app.config['LOG_LEVEL'] = 'INFO'
```

### 2. 增加线程数

```python
# 在 app.py 的 app.run() 中调整
app.run(host='0.0.0.0', port=5000, threaded=True)  # 已启用
```

### 3. 使用生产级 WSGI 服务器

```bash
# 安装 gunicorn
pip install gunicorn

# 使用 gunicorn 启动（8个worker）
gunicorn -w 8 -b 0.0.0.0:5000 app:app
```

---

## ✅ 验收标准

根据第五周任务要求，服务器应达到以下指标：

| 指标 | 目标值 | 测试命令 |
|------|--------|----------|
| **QPS** | > 500 请求/秒 | `python jmeter_test.py --duration 60 --users 10 --type encrypted` |
| **成功率** | > 99% | 同上 |
| **平均响应时间** | < 200ms | 同上 |
| **并发支持** | 30+ | `python jmeter_test.py --duration 60 --users 30 --type encrypted` |

---

## 📞 常见问题

### Q1: 测试时出现 "Address already in use" 错误

**A:** 端口 5000 已被占用。解决方法：

```bash
# 查找占用端口的进程
netstat -tlnp | grep 5000

# 杀死旧进程（假设 PID 是 12345）
kill -9 12345

# 重新启动服务器
nohup python app.py > server.log 2>&1 &
```

### Q2: 成功率很低（< 50%）

**A:** 可能原因：
1. 服务器性能不足 - 减少并发数
2. 网络延迟 - 在服务器上本地测试
3. 认证失败 - 检查用户名/密码或 API Key

### Q3: QPS 很低（< 100）

**A:** 可能原因：
1. 服务器配置低 - 使用更高配置的服务器
2. 磁盘 I/O 瓶颈 - 使用 SSD 或内存盘
3. Python 版本低 - 升级到 Python 3.8+

### Q4: 如何在本地电脑测试远程服务器？

```bash
# 在本地电脑运行（替换为你的服务器 IP）
python jmeter_test.py --url http://47.103.108.47:5000 --duration 60 --users 10 --username user1 --password user123 --type encrypted
```

---

## 🎓 学习资源

- **JMeter 官方文档**: https://jmeter.apache.org/
- **Flask 性能优化**: https://flask.palletsprojects.com/en/2.0.x/deploying/
- **Python 并发编程**: https://docs.python.org/3/library/concurrent.futures.html

---

**最后更新**: 2026-04-08  
**维护者**: 软件设计项目组
