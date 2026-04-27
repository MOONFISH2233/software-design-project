# 第八周服务器部署 - 手动执行指南

## ⚠️ 当前状态

✅ **已完成**:
- 服务器SSH连接正常
- MySQL数据库 `software_design` 已创建
- week8目录已创建

❌ **待完成**:
- 上传新增代码文件（models.py, miniprogram_routes.py等）
- 安装缺失的Python依赖
- 执行15个表的建表SQL
- 更新app.py注册新路由
- 重启服务

---

## 📋 部署步骤（需手动执行）

由于网络限制无法自动推送代码，请按以下步骤手动操作：

### 步骤1: 安装缺失的Python依赖

```bash
ssh root@47.103.108.47

# 在服务器上执行
pip3 install flask-sqlalchemy apscheduler pyjwt pymysql
```

### 步骤2: 上传关键文件到服务器

**方法A: 使用WinSCP或FileZilla（推荐）**

1. 下载WinSCP: https://winscp.net/eng/download.php
2. 连接信息：
   - 主机: 47.103.108.47
   - 用户名: root
   - 密码: @Dierzu999
   - 端口: 22
3. 上传以下文件：

```
本地路径 → 服务器路径
d:\学习\软件设计\data-server\models.py → /root/course-project/data-server/models.py
d:\学习\软件设计\data-server\routes\miniprogram_routes.py → /root/course-project/data-server/routes/miniprogram_routes.py
d:\学习\软件设计\data-server\scripts\init_mysql_week8.sql → /root/course-project/data-server/scripts/init_mysql_week8.sql
d:\学习\软件设计\data-server\app.py → /root/course-project/data-server/app.py
```

**方法B: 使用SCP命令（在本地Windows PowerShell执行）**

```powershell
# 逐个上传文件
scp "d:\学习\软件设计\data-server\models.py" root@47.103.108.47:/root/course-project/data-server/models.py

scp "d:\学习\软件设计\data-server\routes\miniprogram_routes.py" root@47.103.108.47:/root/course-project/data-server/routes/miniprogram_routes.py

scp "d:\学习\软件设计\data-server\scripts\init_mysql_week8.sql" root@47.103.108.47:/root/course-project/data-server/scripts/init_mysql_week8.sql

scp "d:\学习\软件设计\data-server\app.py" root@47.103.108.47:/root/course-project/data-server/app.py
```

### 步骤3: 执行建表SQL

```bash
ssh root@47.103.108.47

# 在服务器上执行
mysql -u root -padmin software_design < /root/course-project/data-server/scripts/init_mysql_week8.sql

# 验证表创建
mysql -u root -padmin -e "USE software_design; SHOW TABLES;"
```

应该看到15个表。

### 步骤4: 验证代码语法

```bash
# 在服务器上执行
cd /root/course-project/data-server

# 检查models.py
python3 -m py_compile models.py

# 检查miniprogram_routes.py
python3 -m py_compile routes/miniprogram_routes.py

# 检查app.py
python3 -m py_compile app.py

echo "✅ 所有文件语法检查通过"
```

### 步骤5: 重启服务

```bash
# 重启Gunicorn
systemctl restart gunicorn-flask-data-server

# 检查服务状态
systemctl status gunicorn-flask-data-server

# 查看日志
tail -f /root/course-project/logs/server_*.log
```

### 步骤6: 测试API接口

```bash
# 健康检查
curl http://localhost:5000/api/health

# 测试用户注册
curl -X POST http://localhost:5000/api/miniprogram/user/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"123456","phone":"13800138000"}'

# 测试用户登录
curl -X POST http://localhost:5000/api/miniprogram/user/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"123456"}'
```

---

## 🔍 故障排查

### 问题1: Python依赖缺失

**症状**: `ModuleNotFoundError: No module named 'flask_sqlalchemy'`

**解决**:
```bash
pip3 install flask-sqlalchemy apscheduler pyjwt pymysql flask-httpauth flask-limiter cryptography
```

### 问题2: 数据库表不存在

**症状**: `Table 'software_design.xxx' doesn't exist`

**解决**:
```bash
# 重新执行建表脚本
mysql -u root -padmin software_design < /root/course-project/data-server/scripts/init_mysql_week8.sql
```

### 问题3: 服务启动失败

**症状**: `systemctl status gunicorn-flask-data-server` 显示 failed

**解决**:
```bash
# 查看详细错误日志
journalctl -u gunicorn-flask-data-server -n 50 --no-pager

# 检查语法错误
cd /root/course-project/data-server
python3 -m py_compile app.py
python3 -m py_compile models.py
python3 -m py_compile routes/miniprogram_routes.py
```

### 问题4: 端口被占用

**症状**: `Address already in use`

**解决**:
```bash
# 查找占用进程
lsof -i :5000

# 杀死进程
kill -9 <PID>

# 重启服务
systemctl restart gunicorn-flask-data-server
```

---

## ✅ 验收检查清单

完成部署后，请确认：

- [ ] 15个MySQL表全部创建成功
- [ ] Python依赖全部安装
- [ ] 代码语法检查通过
- [ ] Gunicorn服务正常运行
- [ ] API健康检查返回ok
- [ ] 用户注册接口可用
- [ ] 用户登录接口可用
- [ ] JWT Token认证成功
- [ ] 日志文件正常生成

---

## 📞 快速验证命令

```bash
# 一键验证脚本
ssh root@47.103.108.47 <<'VERIFY'
echo "=== 数据库表检查 ==="
mysql -u root -padmin -e "USE software_design; SHOW TABLES;" 2>/dev/null | wc -l

echo ""
echo "=== 服务状态检查 ==="
systemctl is-active gunicorn-flask-data-server

echo ""
echo "=== API健康检查 ==="
curl -s http://localhost:5000/api/health

echo ""
echo "=== 日志文件检查 ==="
ls -lh /root/course-project/logs/server_*.log 2>/dev/null | tail -1

echo ""
echo "=== Python依赖检查 ==="
pip3 list 2>/dev/null | grep -E "sqlalchemy|apscheduler|jwt|pymysql" | wc -l
VERIFY
```

---

## 📝 注意事项

1. **文件上传顺序**: 先上传models.py，再上传routes，最后上传app.py
2. **语法检查**: 每次上传后立即执行py_compile检查
3. **备份原文件**: 重要文件上传前先备份
4. **日志监控**: 重启服务后实时查看日志

---

**文档版本**: v1.0  
**创建时间**: 2026-04-27  
**服务器**: 47.103.108.47
