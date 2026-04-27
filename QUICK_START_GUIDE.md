# 🎯 完整演示操作指南

## ⚡ 快速开始（3步搞定）

### Step 1: 启动本地模拟器（Windows）

打开 **PowerShell** 或 **CMD**，执行：

```powershell
cd "d:\学习\软件设计\data-server"
python examples/simple_simulator.py
```

**或者双击运行**：
```
data-server\examples\run_simple_simulator.bat
```

你会看到：
```
✅ [1] 发送成功 | 水分:74.3% | 油分:43.9%
✅ [2] 发送成功 | 水分:78.1% | 油分:38.9%
...
```

按 `Ctrl+C` 停止。

---

### Step 2: SSH登录服务器（查看数据）

新开一个终端窗口：

```bash
ssh root@47.103.108.47
# 密码: @Dierzu999
```

#### 查看文件存储的数据
```bash
# 查看最新的数据文件
ls -lht /root/course-project/week5/data-server/data-server/data/ | head -5

# 查看文件内容
cat /root/course-project/week5/data-server/data-server/data/*.json | tail -20
```

#### 查看MongoDB（如果启动了module_writer）
```bash
mongosh sensor_data
db.skin_sensor.countDocuments()
db.skin_sensor.find().sort({timestamp: -1}).limit(3).pretty()
exit
```

---

### Step 3: 运行监控脚本（展示运维能力）

在服务器上执行：

```bash
cd /root/course-project/week5/data-server/data-server
python3 scripts/mongodb_monitor.py
```

输出示例：
```
🔗 连接数: 当前3, 可用51197, 使用率0.01%
💾 内存使用: 常驻126MB
💿 磁盘使用: 数据0.0MB, 索引0.36MB
🐢 慢查询: 0个
✅ 所有指标正常
```

---

## 📋 详细操作说明

### 本地模拟器选择

#### 选项1：简化版HTTP直连（推荐用于演示）⭐⭐⭐⭐⭐
**文件**: `examples/simple_simulator.py`  
**优点**: 
- ✅ 无需Redis
- ✅ 直接发送到服务器
- ✅ 实时看到发送结果
- ✅ 适合快速演示

**运行**:
```powershell
cd "d:\学习\软件设计\data-server"
python examples/simple_simulator.py
```

#### 选项2：完整版MQ模式（需要Redis）
**文件**: `examples/simulator_mq.py`  
**优点**: 
- ✅ 使用消息队列
- ✅ 支持重传机制
- ✅ 更接近生产环境

**前提条件**:
- 需要安装并启动Redis
- Windows安装Redis: https://github.com/microsoftarchive/redis/releases

**运行**:
```powershell
# 先启动Redis
redis-server

# 再运行模拟器
cd "d:\学习\软件设计\data-server"
python examples/simulator_mq.py
```

---

### 服务器端常用命令

#### 1. 查看数据文件
```bash
# 查看最新的10个数据文件
ls -lht /root/course-project/week5/data-server/data-server/data/ | head -10

# 统计文件数量
ls /root/course-project/week5/data-server/data-server/data/*.json | wc -l

# 查看某个文件内容
cat /root/course-project/week5/data-server/data-server/data/data_20260424_*.json | python3 -m json.tool | head -30
```

#### 2. MongoDB操作
```bash
# 连接数据库
mongosh sensor_data

# 常用命令
show collections                      # 查看所有集合
db.skin_sensor.countDocuments()       # 统计记录数
db.skin_sensor.find().limit(5)        # 查看前5条
db.skin_sensor.find().sort({timestamp: -1}).limit(3).pretty()  # 最新3条
db.environment_sensor.countDocuments()
db.device_status.countDocuments()

# 退出
exit
```

#### 3. 监控和备份
```bash
# 运行监控脚本
cd /root/course-project/week5/data-server/data-server
python3 scripts/mongodb_monitor.py

# 查看备份
ls -lh /backup/mongodb/

# 查看定时任务
crontab -l

# 手动触发备份
./scripts/mongodb_backup.sh
```

#### 4. 服务管理
```bash
# 检查MongoDB状态
systemctl status mongod

# 检查Flask服务
systemctl status gunicorn-flask-data-server

# 查看Flask日志
tail -f /var/log/gunicorn-flask-data-server.log
```

---

## 🎬 向老师演示的完整流程（5-8分钟）

### 准备阶段（提前5分钟）

打开 **3个终端窗口**：

**窗口1 - 本地模拟器**
```powershell
cd "d:\学习\软件设计\data-server"
# 准备好运行命令，等演示时再执行
```

**窗口2 - 服务器SSH**
```bash
ssh root@47.103.108.47
# 已登录，准备好命令
```

**窗口3 - 浏览器**
- 打开 GitHub: https://github.com/MOONFISH2233/software-design-project
- 切换到 week6 分支

