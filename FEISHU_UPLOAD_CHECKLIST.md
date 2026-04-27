# 📋 飞书上传材料清单

## ✅ 必传文档（4份）

### 1. 第六周飞书汇报文档.docx ⭐⭐⭐⭐⭐
**位置**: `docs/第六周飞书汇报文档.docx`  
**内容**: 
- 工作完成情况总结
- MongoDB安装配置详情
- 数据库设计方案
- 性能测试结果
- 自动化运维体系
- **演示说明和使用指南**（重点）
- 给老师的展示要点

**用途**: 主汇报文档，老师主要看这个

---

### 2. 第六周工作总结与MongoDB使用指南.docx ⭐⭐⭐⭐
**位置**: `docs/第六周工作总结与MongoDB使用指南.docx`  
**内容**:
- 详细的使用手册
- MongoDB命令大全
- 故障排查指南
- 常见问题解答

**用途**: 技术参考文档，备查

---

### 3. 数据库设计说明书.docx ⭐⭐⭐⭐
**位置**: `docs/数据库设计说明书.docx`  
**内容**:
- ER图
- 集合结构设计
- 索引设计
- 数据流图

**用途**: 展示专业性，证明有完整的数据库设计

---

### 4. API接口数据传输参数表.xlsx ⭐⭐⭐
**位置**: `docs/API接口数据传输参数表.xlsx`  
**内容**:
- 12个API接口参数
- 传输频率
- 数据类型

**用途**: 展示接口规范性

---

## 📊 建议补充材料

### 5. 性能测试报告（可选但推荐）
**生成方式**:
```bash
cd d:\学习\软件设计\data-server
scp scripts/performance_comparison_test.py root@47.103.108.47:/tmp/
ssh root@47.103.108.47 "python3 /tmp/performance_comparison_test.py 1000 100"
```

**截图内容**:
- MongoDB写入QPS: 16,128
- 文件存储写入QPS: 11,953
- 提升幅度: +34.9%

---

### 6. 监控报告截图（强烈推荐）⭐⭐⭐⭐⭐
**获取方式**:
```bash
ssh root@47.103.108.47 "python3 /root/course-project/week5/data-server/data-server/scripts/mongodb_monitor.py"
```

**截图内容**:
```
🔗 连接数: 当前3, 可用51197, 使用率0.01%
💾 内存使用: 常驻125MB
💿 磁盘使用: 数据0.0MB, 索引0.36MB
🐢 慢查询: 0个
✅ 所有指标正常
```

---

### 7. 备份文件列表截图（推荐）⭐⭐⭐⭐
**获取方式**:
```bash
ssh root@47.103.108.47 "ls -lh /backup/mongodb/"
```

**截图内容**:
```
drwxr-xr-x 3 root root 4.0K Apr 24 09:13 20260424_091332
-rw-r--r-- 1 root root  12K Apr 24 09:13 20260424_091332.archive.gz
```

---

### 8. Git提交记录截图（强烈推荐）⭐⭐⭐⭐⭐
**获取方式**:
```bash
# 本地执行
cd d:\学习\软件设计\data-server
git log --oneline -5
```

**截图内容**:
```
3f3f515 (HEAD -> week6) 添加MongoDB运维工具脚本
ccc53ae 第六周任务：MongoDB数据库集成
```

**GitHub链接**: https://github.com/MOONFISH2233/software-design-project/tree/week6

---

### 9. 录屏视频（强烈建议）⭐⭐⭐⭐⭐
**录制内容**（2-3分钟）:
1. 打开命令行，运行本地模拟器
   ```bash
   cd d:\学习\软件设计\data-server
   python examples/simulator_mq.py
   ```
2. SSH登录服务器
   ```bash
   ssh root@47.103.108.47
   ```
3. 查看MongoDB数据增长
   ```bash
   mongo sensor_data
   db.skin_sensor.countDocuments()  # 多次执行，展示数字增长
   ```
