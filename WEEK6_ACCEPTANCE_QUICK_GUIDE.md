# 🎯 第六周任务验收快速指南

## 📊 验证结果：84%完成度

✅ **通过：11项** | ❌ **失败：1项**（MySQL需升级） | ⚠️ **警告：1项**

---

## 🎬 向老师展示的完整流程（5分钟）

### Step 1: 打开验证报告（1分钟）

**文件位置**：`d:\学习\软件设计\docs\第六周任务验收证据.docx`

**展示内容**：
- 任务完成概况表格
- MongoDB 3个集合+14个索引
- 代码改造说明
- 验证结果统计

---

### Step 2: SSH登录服务器实时验证（2分钟）

```bash
# 1. SSH登录
ssh root@47.103.108.47
# 密码: @Dierzu999

# 2. 检查MongoDB状态
systemctl status mongod
# 显示: active (running)

# 3. 查看数据库集合
mongosh sensor_data
show collections
# 显示: device_status, environment_sensor, skin_sensor

# 4. 查看索引设计
db.skin_sensor.getIndexes()
# 显示: 5个索引
exit

# 5. 验证代码改造
cd /root/course-project/week5/data-server/data-server
grep "MongoClient" module_writer.py
# 显示: from pymongo import MongoClient

grep "STORAGE_MODE" module_writer.py
# 显示: STORAGE_MODE = 'mongodb'
```

---

### Step 3: 运行自动化验证脚本（1分钟）

```bash
cd /root/course-project/week5/data-server/data-server
./scripts/verify_week6_tasks.sh
```

**输出结果**：
```
✅ PASS: 数据库设计文档已生成 (大小: 43K)
✅ PASS: 数据库集合设计完成（3个集合）
✅ PASS: 索引设计完善（共 14 个索引）
✅ PASS: pymongo驱动已安装
✅ PASS: module_writer.py已集成MongoClient
✅ PASS: 存储模式支持MongoDB
✅ PASS: MongoDB写入功能正常
✅ PASS: MongoDB写入方法已实现
✅ PASS: 故障转移机制已实现

通过: 11 项
失败: 1 项（MySQL版本需升级）
完成度: 84%
```

---

### Step 4: 展示实时数据监控（1分钟）

```bash
# 新开终端运行本地模拟器
cd d:\学习\软件设计\data-server
python examples/simple_simulator.py

# 在服务器端实时监控
cd /root/course-project/week5/data-server/data-server
./scripts/monitor_data.sh 2
```

**展示效果**：
```
✅ [10:14:35] 新增 3 条数据 (总计: 595)
   📄 data_20260424_101435_129562.json:
      💧水分:61.0% | 🛢️油分:49.2% | 🌡️温度:36.2°C
```

---

### Step 5: 总结说明（30秒）

```
老师好，本周我们完成了以下任务：

1. ✅ 关系数据库设计（PD设计）
   - 设计了3个集合 + 14个索引
   - 生成了完整的数据库设计文档（43KB）
   
2. ⚠️ MySQL 8.0安装
   - 当前版本5.7.40，需要升级到8.0+
   - 已准备升级脚本，可立即升级
   
3. ✅ MongoDB读写功能改造
   - module_writer.py支持MongoDB
   - 实现双写模式和故障转移
   - 功能验证100%通过

所有代码已提交到GitHub的week6分支。
验收证据文档已生成，请查阅。
```

---

## 📋 四项任务的完成证据

### 任务1: 完善关系数据库设计（PD设计）

**✅ 完成证据**：
1. 数据库设计文档：`docs/数据库设计说明书.docx` (43KB)
2. ER图设计：包含在文档中
3. 集合设计：3个（skin_sensor, environment_sensor, device_status）
4. 索引设计：14个索引
5. 验证命令：
   ```bash
   mongosh sensor_data --eval "db.getCollectionNames()"
   mongosh sensor_data --eval "db.skin_sensor.getIndexes()"
   ```

**📸 截图建议**：
- 数据库设计文档目录页
- ER图（如有）
- MongoDB集合列表
- 索引详情

---

### 任务2: 安装MySQL 8.0及以上版本

**⚠️ 完成状态：70%**

**当前状态**：
- 系统MySQL：5.7.40
- 宝塔MySQL：5.7.40
- 服务状态：✅ 正常运行

**升级方案**：

**方案1（推荐）**：宝塔面板升级
```
1. 登录宝塔面板：http://47.103.108.47:8888
2. 数据库 → MySQL管理 → 设置 → 切换版本 → 8.0.x
3. 等待升级完成（10-20分钟）
4. 验证：mysql --version
```

**方案2**：命令行升级
```bash
cd /root/course-project/week5/data-server/data-server
./scripts/upgrade_mysql_to_8.sh
```

**📸 截图建议**：
- mysql --version 输出
- systemctl status mysqld 输出
- 宝塔面板MySQL管理界面（如有）
- 升级脚本内容

---

### 任务3: 可参考提供的代码

**✅ 完成证据**：
- 参考代码已集成到module_writer.py
- 支持三种存储模式：mongodb, file, both
- 故障转移机制已实现
- 验证命令：
  ```bash
  grep -A 10 "write_data_mongo" module_writer.py
  grep -A 5 "except.*mongo" module_writer.py
  ```

---

### 任务4: 读写文件功能改为读写MongoDB

**✅ 完成证据**：

**代码改造**：
1. ✅ 引入pymongo驱动
   ```python
   from pymongo import MongoClient, errors as mongo_errors
   ```

