# 第八周代码部署指南

## 📋 部署前准备

### 1. 本地Git推送（可选）
如果GitHub可以访问，执行：
```bash
cd "d:\学习\软件设计"
git push origin week8
```

如果无法推送到GitHub，可以直接通过SCP上传到服务器。

---

## 🚀 方法一：通过SSH直接部署到服务器（推荐）

### 步骤1: 连接服务器
```bash
ssh root@47.103.108.47
# 密码: @Dierzu999
```

### 步骤2: 创建week8目录并拉取代码
```bash
# 在服务器上执行
cd /root/course-project
mkdir -p week8
cd week8

# 从GitHub克隆（如果可以访问）
git clone -b week8 https://github.com/MOONFISH2233/software-design-project.git .

# 或者从本地上传（如果GitHub无法访问）
# 在本地Windows执行：
# scp -r "d:\学习\软件设计\*" root@47.103.108.47:/root/course-project/week8/
```

### 步骤3: 执行部署脚本
```bash
cd /root/course-project/week8/data-server

# 赋予执行权限
chmod +x scripts/deploy_week8.sh
chmod +x scripts/organize_project.sh

# 执行部署
bash scripts/deploy_week8.sh
```

部署脚本会自动完成：
- ✅ 安装Python依赖
- ✅ 初始化MySQL数据库（15个表）
- ✅ 整理项目文件结构
- ✅ 重启Gunicorn服务
- ✅ 启动定时任务
- ✅ 验证部署状态

---

## 📦 方法二：手动部署

### 1. 上传代码到服务器

**在本地Windows PowerShell执行：**
```powershell
# 压缩项目
Compress-Archive -Path "d:\学习\软件设计\*" -DestinationPath "d:\学习\software-design-week8.zip"

# 上传到服务器
scp "d:\学习\software-design-week8.zip" root@47.103.108.47:/root/course-project/

# SSH登录服务器解压
ssh root@47.103.108.47
cd /root/course-project
mkdir -p week8
unzip software-design-week8.zip -d week8/
```

### 2. 初始化MySQL数据库

```bash
# SSH登录服务器
ssh root@47.103.108.47

# 执行建表脚本
mysql -u root -padmin < /root/course-project/week8/data-server/scripts/init_mysql_week8.sql

# 验证表创建
mysql -u root -padmin -e "USE software_design; SHOW TABLES;"
```

应该看到15个表：
```
+---------------------------+
| Tables_in_software_design |
+---------------------------+
| devices                   |
| skin_sensor_data          |
| environment_sensor_data   |
| daily_statistics          |
| users                     |
| user_profiles             |
| health_reports            |
| device_bindings           |
| community_posts           |
| post_comments             |
| notifications             |
| user_points               |
| skincare_products         |
| user_skincare_records     |
| system_configs            |
+---------------------------+
```

### 3. 安装Python依赖

```bash
pip3 install flask flask-sqlalchemy apscheduler pyjwt cryptography pymongo pymysql flask-httpauth flask-limiter gunicorn
```

### 4. 整理项目文件结构

```bash
cd /root/course-project/week8/data-server
bash scripts/organize_project.sh
```

### 5. 重启应用服务

```bash
# 重启Gunicorn
systemctl restart gunicorn-flask-data-server

# 检查服务状态
systemctl status gunicorn-flask-data-server
```

### 6. 启动定时任务

**选项A: 使用Systemd服务（推荐）**

创建服务文件：
```bash
sudo nano /etc/systemd/system/daily-statistics.service
```

内容：
```ini
[Unit]
Description=Daily Statistics Task
After=network.target mysql.service mongod.service

[Service]
Type=simple
User=root
WorkingDirectory=/root/course-project/week8/data-server
ExecStart=/usr/bin/python3 tasks/daily_statistics.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/daily_statistics.log
StandardError=append:/var/log/daily_statistics.log

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable daily-statistics
sudo systemctl start daily-statistics
sudo systemctl status daily-statistics
```

**选项B: 后台进程方式**

```bash
nohup python3 /root/course-project/week8/data-server/tasks/daily_statistics.py > /var/log/daily_statistics.log 2>&1 &
```

---

## ✅ 验证部署

### 1. 检查应用健康状态
```bash
curl http://localhost:5000/api/health
```

预期响应：
```json
{"status": "ok", "timestamp": "2026-04-27T..."}
```