4. 运行监控脚本
   ```bash
   python3 scripts/mongodb_monitor.py
   ```

**录制工具**: 
- Windows: Win+G 游戏栏录制
- OBS Studio（免费专业）
- 剪映（简单易用）

---

## 🎯 上传到飞书的步骤

### 方式1：飞书文档（推荐）
1. 打开飞书 → 云文档 → 新建文档
2. 标题：**第六周任务完成情况汇报 - MongoDB数据库集成**
3. 上传上述Word文档作为附件
4. 在文档中插入关键截图
5. 添加文字说明和结论
6. 分享给老师

### 方式2：飞书群聊
1. 直接将4个Word文档拖入群聊
2. 附加简短说明：
   ```
   老师好，这是第六周任务完成情况：
   
   ✅ 已完成：
   1. MongoDB 6.0.27安装配置
   2. 数据库设计（3个集合+11个索引）
   3. 代码改造支持双写模式
   4. 自动化备份（每日凌晨2点）
   5. 实时监控告警（每5分钟）
   6. 性能测试（写入QPS提升34.9%）
   
   📄 附件：
   - 第六周飞书汇报文档.docx（主文档）
   - 数据库设计说明书.docx
   - 使用指南.docx
   - API参数表.xlsx
   
   🔗 GitHub: https://github.com/MOONFISH2233/software-design-project/tree/week6
   ```

### 方式3：飞书知识库
如果有团队知识库，可以创建专门的项目文档页面，结构化展示所有内容。

---

## 💡 给老师展示的核心要点

### 开场白（30秒）
```
老师好，本周我们完成了MongoDB数据库集成和运维体系建设：

1. 安装了MongoDB 6.0.27并设计了3个集合
2. 改造了代码支持双写模式和故障转移
3. 建立了自动化备份和监控告警系统
4. 完成了性能测试，写入QPS提升34.9%

下面我现场演示一下。
```

### 演示流程（5-8分钟）

#### Step 1: 展示Git仓库（1分钟）
```
• 打开浏览器访问：
  https://github.com/MOONFISH2233/software-design-project
  
• 切换到week6分支
• 展示最新提交："添加MongoDB运维工具脚本"
• 指出新增的4个脚本文件
```

#### Step 2: SSH登录服务器（1分钟）
```bash
ssh root@47.103.108.47
# 输入密码：@Dierzu999

# 检查MongoDB服务
systemctl status mongod

# 进入MongoDB
mongo sensor_data
show collections
exit
```

#### Step 3: 运行本地模拟器（2分钟）
```bash
# 新开一个终端窗口
cd d:\学习\软件设计\data-server
python examples/simulator_mq.py

# 同时在服务器端观察
mongo sensor_data
db.skin_sensor.countDocuments()  # 看到数字在增长
```

#### Step 4: 展示监控报告（1分钟）
```bash
python3 scripts/mongodb_monitor.py

# 展示输出：
# 🔗 连接数使用率：0.01%
# 💾 内存使用：125MB
# 💿 磁盘使用：0.45MB
# 🐢 慢查询：0个
# ✅ 所有指标正常
```

#### Step 5: 展示备份机制（1分钟）
```bash
# 查看备份目录
ls -lh /backup/mongodb/

# 查看定时任务
crontab -l

# 输出显示：
# 0 2 * * * ... mongodb_backup.sh  （每天2点备份）
# */5 * * * * ... mongodb_monitor.py  （每5分钟监控）
```

#### Step 6: 性能对比（可选，1分钟）
```bash
python3 scripts/performance_comparison_test.py 500 50

# 展示关键结果：
# MongoDB写入QPS: 16,128
# 文件存储写入QPS: 11,953
# 提升: +34.9%
```

### 结束语（30秒）
```
以上就是本周的工作成果。我们不仅完成了MongoDB集成，
还建立了完整的运维体系，包括自动备份和实时监控。

所有代码已提交到GitHub的week6分支，文档也已整理完成。

老师您有什么问题吗？
```

---

