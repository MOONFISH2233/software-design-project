# 📖 完整操作指南 - 第六周MongoDB项目

## 🎯 快速开始

### 本地模拟器运行（Windows）

#### 方法1：双击批处理文件（推荐）
```
双击: d:\学习\软件设计\启动模拟器.bat
```

#### 方法2：命令行运行
```powershell
# PowerShell 或 CMD
cd "d:\学习\软件设计\data-server"
python examples/simulator_mq.py
```

**注意**: 
- ✅ 必须在 `data-server` 目录下运行
- ✅ 确保Redis已安装并运行
- ❌ 不要在其他目录运行，否则会找不到 `mq_utils` 模块

---

### 服务器端操作（Linux）

#### 1. SSH登录
```bash
ssh root@47.103.108.47
# 密码: @Dierzu999
```

#### 2. MongoDB操作命令

##### ❌ 错误命令（不要用）
```bash
mongo sensor_data  # MongoDB 6.0+ 已废弃此命令
```

##### ✅ 正确命令
```bash
# 方式1: 使用 mongosh（推荐）
mongosh mongodb://localhost:27017/sensor_data

# 进入后执行
db.skin_sensor.countDocuments()           # 查看记录数
db.skin_sensor.find().limit(5).pretty()   # 查看前5条
show collections                           # 查看所有集合
exit                                       # 退出
```

```bash
# 方式2: 一行命令（不进入交互模式）
mongosh --eval "db = db.getSiblingDB('sensor_data'); db.skin_sensor.countDocuments()"

# 或者
mongosh sensor_data --eval "db.skin_sensor.find().limit(5)"
```

#### 3. 运行监控脚本
```bash
# 进入项目目录
cd /root/course-project/week5/data-server/data-server

# 运行监控
python3 scripts/mongodb_monitor.py
```

#### 4. 查看备份
```bash
ls -lh /backup/mongodb/
```

#### 5. 查看定时任务
```bash
crontab -l
```

---

## ⚠️ 常见错误及解决

### 错误1: ModuleNotFoundError: No module named 'mq_utils'

**原因**: 不在正确的目录运行

**解决**:
```powershell
# Windows
cd "d:\学习\软件设计\data-server"
python examples/simulator_mq.py
```

### 错误2: bash: mongo: command not found

**原因**: MongoDB 6.0+ 使用 `mongosh` 而不是 `mongo`

**解决**:
```bash
# 使用 mongosh
mongosh sensor_data

# 或者安装旧版mongo shell（不推荐）
```

### 错误3: 在Windows PowerShell中执行Linux命令

**错误示例**:
```powershell
cd /root/course-project/...  # ❌ 这是Linux路径
python3 scripts/mongodb_monitor.py  # ❌ 这是服务器上的文件
```

**正确做法**:
- Windows本地操作 → 在Windows路径下
- 服务器操作 → 先SSH登录，再执行Linux命令

### 错误4: .bat文件中文乱码

**原因**: 编码问题

**解决**: 已修复，现在使用英文

---

## 📋 完整演示流程

### 场景1：向老师展示（推荐流程）

#### Step 1: 准备阶段（提前5分钟）
```powershell
# 1. 打开两个终端窗口

# 窗口1 - 本地模拟器
cd "d:\学习\软件设计\data-server"

# 窗口2 - 服务器SSH
ssh root@47.103.108.47
# 输入密码: @Dierzu999
```

#### Step 2: 开始演示

**在窗口2（服务器）执行**:
```bash
# 检查MongoDB服务
systemctl status mongod

# 进入MongoDB
mongosh sensor_data

# 查看当前记录数（记下数字）
db.skin_sensor.countDocuments()
```

**在窗口1（本地）执行**:
```powershell
python examples/simulator_mq.py
```

**回到窗口2（服务器）执行**:
```javascript
// 再次查看记录数，应该增加了
db.skin_sensor.countDocuments()

// 查看最新数据
db.skin_sensor.find().sort({timestamp: -1}).limit(3).pretty()
```

**展示监控报告**:
```bash
exit  # 退出mongosh
python3 scripts/mongodb_monitor.py
```

**展示备份**:
```bash
ls -lh /backup/mongodb/
crontab -l
```

---

### 场景2：日常开发调试

#### 启动所有服务
```bash
# 1. SSH登录服务器
ssh root@47.103.108.47

# 2. 检查服务状态
systemctl status mongod
systemctl status redis

# 3. 查看日志
tail -f /var/log/mongodb/mongod.log
```

#### 发送测试数据
```powershell
# 本地Windows
cd "d:\学习\软件设计\data-server"
python examples/simulator_mq.py
```

#### 验证数据
```bash
# 服务器Linux
mongosh sensor_data --eval "db.skin_sensor.countDocuments()"
```

---

## 🔑 关键命令速查表

### Windows本地命令

| 操作 | 命令 |
|------|------|
| 运行模拟器 | `cd "d:\学习\软件设计\data-server"` <br> `python examples/simulator_mq.py` |
| 双击启动 | 运行 `启动模拟器.bat` |
| 查看Git | `git log --oneline -5` |

### Linux服务器命令

