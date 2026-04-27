# 小程序功能思维导图

## 📱 皮肤健康监测小程序 - 功能架构

### 1️⃣ 用户管理模块
- **注册登录**
  - 微信一键登录
  - 手机号验证码登录
  - 账号密码登录
- **个人中心**
  - 基本信息编辑（昵称、头像、性别、年龄）
  - 肤质档案建立（干性/油性/混合性/敏感性）
  - 护肤目标设置（保湿/控油/抗衰/美白）
- **会员体系**
  - 积分系统
  - 等级权益
  - 专属报告

### 2️⃣ 数据可视化模块
- **实时监测**
  - 皮肤水分含量趋势图
  - 皮肤油脂度变化曲线
  - 皮肤温度波动图
  - 环境监测数据（温湿度、PM2.5、CO2）
- **历史数据**
  - 日/周/月/年视图切换
  - 多维度数据对比
  - 数据导出（Excel/PDF）
- **智能分析**
  - 异常数据预警
  - 周期性规律识别
  - 环境影响因子分析

### 3️⃣ 设备管理模块
- **设备绑定**
  - 扫码添加设备
  - 手动输入设备ID
  - 多设备管理
- **设备状态**
  - 在线/离线状态
  - 电池电量显示
  - 信号强度指示
  - 固件版本检查
- **设备控制**
  - 数据采集频率设置
  - 传感器校准
  - 远程重启
  - OTA升级

### 4️⃣ 健康报告模块
- **日报**
  - 今日数据概览
  - 与昨日对比
  - 改善建议
- **周报**
  - 本周趋势分析
  - 最佳/最差时段
  - 护肤效果评估
- **月报**
  - 月度综合评分
  - 关键指标变化
  - 个性化护肤方案
- **年度报告**
  - 全年数据总结
  - 季节性变化规律
  - 长期改善轨迹

### 5️⃣ 社区分享模块
- **动态发布**
  - 图文分享
  - 数据截图分享
  - 护肤心得记录
- **话题讨论**
  - 热门话题
  - 专家问答
  - 经验交流
- **达人推荐**
  - 护肤达人榜单
  - 优质内容推荐
  - 产品评测分享

### 6️⃣ 设置中心模块
- **通知设置**
  - 数据异常提醒
  - 报告生成通知
  - 社区互动消息
- **隐私设置**
  - 数据可见范围
  - 匿名分享选项
  - 数据删除
- **通用设置**
  - 主题切换（浅色/深色）
  - 语言选择
  - 缓存清理
  - 关于我们

### 7️⃣ 消息通知模块
- **系统通知**
  - 版本更新提示
  - 活动推广
  - 服务公告
- **数据提醒**
  - 采集异常告警
  - 设备低电量提醒
  - 数据同步失败
- **互动消息**
  - 点赞通知
  - 评论回复
  - 关注动态

---

## 🗄️ 数据库设计补充说明

### 新增表结构（基于原有8个表扩展至15个表）

#### 已有表（第八周前完成）
1. ✅ devices - 设备信息表
2. ✅ skin_sensor_data - 皮肤传感器数据表
3. ✅ environment_sensor_data - 环境传感器数据表
4. ✅ daily_statistics - 每日统计表
5. ✅ users - 用户基础表

#### 新增表（第八周补充）
6. **user_profiles** - 用户详细档案表
   - user_id, skin_type, skincare_goals, age, gender, register_date
   
7. **health_reports** - 健康报告表
   - report_id, user_id, report_type(daily/weekly/monthly/yearly), report_date, content_json, score, suggestions
   
8. **device_bindings** - 设备绑定关系表
   - binding_id, user_id, device_id, bind_time, is_primary, status
   
9. **community_posts** - 社区帖子表
   - post_id, user_id, title, content, images_json, like_count, comment_count, view_count, created_at
   
10. **post_comments** - 帖子评论表
    - comment_id, post_id, user_id, parent_comment_id, content, like_count, created_at
    
11. **notifications** - 消息通知表
    - notification_id, user_id, type(system/data/interaction), title, content, is_read, created_at
    
12. **user_points** - 用户积分表
    - user_id, total_points, available_points, expired_points, last_update
    
13. **skincare_products** - 护肤品数据库
    - product_id, name, brand, category, ingredients, suitable_skin_type, rating
    
14. **user_skincare_records** - 用户护肤记录表
    - record_id, user_id, product_id, usage_time, usage_amount, notes
    
15. **system_configs** - 系统配置表
    - config_key, config_value, description, updated_at

---

## 🔄 定时任务流程

```
每天凌晨 2:00
    ↓
从 MongoDB 读取前一天数据
    ↓
聚合计算统计指标
    ├─ 总记录数
    ├─ 活跃设备数
    ├─ 各项平均值（水分、油脂、温度等）
    └─ 最多/最少记录设备
    ↓
写入 MySQL daily_statistics 表
    ↓
生成用户健康报告
    ↓
发送推送通知（如有异常）
```