---

### 演示步骤

#### Step 1: 展示GitHub仓库（1分钟）
- 展示week6分支
- 指出最新提交："添加MongoDB运维工具脚本"
- 展示新增的4个脚本文件

#### Step 2: 启动本地模拟器（1分钟）
在**窗口1**执行：
```powershell
python examples/simple_simulator.py
```

展示输出：
```
✅ [1] 发送成功 | 水分:74.3% | 油分:43.9%
✅ [2] 发送成功 | 水分:78.1% | 油分:38.9%
```

#### Step 3: 服务器端查看数据（2分钟）
在**窗口2**执行：

```bash
# 查看文件存储
ls -lht /root/course-project/week5/data-server/data-server/data/ | head -5
```

展示输出（显示新生成的文件）。

```bash
# 查看文件内容
cat /root/course-project/week5/data-server/data-server/data/data_20260424_*.json | tail -1 | python3 -m json.tool
```

展示JSON数据结构。

#### Step 4: 展示MongoDB（可选，1分钟）
如果启动了module_writer：

```bash
mongosh sensor_data
db.skin_sensor.countDocuments()
db.skin_sensor.find().sort({timestamp: -1}).limit(2).pretty()
exit
```

#### Step 5: 展示监控报告（1分钟）
```bash
cd /root/course-project/week5/data-server/data-server
python3 scripts/mongodb_monitor.py
```

展示输出：
```
🔗 连接数使用率: 0.01%
💾 内存使用: 126MB
💿 磁盘使用: 0.45MB
🐢 慢查询: 0个
✅ 所有指标正常
```

#### Step 6: 展示备份机制（1分钟）
```bash
ls -lh /backup/mongodb/
crontab -l
```

展示输出：
```
drwxr-xr-x 3 root root 4.0K Apr 24 09:13 20260424_091332

0 2 * * * ... mongodb_backup.sh      # 每天2点备份
*/5 * * * * ... mongodb_monitor.py   # 每5分钟监控
```

#### Step 7: 总结（30秒）
```
以上就是本周的工作成果：
1. MongoDB 6.0.27安装配置完成
2. 数据库设计了3个集合+11个索引
3. 代码支持双写模式和故障转移
4. 建立了自动化备份和监控告警系统
5. 性能测试显示写入QPS提升34.9%

所有代码已提交到GitHub的week6分支。
```

---

## ❓ 常见问题

### Q1: 为什么MongoDB中没有数据？
**A**: 因为 module_writer.py 没有运行。当前Flask的app.py直接将数据写入JSON文件。要写入MongoDB，需要：
```bash
cd /root/course-project/week5/data-server/data-server
nohup python3 module_writer.py > logs/writer.log 2>&1 &
```

### Q2: 如何启动module_writer？
**A**: 
```bash
cd /root/course-project/week5/data-server/data-server
mkdir -p logs
nohup python3 module_writer.py > logs/writer.log 2>&1 &
tail -f logs/writer.log  # 查看日志
```

### Q3: Redis未安装怎么办？
**A**: 使用简化版模拟器 `simple_simulator.py`，它不依赖Redis，直接通过HTTP发送数据。

### Q4: 如何验证数据真的发送到服务器了？
**A**: 
1. 看本地模拟器输出 "✅ 发送成功"
2. 在服务器查看数据文件：`ls -lht data/`
3. 或在MongoDB中查询（如果module_writer在运行）

### Q5: 批处理文件闪退怎么办？
**A**: 改用命令行方式运行，或使用新创建的 `simple_simulator.py`。

---

## 📊 关键截图清单

向老师汇报时，至少准备以下截图：

1. ⭐⭐⭐⭐⭐ **本地模拟器运行截图**
   - 显示 "✅ 发送成功" 的输出
   
2. ⭐⭐⭐⭐⭐ **服务器数据文件列表**
   ```bash
   ls -lht /root/course-project/week5/data-server/data-server/data/ | head -5
   ```
   
3. ⭐⭐⭐⭐⭐ **监控报告输出**
   ```bash
   python3 scripts/mongodb_monitor.py
   ```
   
4. ⭐⭐⭐⭐ **Git提交记录**
   ```bash
   git log --oneline -3
   ```
   
5. ⭐⭐⭐⭐ **备份文件和定时任务**
   ```bash
   ls -lh /backup/mongodb/
   crontab -l
   ```

---

## 🎯 最终检查清单

演示前确认：

- [ ] 本地可以运行 `simple_simulator.py`
- [ ] SSH能连接到服务器
- [ ] 服务器上有数据文件生成
- [ ] 监控脚本可以正常运行
- [ ] 备份目录有文件
- [ ] GitHub仓库可访问
- [ ] 4个Word文档已准备好
- [ ] 演示流程已演练1遍

---

**祝演示顺利！🎉**
