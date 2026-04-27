# 第八周任务 - 快速操作指南

## 🎯 本周完成内容

### ✅ 已完成
1. **小程序功能规划** - 7大模块，20+接口设计
2. **数据库设计完善** - 从5个表扩展到15个表
3. **定时任务实现** - APScheduler每日凌晨2点自动统计
4. **Flask接口开发** - 14个核心API接口（JWT认证）
5. **PowerDesigner教程** - 完整使用指南
6. **项目文件整理** - 清晰的目录结构

---

## 📁 新增文件清单

### 核心代码
- `data-server/models.py` - 更新：添加10个新表模型
- `data-server/routes/miniprogram_routes.py` - 新增：小程序API路由
- `data-server/app.py` - 更新：注册小程序路由

### 数据库脚本
- `data-server/scripts/init_mysql_week8.sql` - 新增：15个表建表脚本

### 文档
- `docs/WEEK8_MINIPROGRAM_PLAN.md` - 新增：小程序功能思维导图
- `docs/POWERDESIGNER_TUTORIAL.md` - 新增：PowerDesigner使用教程
- `docs/WEEK8_COMPLETION_SUMMARY.md` - 新增：第八周完成总结
- `docs/WEEK8_DEPLOYMENT_GUIDE.md` - 新增：部署指南

### 脚本工具
- `data-server/scripts/organize_project.sh` - 新增：项目整理脚本
- `data-server/scripts/deploy_week8.sh` - 新增：服务器部署脚本
- `data-server/scripts/commit_and_push_week8.bat` - 新增：Git提交脚本

---

## 🚀 快速部署到服务器

### 方法一：一键部署（推荐）

```bash
# 1. SSH登录服务器
ssh root@47.103.108.47
# 密码: @Dierzu999

# 2. 执行部署脚本
cd /root/course-project
mkdir -p week8 && cd week8
git clone -b week8 https://github.com/MOONFISH2233/software-design-project.git .
cd data-server
chmod +x scripts/*.sh
bash scripts/deploy_week8.sh
```

### 方法二：手动部署

详见：`docs/WEEK8_DEPLOYMENT_GUIDE.md`

---

## 🔌 API接口测试

### 1. 注册用户
```bash
curl -X POST http://47.103.108.47:5000/api/miniprogram/user/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"123456","phone":"13800138000"}'
```

### 2. 登录获取Token
```bash
curl -X POST http://47.103.108.47:5000/api/miniprogram/user/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"123456"}'
```

### 3. 查询用户信息
```bash
curl -X GET http://47.103.108.47:5000/api/miniprogram/user/profile \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 🗄️ 数据库验证

```bash
# SSH登录服务器
ssh root@47.103.108.47

# 检查表数量
mysql -u root -padmin -e "USE software_design; SHOW TABLES;" | wc -l

# 应该返回 16（15个表 + 标题行）

# 查看表列表
mysql -u root -padmin -e "USE software_design; SHOW TABLES;"
```

预期输出：
```
+---------------------------+
| Tables_in_software_design |
+---------------------------+
| community_posts           |
| daily_statistics          |
| device_bindings           |
| devices                   |
| environment_sensor_data   |
| health_reports            |
| notifications             |
| post_comments             |
| skin_sensor_data          |
| skincare_products         |
| system_configs            |
| user_points               |
| user_profiles             |
| user_skincare_records     |
| users                     |
+---------------------------+
```

---

## ⏰ 定时任务验证

```bash
# 查看定时任务日志
tail -f /var/log/daily_statistics.log

# 查看服务状态
systemctl status daily-statistics

# 手动触发一次（测试用）
python3 /root/course-project/week8/data-server/tasks/daily_statistics.py
```

---

## 📊 关键数据

### 数据库表统计
- **原有表**: 5个（devices, skin_sensor_data, environment_sensor_data, daily_statistics, users）
- **新增表**: 10个（user_profiles, health_reports, device_bindings, community_posts, post_comments, notifications, user_points, skincare_products, user_skincare_records, system_configs）
- **总计**: 15个表

### API接口统计
- **用户管理**: 4个接口
- **设备管理**: 3个接口
- **数据查询**: 3个接口
- **健康报告**: 2个接口
- **消息通知**: 2个接口
- **总计**: 14个接口

### 代码统计
- **新增代码行数**: ~2500行
- **新增文档**: 4个Markdown文件
- **新增脚本**: 3个Shell/Batch脚本

---

## 🎓 PowerDesigner学习要点

### 快速开始
1. 打开PowerDesigner
2. File → New Model → Conceptual Data Model
3. 创建实体（Entity）和属性（Attribute）
4. 建立关系（Relationship）
5. Tools → Generate Physical Data Model
6. Database → Generate Database

### 详细教程
查看：`docs/POWERDESIGNER_TUTORIAL.md`

---

## 📝 Git操作

### 本地提交（已完成）
```bash
cd "d:\学习\软件设计"
git checkout week8
git add .
git commit -m "feat: 完成第八周任务"
```

### 推送到GitHub（如网络允许）
```bash
git push origin week8
```

### 查看提交历史
```bash
git log --oneline -5
```

---

## 🔍 故障排查

### 应用无法启动
```bash
# 查看日志
tail -f /root/course-project/logs/server_*.log

# 检查端口占用
netstat -tlnp | grep 5000

# 重启服务
systemctl restart gunicorn-flask-data-server
```

### 数据库连接失败
```bash
# 检查MySQL状态
systemctl status mysqld

# 检查MongoDB状态
systemctl status mongod

# 测试连接
mysql -u root -padmin -e "SHOW DATABASES;"
mongosh --eval "db.adminCommand('listDatabases')"
```

### 定时任务未执行
```bash
# 检查服务状态
systemctl status daily-statistics

# 查看日志
journalctl -u daily-statistics -n 50
```

---

## 📞 下一步计划

### 第九周任务预告
- 小程序前端开发（UniApp）
- 用户界面设计
- 数据可视化图表
- 实时数据推送

### 第十周任务预告
- 系统集成测试
- 性能优化
- 安全加固
- 验收准备

---

## 📚 相关文档

- **小程序功能规划**: `docs/WEEK8_MINIPROGRAM_PLAN.md`
- **PowerDesigner教程**: `docs/POWERDESIGNER_TUTORIAL.md`
- **完成总结**: `docs/WEEK8_COMPLETION_SUMMARY.md`
- **部署指南**: `docs/WEEK8_DEPLOYMENT_GUIDE.md`

---

## ✨ 总结

第八周任务已全部完成！主要成果：

✅ 完整的小程序功能规划  
✅ 15个表的数据库设计  
✅ 14个Flask API接口  
✅ 每日自动统计定时任务  
✅ PowerDesigner详细教程  
✅ 清晰的项目文件结构  

**服务器地址**: 47.103.108.47  
**GitHub仓库**: https://github.com/MOONFISH2233/software-design-project  
**当前分支**: week8  

祝学习愉快！🎉
