# 第七周任务 - 快速验证命令清单

## 🚀 一键验证(复制粘贴即可)

### 1. MySQL数据库验证
```bash
ssh root@47.103.108.47 'mysql --version && echo "" && mysql -u root -padmin -e "USE sensor_project; SHOW TABLES;" 2>/dev/null'
```
**预期输出**: 
- MySQL 8.0.46
- 8个表名列表

---

### 2. 定时任务服务验证
```bash
ssh root@47.103.108.47 'systemctl status daily-statistics | head -5'
```
**预期输出**: 
- Active: active (running)

---

### 3. Flask API健康检查
```bash
curl http://47.103.108.47:5000/api/health | python3 -m json.tool
```
**预期输出**: 
- status: healthy

---

### 4. MySQL设备接口测试
```bash
curl http://47.103.108.47:5000/api/mysql/devices | python3 -m json.tool | head -20
```
**预期输出**: 
- code: 200
- 设备列表数据

---

### 5. MySQL统计接口测试
```bash
curl http://47.103.108.47:5000/api/mysql/statistics/latest | python3 -m json.tool
```
**预期输出**: 
- code: 200
- 统计数据(日期、记录数、活跃设备等)

---

### 6. 完整数据流测试
```bash
# 步骤1: 上传测试数据
curl -X POST http://47.103.108.47:5000/api/receive \
     -H "Content-Type: application/json" \
     -d '{"device_id": "TEST_001", "type": "skin", "data": {"moisture": 45}}'

# 步骤2: 等待2秒后查询MySQL统计
sleep 2
curl http://47.103.108.47:5000/api/mysql/statistics | python3 -m json.tool
```

---

## 📊 验收演示脚本(5分钟版)

### 开场白(30秒)
```
老师好,本周我们完成了数据存储层的全面升级:
1. MySQL 8.0部署并创建8个核心表
2. APScheduler定时任务每日自动统计
3. 12个Flask MySQL CRUD接口
4. 小程序功能规划(7大模块)

下面进行实时演示。
```

### 演示1: 数据库展示(1分钟)
```bash
# 在终端执行
ssh root@47.103.108.47 <<EOF
echo "=== MySQL版本 ==="
mysql --version

echo ""
echo "=== 8个数据表 ==="
mysql -u root -padmin -e "USE sensor_project; SHOW TABLES;" 2>/dev/null
EOF
```

### 演示2: 定时任务(1分钟)
```bash
# 查看服务状态
ssh root@47.103.108.47 'systemctl status daily-statistics | grep -E "(Active|Main PID)"'

# 查看最近日志
ssh root@47.103.108.47 'tail -3 /var/log/daily_statistics.log'
```

### 演示3: API接口(2分钟)
```bash
# 设备管理
echo "=== 获取设备列表 ==="
curl -s http://47.103.108.47:5000/api/mysql/devices | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'返回码: {d[\"code\"]}, 设备数: {d[\"data\"][\"total\"]}')"

# 统计数据
echo "=== 获取最新统计 ==="
curl -s http://47.103.108.47:5000/api/mysql/statistics/latest | python3 -c "import sys,json; d=json.load(sys.stdin); s=d['data']; print(f'日期: {s[\"stat_date\"]}, 记录数: {s[\"total_records\"]}, 活跃设备: {s[\"active_devices\"]}')"
```

### 演示4: 小程序规划(30秒)
```
打开 docs/小程序功能思维导图.md
展示7大核心模块和技術架构
```

### 总结(30秒)
```
所有任务100%完成:
✅ MySQL 8.0.46 + 8个表
✅ 定时任务每日自动统计
✅ 12个RESTful API接口
✅ 小程序功能完整规划

代码已部署到服务器,可以随时验收!
```

---

## 🔍 故障排查命令

### 如果MySQL接口404
```bash
# 检查Gunicorn进程
ssh root@47.103.108.47 'ps aux | grep gunicorn | grep -v grep'

# 重启服务
ssh root@47.103.108.47 'pkill -f gunicorn && sleep 2 && cd /root/course-project/week5/data-server/data-server && nohup gunicorn -c config/gunicorn_config.py app:app > /tmp/flask.log 2>&1 &'

# 等待5秒后测试
sleep 5
curl http://47.103.108.47:5000/api/mysql/devices
```

### 如果定时任务未运行
```bash
# 启动服务
ssh root@47.103.108.47 'systemctl start daily-statistics'

# 查看日志
ssh root@47.103.108.47 'journalctl -u daily-statistics -n 20'
```

### 如果数据库连接失败
```bash
# 检查MySQL服务
ssh root@47.103.108.47 'systemctl status mysqld'

# 测试连接
ssh root@47.103.108.47 'mysql -u root -padmin -e "SELECT 1"'
```

---

## 📝 验收检查清单

打印此清单,逐项勾选:

- [ ] MySQL 8.0.46已安装并运行
- [ ] sensor_project数据库已创建
- [ ] 8个数据表全部存在
- [ ] 定时任务服务状态为active
- [ ] Flask服务健康检查通过
- [ ] GET /api/mysql/devices 返回200
- [ ] GET /api/mysql/statistics 返回200
- [ ] 可以成功上传传感器数据
- [ ] 小程序功能思维导图文档完整
- [ ] WEEK7_VERIFICATION_REPORT.md已生成

**总计**: 10项,全部勾选即为验收通过 ✅

---

**最后更新**: 2026-04-25 16:36  
**维护人**: AI助手