### 2. 测试API接口

**注册用户：**
```bash
curl -X POST http://localhost:5000/api/miniprogram/user/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Test@123",
    "phone": "13800138000",
    "nickname": "测试用户"
  }'
```

**登录获取Token：**
```bash
curl -X POST http://localhost:5000/api/miniprogram/user/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Test@123"
  }'
```

保存返回的token，用于后续请求。

**查询用户信息（需要Token）：**
```bash
curl -X GET http://localhost:5000/api/miniprogram/user/profile \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 3. 检查定时任务日志
```bash
tail -f /var/log/daily_statistics.log
```

应该看到类似输出：
```
2026-04-27 02:00:00 - daily_statistics - INFO - ✅ 定时任务初始化完成
2026-04-27 02:00:00 - daily_statistics - INFO - ✅ 定时任务调度器已启动
2026-04-27 02:00:00 - daily_statistics - INFO - 📅 每日凌晨2点自动计算统计数据
```

### 4. 查看应用日志
```bash
tail -f /root/course-project/logs/server_*.log
```

---

## 🔧 常见问题排查

### 问题1: MySQL连接失败
**症状**: `Can't connect to MySQL server`

**解决**:
```bash
# 检查MySQL服务状态
systemctl status mysqld

# 启动MySQL
systemctl start mysqld

# 检查端口
netstat -tlnp | grep 3306
```

### 问题2: MongoDB连接失败
**症状**: `pymongo.errors.ServerSelectionTimeoutError`

**解决**:
```bash
# 检查MongoDB服务状态
systemctl status mongod

# 启动MongoDB
systemctl start mongod
```

### 问题3: 端口被占用
**症状**: `Address already in use`

**解决**:
```bash
# 查找占用5000端口的进程
lsof -i :5000

# 杀死进程
kill -9 <PID>

# 重启Gunicorn
systemctl restart gunicorn-flask-data-server
```

### 问题4: Python依赖缺失
**症状**: `ModuleNotFoundError: No module named 'xxx'`

**解决**:
```bash
cd /root/course-project/week8/data-server
pip3 install -r requirements.txt

# 如果没有requirements.txt，手动安装
pip3 install flask flask-sqlalchemy apscheduler pyjwt cryptography pymongo pymysql
```

### 问题5: 定时任务未执行
**症状**: 日志文件中没有定时任务记录

**解决**:
```bash
# 检查服务状态
systemctl status daily-statistics

# 查看系统日志
journalctl -u daily-statistics -f

# 手动触发一次测试
python3 /root/course-project/week8/data-server/tasks/daily_statistics.py
```

---

## 📊 监控和维护

### 查看服务状态
```bash
# Gunicorn服务
systemctl status gunicorn-flask-data-server

# 定时任务
systemctl status daily-statistics

# MongoDB
systemctl status mongod

# MySQL
systemctl status mysqld
```

### 查看日志
```bash
# 应用日志
tail -f /root/course-project/logs/server_*.log

# 定时任务日志
tail -f /var/log/daily_statistics.log

# 系统日志
journalctl -u gunicorn-flask-data-server -f
journalctl -u daily-statistics -f
```

### 性能监控
```bash
# CPU和内存使用
top

# 磁盘空间
df -h

# 网络连接
netstat -tlnp
```

### 数据库备份
```bash
# MySQL备份
mysqldump -u root -padmin software_design > /backup/mysql_backup_$(date +%Y%m%d).sql

# MongoDB备份
mongodump --db sensor_data --out /backup/mongodb_backup_$(date +%Y%m%d)
```

---

## 🎯 部署检查清单

- [ ] 代码已上传到服务器
- [ ] MySQL数据库已初始化（15个表）
- [ ] Python依赖已安装
- [ ] 项目文件结构已整理
- [ ] Gunicorn服务已启动
- [ ] 定时任务已启动
- [ ] API健康检查通过
- [ ] 测试接口调用成功
- [ ] 日志文件正常生成
- [ ] 数据库连接正常

---

## 📞 技术支持

如遇到问题，请检查：
1. 服务器日志文件
2. 数据库连接状态
3. 网络连通性
4. 依赖包版本兼容性

**联系方式**: 
- GitHub Issues: https://github.com/MOONFISH2233/software-design-project/issues
- 服务器: 47.103.108.47

---

**文档版本**: v1.0  
**最后更新**: 2026-04-27
