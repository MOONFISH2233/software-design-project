# Flask服务持久化部署与管理指南

## 📋 概述

Flask后端服务已通过**systemd系统服务**实现持久化部署，确保：
- ✅ **开机自动启动** - 服务器重启后自动恢复
- ✅ **进程崩溃自动重启** - 5秒后自动重新启动
- ✅ **7x24小时运行** - 无需人工维护
- ✅ **统一日志管理** - 集中记录所有日志

---

## 🔧 服务配置详情

### 服务文件位置
```
/etc/systemd/system/flask-data-server.service
```

### 关键配置
```ini
[Unit]
Description=Flask Data Server for Skin Health Monitoring
After=network.target mysqld.service mongod.service

[Service]
Type=simple
User=root
WorkingDirectory=/root/course-project/data-server
ExecStart=/root/course-project/data-server/gunicorn_start.sh
Restart=always          # 总是自动重启
RestartSec=5            # 重启间隔5秒
MemoryMax=2G            # 内存限制2GB

[Install]
WantedBy=multi-user.target  # 开机自启
```

### Gunicorn配置
```bash
#!/bin/bash
cd /root/course-project/data-server
exec gunicorn \
    --workers 4 \              # 4个工作进程
    --bind 0.0.0.0:5000 \      # 监听5000端口
    --timeout 120 \            # 超时时间120秒
    wsgi:app                   # WSGI入口
```

---

## 📝 常用管理命令

### 1. 查看服务状态
```bash
systemctl status flask-data-server
```

**输出示例**：
```
● flask-data-server.service - Flask Data Server for Skin Health Monitoring
   Loaded: loaded (/etc/systemd/system/flask-data-server.service; enabled)
   Active: active (running) since Fri 2026-05-08 14:36:26 CST
 Main PID: 1714185 (python3)
    Tasks: 6
   Memory: 86.3M
```

### 2. 重启服务
```bash
systemctl restart flask-data-server
```

**使用场景**：
- 代码更新后需要重启
- 服务异常时手动重启
- 修改配置文件后生效

### 3. 停止服务
```bash
systemctl stop flask-data-server
```

### 4. 启动服务
```bash
systemctl start flask-data-server
```

### 5. 禁用开机自启
```bash
systemctl disable flask-data-server
```

### 6. 启用开机自启
```bash
systemctl enable flask-data-server
```

---

## 📊 日志管理

### 1. 实时查看日志
```bash
# 查看应用日志
journalctl -u flask-data-server -f

# 查看最近100行
journalctl -u flask-data-server -n 100

# 查看今天的日志
journalctl -u flask-data-server --since today
```

### 2. 日志文件位置
```bash
# 标准输出日志
/var/log/flask-server.log

# 错误日志
/var/log/flask-server-error.log

# Gunicorn访问日志
/var/log/flask-access.log

# Gunicorn错误日志
/var/log/flask-error.log
```

### 3. 查看日志文件大小
```bash
ls -lh /var/log/flask*.log
```

### 4. 清空日志（谨慎使用）
```bash
> /var/log/flask-server.log
> /var/log/flask-server-error.log
```

---

## 🔍 故障排查

### 问题1：服务无法启动

**检查步骤**：
```bash
# 1. 查看详细错误日志
journalctl -u flask-data-server -xe

# 2. 检查端口是否被占用
netstat -tlnp | grep 5000

# 3. 检查依赖服务是否正常
systemctl status mysqld
systemctl status mongod

# 4. 手动测试启动
cd /root/course-project/data-server
python3 wsgi.py
```

**常见原因**：
- 端口5000被占用 → 杀死旧进程 `pkill -9 python`
- MySQL/MongoDB未启动 → 启动依赖服务
- 代码语法错误 → 检查最新修改的代码

### 问题2：API响应缓慢

**检查步骤**：
```bash
# 1. 查看CPU和内存使用
top -p $(pgrep -f gunicorn)

# 2. 查看工作进程数量
ps aux | grep gunicorn | wc -l

# 3. 检查数据库连接
mysql -u root -padmin -e "SHOW PROCESSLIST;"
```