## ❓ 常见问题准备

### Q1: 为什么选择MongoDB而不是MySQL？
**回答**:
```
主要有三个原因：
1. 数据结构灵活：传感器数据是半结构化JSON，MongoDB的文档模型天然支持
2. 写入性能更好：实测写入QPS比文件存储快34.9%
3. 扩展性强：未来数据量大了可以水平分片，MySQL需要做复杂的分库分表
```

### Q2: 如果MongoDB挂了怎么办？
**回答**:
```
我们有三层保障：
1. 故障转移：module_writer.py配置为双写模式，MongoDB失败时自动降级到文件存储
2. 监控告警：每5分钟检查一次，异常立即发现
3. 定期备份：每天凌晨2点自动备份，可以恢复到任意时间点
```

### Q3: 备份策略是什么？
**回答**:
```
• 频率：每日凌晨2点（业务低峰期）
• 保留：滚动保留最近7天
• 格式：gzip压缩节省空间
• 位置：/backup/mongodb/
• 验证：每次备份后检查文件大小和完整性
```

### Q4: 性能瓶颈在哪里？如何优化？
**回答**:
```
当前瓶颈：
• 网络IO：单台服务器带宽限制
• 磁盘IO：机械硬盘读写速度

优化方案：
• 短期：升级到SSD硬盘
• 中期：增加Redis缓存层
• 长期：搭建MongoDB副本集或分片集群
```

### Q5: 如何保证数据安全？
**回答**:
```
三层保障：
1. 冗余存储：双写模式同时写入MongoDB和文件
2. 定期备份：每日自动备份，保留7天
3. 实时监控：每5分钟检查，异常立即告警

即使MongoDB完全损坏，也可以从文件或备份恢复。
```

---

## 📸 必备截图清单

截图以下内容（按优先级）：

1. ⭐⭐⭐⭐⭐ Git提交记录
   - 显示week6分支
   - 显示最新提交信息
   
2. ⭐⭐⭐⭐⭐ MongoDB服务状态
   - `systemctl status mongod` 输出
   - 显示 active (running)
   
3. ⭐⭐⭐⭐⭐ 监控报告输出
   - `python3 scripts/mongodb_monitor.py` 完整输出
   - 显示所有指标正常
   
4. ⭐⭐⭐⭐ 备份文件列表
   - `ls -lh /backup/mongodb/` 输出
   
5. ⭐⭐⭐⭐ 性能测试结果
   - MongoDB vs 文件存储对比表格
   
6. ⭐⭐⭐ MongoDB集合列表
   - `mongo sensor_data` -> `show collections`
   
7. ⭐⭐⭐ 定时任务配置
   - `crontab -l` 输出

---

## 🎬 录屏脚本（如果需要）

### 场景1：完整演示（3分钟）
```
[0:00-0:10] 开场：今天演示第六周MongoDB集成成果
[0:10-0:30] 展示GitHub仓库week6分支
[0:30-1:00] SSH登录服务器，检查MongoDB服务
[1:00-1:30] 运行本地模拟器
[1:30-2:00] 服务器端观察数据增长
[2:00-2:30] 运行监控脚本，展示各项指标
[2:30-3:00] 展示备份文件和cron配置，总结
```

### 场景2：快速演示（1分钟）
```
[0:00-0:10] 展示Git提交
[0:10-0:30] SSH登录，systemctl status mongod
[0:30-0:50] python3 scripts/mongodb_monitor.py
[0:50-1:00] 总结：所有功能正常运行
```

---

## ✅ 最终检查清单

在上传飞书前，确认：

- [ ] 4个Word/Excel文档已生成
- [ ] 至少5张关键截图已准备
- [ ] （可选）录屏视频已录制
- [ ] GitHub链接可访问
- [ ] SSH连接测试通过
- [ ] 所有命令已预先测试
- [ ] 常见问题答案已准备
- [ ] 演示流程已演练1-2遍

---

**祝汇报顺利！🎉**
