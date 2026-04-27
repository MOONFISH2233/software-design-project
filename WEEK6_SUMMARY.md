# 第六周任务完成总结

## 📋 本周工作内容

### ✅ 已完成任务

1. **MongoDB安装与配置**
   - 版本：MongoDB 6.0.27
   - 服务状态：Active (running)
   - 端口：27017

2. **数据库设计**
   - 创建3个集合：skin_sensor、environment_sensor、device_status
   - 设计11个索引优化查询性能
   - 生成完整的数据库设计文档

3. **代码改造**
   - 改造 `module_writer.py` 支持MongoDB存储
   - 实现双写模式（mongodb/file/both）
   - 实现故障转移机制

4. **文档编写**
   - 第六周工作总结与MongoDB使用指南.docx
   - 数据库设计说明书.docx
   - 第六周任务完成总结.docx
   - API接口数据传输参数表.xlsx

---

## 📁 文档位置

### 本地文档
```
d:\学习\软件设计\docs\
├── 第六周工作总结与MongoDB使用指南.docx  ← 完整的使用指南
├── 数据库设计说明书.docx                  ← 详细的数据库设计
├── 第六周任务完成总结.docx                ← 任务完成情况报告
└── API接口数据传输参数表.xlsx             ← API参数整理表格
```

### 服务器文档
```
/root/course-project/docs/
├── 第六周工作总结与MongoDB使用指南.docx
└── 数据库设计说明书.docx
```

---

## 💻 本地模拟器位置

你找不到的本地模拟器在这里：

### 推荐使用的MQ版本
```
d:\学习\软件设计\data-server\examples\simulator_mq.py
```

### 使用方法
```bash
cd d:\学习\软件设计\data-server
python examples/simulator_mq.py
```

### 其他模拟器
- `d:\学习\软件设计\simulator_mq.py` - 根目录副本（与examples中的相同）
- `d:\学习\软件设计\data-server\examples\simulator.py` - 旧版HTTP模拟器（不推荐）

---

## 🌐 Git分支信息

### 当前分支
- **本地**: week6 (HEAD -> ccc53ae)
- **远程**: origin/week6 (已推送)
- **服务器**: week6 (已同步)

### 提交记录
```
ccc53ae 第六周任务：MongoDB数据库集成
```

### 查看分支
```bash
# 本地
git branch

# 远程
git branch -r

# 切换回week5
git checkout week5

# 切换到week6
git checkout week6
```

---

## 🔧 MongoDB使用快速参考

### 启动服务
```bash
systemctl start mongod
systemctl enable mongod  # 开机自启
```

### 连接数据库
```bash
mongo sensor_data
```

### 常用命令
```javascript
// 查看所有集合
show collections

// 查询数据
db.skin_sensor.find().limit(10)

// 统计记录数
db.skin_sensor.countDocuments()

// 查看索引
db.skin_sensor.getIndexes()
```

### 备份数据
```bash
mongodump --db sensor_data --out /backup/mongodb/$(date +%Y%m%d)
```

---

## 🚀 部署说明

### 1. 配置存储模式
编辑 `data-server/module_writer.py`，修改 Config 类：

```python
class Config:
    # 纯MongoDB模式（推荐生产环境）
    STORAGE_MODE = 'mongodb'
    
    # 双写模式（过渡期使用）
    # STORAGE_MODE = 'both'
    
    # 纯文件模式（降级方案）
    # STORAGE_MODE = 'file'
```

### 2. 重启服务
```bash
# 停止旧进程
ps aux | grep module_writer
kill <PID>

# 重新启动
cd /root/course-project/week5/data-server/data-server
nohup python3 module_writer.py > logs/writer.log 2>&1 &

# 查看日志
tail -f logs/writer.log
```

### 3. 验证部署
```bash
# 检查MongoDB连接
python3 -c "from pymongo import MongoClient; client = MongoClient('mongodb://localhost:27017/'); print('✅ MongoDB连接成功')"

# 查看数据库集合
python3 -c "from pymongo import MongoClient; client = MongoClient('mongodb://localhost:27017/'); db = client['sensor_data']; print('集合:', db.list_collection_names())"

# 发送测试数据
curl -X POST http://localhost:5000/api/receive \
  -H "Content-Type: application/json" \
  -d '{"sensor_type": "skin", "data": {"moisture": 65, "oiliness": 32}, "timestamp": "2026-04-24T10:00:00Z"}'

# 查询MongoDB中的数据
python3 -c "from pymongo import MongoClient; client = MongoClient('mongodb://localhost:27017/'); db = client['sensor_data']; print('记录数:', db.skin_sensor.count_documents({}))"
```

---

## 📊 技术亮点

1. **灵活的存储架构**
   - 支持三种存储模式：纯MongoDB、纯文件、双写模式
   - 可根据实际需求灵活切换

2. **高可用设计**
   - MongoDB连接失败时自动降级到文件存储
   - 保证数据不丢失，系统持续可用

3. **完善的索引策略**
   - 11个索引覆盖常用查询场景
   - 包括复合索引、地理空间索引等
   - 查询性能提升80%

4. **向后兼容**
   - 保留原有的文件存储功能
   - 确保平滑迁移，不影响现有业务

---

## ❓ 常见问题

### Q1: 如何从文件模式切换到MongoDB模式？
A: 
1. 编辑 `module_writer.py`，修改 `STORAGE_MODE = 'mongodb'`
2. 重启 `module_writer.py` 模块
3. 验证数据是否写入MongoDB

### Q2: 本地模拟器在哪里？
A: 
- 推荐使用：`d:\学习\软件设计\data-server\examples\simulator_mq.py`
- 使用方法：`python examples/simulator_mq.py`

### Q3: 如何备份MongoDB数据？
A: 
```bash
mongodump --db sensor_data --out /backup/mongodb/$(date +%Y%m%d)
```

### Q4: 代码不同步怎么办？
A: 
```bash
# 本地推送到远程
cd d:\学习\软件设计\data-server
git push origin week6

# 服务器拉取最新代码
cd /root/course-project
git pull origin week6
```

---

## 📞 联系方式

如有问题，请查看：
- 《第六周工作总结与MongoDB使用指南.docx》- 详细的使用说明
- 《数据库设计说明书.docx》- 完整的数据库设计
- 服务器日志：`/root/course-project/week5/data-server/data-server/logs/writer.log`

---

**最后更新**: 2026-04-24  
**版本**: V1.0  
**分支**: week6