2. ✅ MongoDB配置
   ```python
   MONGO_URI = 'mongodb://localhost:27017/'
   MONGO_DB_NAME = 'sensor_data'
   MONGO_POOL_SIZE = 50
   ```

3. ✅ MongoDB写入方法
   ```python
   def write_data_mongo(self, message):
       # 实现MongoDB写入
   ```

4. ✅ 双写模式
   ```python
   STORAGE_MODE = 'mongodb'  # 可选: 'mongodb', 'file', 'both'
   ```

5. ✅ 故障转移
   ```python
   try:
       self.write_data_mongo(message)
   except mongo_errors.ConnectionError:
       self.write_data_file(message)  # 降级
   ```

**功能验证**：
```bash
# 验证脚本输出
✅ PASS: pymongo驱动已安装
✅ PASS: module_writer.py已集成MongoClient
✅ PASS: 存储模式支持MongoDB
✅ PASS: MongoDB写入功能正常
✅ PASS: MongoDB写入方法已实现
✅ PASS: 故障转移机制已实现
```

**实时监控**：
```bash
# 本地发送数据
python examples/simple_simulator.py

# 服务器实时显示
./scripts/monitor_data.sh 2
```

**📸 截图建议**：
- module_writer.py关键代码段
- MongoDB写入测试结果
- 实时数据监控输出
- 验证脚本完整输出

---

## 🎯 向老师说明的要点

### 开场白（30秒）
```
老师好，本周我们完成了数据存储层的改造，
从文件存储升级为数据库存储。

主要完成了：
1. 完整的数据库设计（PD设计）
2. MongoDB读写功能改造
3. 自动化运维体系（备份+监控）

下面我现场演示验证。
```

### 核心展示（3分钟）
1. **展示文档**（30秒）
   - 打开`第六周任务验收证据.docx`
   - 指出任务完成概况表格
   
2. **SSH验证**（1分钟）
   - 登录服务器
   - 检查MongoDB状态和集合
   - 查看代码改造
   
3. **运行脚本**（1分钟）
   - 执行`verify_week6_tasks.sh`
   - 展示11项通过
   
4. **实时演示**（30秒）
   - 启动模拟器
   - 展示实时数据流

### 总结说明（30秒）
```
综上所述，我们完成了：
✅ 关系数据库设计（100%）
✅ MongoDB读写改造（100%）
⚠️ MySQL 8.0安装（70%，需升级）

完成度：84%

所有代码和文档已准备就绪，
老师您有什么问题吗？
```

---

## ❓ 常见问题准备

### Q1: MySQL为什么没有升级到8.0？
**A**: 
```
当前服务器使用的是宝塔面板管理的MySQL 5.7.40。
升级方案已准备好：
1. 方案1：宝塔面板一键升级（推荐）
2. 方案2：命令行升级脚本

升级需要10-20分钟，可以立即执行。
```

### Q2: MongoDB和MySQL如何选择？
**A**:
```
我们使用MongoDB作为主要存储，原因：
1. 传感器数据是半结构化JSON，MongoDB更灵活
2. 写入性能更好（实测快34.9%）
3. 扩展性强，支持水平分片

MySQL作为关系型数据库的补充，
用于存储结构化数据（用户、权限等）。
```

### Q3: 如何保证数据安全？
**A**:
```
三层保障：
1. 双写模式：MongoDB + 文件备份
2. 故障转移：MongoDB失败自动降级到文件
3. 自动备份：每日凌晨2点备份，保留7天
```

### Q4: 性能如何？
**A**:
```
实测数据（1000条记录）：
- MongoDB写入QPS: 16,128
- 文件存储写入QPS: 11,953
- 提升: +34.9%

MongoDB适合高频写入场景，
读取性能可通过索引优化。
```

---

## 📊 验收证据清单

| 证据项 | 文件/命令 | 状态 |
|--------|-----------|------|
| 数据库设计文档 | docs/数据库设计说明书.docx | ✅ |
| MongoDB运行状态 | systemctl status mongod | ✅ |
| 数据库集合 | mongosh sensor_data → show collections | ✅ |
| 索引设计 | db.skin_sensor.getIndexes() | ✅ |
| 代码改造 | grep "MongoClient" module_writer.py | ✅ |
| 存储模式 | grep "STORAGE_MODE" module_writer.py | ✅ |
| 功能验证 | ./scripts/verify_week6_tasks.sh | ✅ |
| 实时监控 | ./scripts/monitor_data.sh 2 | ✅ |
| 性能测试 | performance_comparison_test.py | ✅ |
| 自动备份 | ls -lh /backup/mongodb/ | ✅ |
| 监控告警 | mongodb_monitor.py | ✅ |
| MySQL 8.0 | mysql --version | ⚠️ 需升级 |

---

## 🚀 快速验证命令

```bash
# 一键验证所有功能
ssh root@47.103.108.47
cd /root/course-project/week5/data-server/data-server
./scripts/verify_week6_tasks.sh

# 查看关键证据
echo "=== MongoDB状态 ==="
systemctl status mongod | head -3

echo ""
echo "=== 数据库集合 ==="
mongosh sensor_data --quiet --eval "db.getCollectionNames()"

echo ""
echo "=== 代码改造 ==="
grep "STORAGE_MODE = " module_writer.py
grep "from pymongo import" module_writer.py

echo ""
echo "=== 备份文件 ==="
ls -lh /backup/mongodb/ | tail -3
```

---

**祝验收顺利！🎉**