---

## 🔌 Flask API 接口清单

### 用户相关
- POST /api/user/register - 用户注册
- POST /api/user/login - 用户登录
- GET /api/user/profile - 获取用户信息
- PUT /api/user/profile - 更新用户信息

### 设备相关
- POST /api/device/bind - 绑定设备
- GET /api/device/list - 获取设备列表
- GET /api/device/status/{device_id} - 查询设备状态
- PUT /api/device/settings - 更新设备设置

### 数据查询
- GET /api/data/skin - 查询皮肤数据（支持时间范围、分页）
- GET /api/data/environment - 查询环境数据
- GET /api/data/statistics - 查询统计数据
- GET /api/data/export - 导出数据

### 健康报告
- GET /api/report/list - 获取报告列表
- GET /api/report/detail/{report_id} - 获取报告详情
- POST /api/report/generate - 手动生成报告

### 社区功能
- POST /api/community/post - 发布帖子
- GET /api/community/posts - 获取帖子列表
- POST /api/community/comment - 发表评论
- GET /api/community/comments/{post_id} - 获取评论列表

### 消息通知
- GET /api/notification/list - 获取通知列表
- PUT /api/notification/read/{notification_id} - 标记已读
- DELETE /api/notification/{notification_id} - 删除通知

---

## 📊 PowerDesigner 使用教程

### 1. 创建概念数据模型(CDM)
1. 打开 PowerDesigner → File → New Model
2. 选择 Conceptual Data Model
3. 命名模型为 "SkinHealthSystem"

### 2. 创建实体(Entity)
1. 点击工具栏 "Entity" 图标
2. 在画布上点击创建实体
3. 双击实体编辑属性：
   - Name: 实体名称（中文）
   - Code: 实体代码（英文，对应表名）
   - Attributes: 添加字段

### 3. 定义属性(Attribute)
每个属性包含：
- Name: 字段中文名
- Code: 字段英文名（对应列名）
- Data Type: 数据类型
- Primary: 是否主键
- Mandatory: 是否必填
- Comment: 注释说明

### 4. 创建关系(Relationship)
1. 点击工具栏 "Relationship" 图标
2. 从父实体拖拽到子实体
3. 设置关系类型：
   - One-to-One (1:1)
   - One-to-Many (1:n)
   - Many-to-Many (m:n)

### 5. 生成物理数据模型(PDM)
1. Tools → Generate Physical Data Model
2. 选择 DBMS: MySQL 8.0
3. 配置生成选项：
   - 表名前缀
   - 索引策略
   - 外键约束
4. 点击确定生成

### 6. 导出 SQL 脚本
1. Database → Generate Database
2. 选择输出目录
3. 勾选选项：
   - Generate SQL script file
   - Include DROP statements
   - Include CREATE statements
4. 点击确定生成 .sql 文件

### 7. 反向工程（从数据库导入）
1. File → Reverse Engineer → Database
2. 选择 DBMS: MySQL 8.0
3. 配置连接参数
4. 选择要导入的表
5. 自动生成 CDM/PDM

---

## 🎯 实施步骤

### 第一阶段：数据库设计完善（Day 1-2）
- [x] 分析小程序功能需求
- [x] 设计新增表结构
- [ ] 使用 PowerDesigner 绘制 ER 图
- [ ] 生成 MySQL DDL 脚本
- [ ] 在服务器执行建表语句

### 第二阶段：定时任务优化（Day 3）
- [x] 完善 daily_statistics.py
- [ ] 增加健康报告自动生成
- [ ] 添加任务执行日志
- [ ] 测试定时任务触发

### 第三阶段：Flask 接口开发（Day 4-5）
- [ ] 创建 routes/miniprogram_routes.py
- [ ] 实现用户管理接口
- [ ] 实现设备管理接口
- [ ] 实现数据查询接口
- [ ] 实现健康报告接口
- [ ] 实现社区功能接口
- [ ] 实现消息通知接口

### 第四阶段：项目整理与部署（Day 6-7）
- [ ] 整理服务器文件结构
- [ ] 清理冗余文件
- [ ] 创建 week8 分支
- [ ] 提交代码到 GitHub
- [ ] 部署到服务器
- [ ] 编写验收文档

---

## 📝 验收标准

1. **数据库完整性**
   - 15个表全部创建成功
   - 外键约束正确
   - 索引优化合理

2. **定时任务可靠性**
   - 每日凌晨2点准时执行
   - 数据统计准确无误
   - 异常处理完善

3. **接口功能性**
   - 所有接口可正常调用
   - 返回数据格式统一
   - 错误处理友好

4. **代码规范性**
   - 文件夹结构清晰
   - 代码注释完整
   - 无冗余文件

5. **文档完整性**
   - PowerDesigner 源文件
   - ER 图导出图片
   - API 接口文档
   - 部署操作手册