**优化方案**：
- 增加Gunicorn工作进程数（修改gunicorn_start.sh）
- 优化数据库查询
- 添加Redis缓存

### 问题3：内存占用过高

**检查步骤**：
```bash
# 1. 查看内存使用
systemctl status flask-data-server | grep Memory

# 2. 查看具体进程
ps aux --sort=-%mem | grep python | head -5
```

**解决方案**：
- 调整MemoryMax限制（当前2GB）
- 减少Gunicorn工作进程数
- 检查是否有内存泄漏

---

## 🚀 性能监控

### 1. 实时监控命令
```bash
# 综合监控脚本
watch -n 5 'echo "=== 服务状态 ===" && systemctl is-active flask-data-server && echo "" && echo "=== 内存使用 ===" && systemctl show flask-data-server --property=MemoryCurrent && echo "" && echo "=== 进程数 ===" && ps aux | grep gunicorn | grep -v grep | wc -l'
```

### 2. 创建监控脚本
```bash
cat > /root/monitor_flask.sh << 'BASH'
#!/bin/bash
while true; do
    STATUS=$(systemctl is-active flask-data-server)
    if [ "$STATUS" != "active" ]; then
        echo "$(date): 服务异常，尝试重启..." >> /var/log/flask-monitor.log
        systemctl restart flask-data-server
    fi
    sleep 60
done
BASH

chmod +x /root/monitor_flask.sh
nohup /root/monitor_flask.sh &
```

---

## 📅 维护计划

### 每日检查
```bash
# 检查服务状态
systemctl status flask-data-server --no-pager

# 检查磁盘空间
df -h /var/log

# 检查日志文件大小
du -sh /var/log/flask*.log
```

### 每周维护
```bash
# 清理旧日志（保留7天）
find /var/log -name "flask*.log.*" -mtime +7 -delete

# 重启服务（释放内存）
systemctl restart flask-data-server
```

### 每月维护
```bash
# 备份数据库
mysqldump -u root -padmin software_design > /backup/mysql_$(date +%Y%m%d).sql

# 检查系统更新
yum check-update
```

---

## 🎯 最佳实践

### 1. 代码更新流程
```bash
# 1. 上传新代码
scp app.py routes/*.py root@47.103.108.47:/root/course-project/data-server/

# 2. 重启服务
ssh root@47.103.108.47 "systemctl restart flask-data-server"

# 3. 验证服务
ssh root@47.103.108.47 "curl -s http://localhost:5000/api/health"
```

### 2. 紧急回滚
```bash
# 如果新版本有问题，快速回滚
ssh root@47.103.108.47 << 'SSH'
cd /root/course-project/data-server
git checkout HEAD~1  # 回退到上一个版本
systemctl restart flask-data-server
SSH
```

### 3. 健康检查自动化
```bash
# 添加到crontab，每5分钟检查一次
echo "*/5 * * * * curl -sf http://localhost:5000/api/health || systemctl restart flask-data-server" | crontab -
```

---

## 📞 应急处理

### 服务完全无法启动
```bash
# 1. 停止systemd服务
systemctl stop flask-data-server

# 2. 手动启动调试
cd /root/course-project/data-server
python3 wsgi.py 2>&1 | tee /tmp/debug.log

# 3. 根据错误信息修复
# 4. 重新启动systemd服务
systemctl start flask-data-server
```

### 数据丢失风险
```bash
# 立即备份数据库
mysqldump -u root -padmin software_design > /backup/emergency_backup_$(date +%Y%m%d_%H%M%S).sql
mongodump --db skin_health --out /backup/mongo_emergency_$(date +%Y%m%d_%H%M%S)
```

---

## 🎊 总结

✅ **Flask服务已实现持久化部署**
- systemd管理，开机自启
- 自动重启，7x24小时运行
- 统一日志，便于排查
- 资源限制，防止崩溃

✅ **随时可用**
- 任何时候访问 http://47.103.108.47/ 都能正常使用
- 服务器重启后自动恢复
- 进程崩溃后5秒内自动重启

✅ **易于维护**
- 简单的systemctl命令管理
- 清晰的日志记录
- 完善的监控方案