| 操作 | 命令 |
|------|------|
| SSH登录 | `ssh root@47.103.108.47` |
| MongoDB连接 | `mongosh sensor_data` |
| 查看记录数 | `db.skin_sensor.countDocuments()` |
| 查看数据 | `db.skin_sensor.find().limit(5).pretty()` |
| 运行监控 | `cd /root/course-project/week5/data-server/data-server` <br> `python3 scripts/mongodb_monitor.py` |
| 查看备份 | `ls -lh /backup/mongodb/` |
| 查看定时任务 | `crontab -l` |
| 手动备份 | `./scripts/mongodb_backup.sh` |
| 性能测试 | `python3 scripts/performance_comparison_test.py 500 50` |

---

## 📊 飞书汇报材料清单

### 必传文档（4份）
1. ✅ `docs/第六周飞书汇报文档.docx` - 主汇报文档
2. ✅ `docs/数据库设计说明书.docx` - 专业设计
3. ✅ `docs/第六周工作总结与MongoDB使用指南.docx` - 技术手册
4. ✅ `docs/API接口数据传输参数表.xlsx` - 接口规范

### 必备截图（至少5张）

#### 截图1: Git提交记录
```powershell
cd "d:\学习\软件设计\data-server"
git log --oneline -3
```
**输出**:
```
3f3f515 (HEAD -> week6) 添加MongoDB运维工具脚本
ccc53ae 第六周任务：MongoDB数据库集成
ff0a1be (origin/week5, week5) docs: 添加测试平台升级总结文档
```

#### 截图2: MongoDB服务状态
```bash
ssh root@47.103.108.47 "systemctl is-active mongod"
```
**输出**:
```
active
```

#### 截图3: 监控报告
```bash
ssh root@47.103.108.47 "python3 /root/course-project/week5/data-server/data-server/scripts/mongodb_monitor.py"
```
**输出**:
```
🔗 连接数: 当前3, 可用51197, 使用率0.01%
💾 内存使用: 常驻126MB
💿 磁盘使用: 数据0.0MB, 索引0.36MB
🐢 慢查询: 0个
✅ 所有指标正常
```

#### 截图4: 备份文件
```bash
ssh root@47.103.108.47 "ls -lh /backup/mongodb/"
```
**输出**:
```
drwxr-xr-x 3 root root 4.0K Apr 24 09:13 20260424_091332
```

#### 截图5: 定时任务
```bash
ssh root@47.103.108.47 "crontab -l"
```
**输出**:
```
0 2 * * * ... mongodb_backup.sh
*/5 * * * * ... mongodb_monitor.py
```

---

## 💡 给老师的演示脚本（5-8分钟）

### 开场白（30秒）
```
老师好，本周我们完成了MongoDB数据库集成和运维体系建设。

主要成果：
1. 安装了MongoDB 6.0.27并设计了3个集合
2. 改造了代码支持双写模式和故障转移
3. 建立了自动化备份和监控告警系统
4. 完成了性能测试，写入QPS提升34.9%

下面我现场演示一下。
```

### 演示步骤

#### 1. 展示GitHub（1分钟）
- 打开浏览器
- 访问: https://github.com/MOONFISH2233/software-design-project
- 切换到 `week6` 分支
- 展示最新提交

#### 2. SSH登录服务器（1分钟）
```bash
ssh root@47.103.108.47
# 输入密码

systemctl status mongod
# 显示 active (running)
```

#### 3. 运行本地模拟器（2分钟）
```powershell
# 新开终端
cd "d:\学习\软件设计\data-server"
python examples/simulator_mq.py
```

同时在服务器观察：
```bash
mongosh sensor_data
db.skin_sensor.countDocuments()
# 看到数字在增长
```

#### 4. 展示监控（1分钟）
```bash
exit  # 退出mongosh
python3 scripts/mongodb_monitor.py
# 展示所有指标正常
```

#### 5. 展示备份（1分钟）
```bash
ls -lh /backup/mongodb/
crontab -l
# 展示每天2点备份，每5分钟监控
```

### 结束语（30秒）
```
以上就是本周的工作成果。我们不仅完成了MongoDB集成，
还建立了完整的运维体系。

所有代码已提交到GitHub的week6分支，文档也已整理完成。

老师您有什么问题吗？
```

---

## ❓ 常见问题FAQ

### Q1: 为什么选择MongoDB而不是MySQL？
**A**: 
- 数据结构灵活：传感器数据是半结构化JSON
- 写入性能更好：实测快34.9%
- 扩展性强：支持水平分片

### Q2: MongoDB挂了怎么办？
**A**: 
三层保障：
1. 故障转移：自动降级到文件存储
2. 监控告警：每5分钟检查
3. 定期备份：每天凌晨2点

### Q3: 如何保证数据安全？
**A**: 
- 双写冗余：同时写入MongoDB和文件
- 每日备份：保留7天
- 实时监控：异常立即发现

### Q4: 性能瓶颈在哪里？
**A**: 
- 当前瓶颈：网络IO和磁盘IO
- 优化方案：SSD硬盘、Redis缓存、分片集群

---

## 🎯 最后检查清单

在向老师汇报前，确认：

- [ ] 本地模拟器可以正常运行
- [ ] SSH连接服务器正常
- [ ] MongoDB服务正在运行
- [ ] 监控脚本可以执行
- [ ] 备份文件存在
- [ ] 4个Word/Excel文档已生成
- [ ] 至少5张截图已准备
- [ ] GitHub链接可访问
- [ ] 演示流程已演练1-2遍

---

**祝汇报顺利！🎉**

如有问题，随时问我！
