# PowerDesigner 第八周任务操作指南

## 🎯 本周任务目标

根据课程要求，你需要在PowerDesigner中完成以下工作：

### ✅ 已完成（代码层面）
- ✓ 小程序功能思维导图（`docs/WEEK8_MINIPROGRAM_PLAN.md`）
- ✓ 15个表的MySQL建表脚本（`data-server/scripts/init_mysql_week8.sql`）
- ✓ Flask接口开发（14个API）
- ✓ Python定时任务（每日统计）

### 📋 需在PowerDesigner中完成
1. **创建概念数据模型（CDM）** - 可视化ER图
2. **生成物理数据模型（PDM）** - 转换为MySQL格式
3. **导出SQL脚本** - 验证与现有脚本一致
4. **保存.pdm文件** - 提交到Git仓库

---

## 📝 PowerDesigner操作步骤详解

### 第一步：启动PowerDesigner并新建CDM

#### 1.1 打开PowerDesigner
```
双击桌面 PowerDesigner 图标
或
开始菜单 → SAP PowerDesigner → PowerDesigner 16
```

#### 1.2 创建新的概念数据模型
```
File → New Model
或按 Ctrl+N
```

**配置对话框：**
- **Category**: Information
- **Model type**: Conceptual Data Model
- **Model name**: `SkinHealthSystem_CDM`
- **DBMS**: 任意选择（CDM不依赖具体数据库）
- 点击 **OK**

---

### 第二步：创建15个实体（Entity）

> 💡 **提示**: 每个实体对应一个数据库表

#### 2.1 创建实体的方法

**方法A: 工具栏快速创建（推荐）**
1. 左侧工具栏找到 **Entity** 图标（看起来像一个表格）
2. 点击后在画布空白处单击
3. 自动出现新实体框

**方法B: 菜单创建**
```
Model → Entities → Add Entity
```

#### 2.2 逐个创建15个实体

按照以下顺序创建（建议从左到右、从上到下排列）：

| 序号 | 实体Name（中文） | 实体Code（英文表名） | 说明 |
|------|-----------------|---------------------|------|
| 1 | 用户 | users | 用户基本信息 |
| 2 | 用户资料 | user_profiles | 用户详细资料 |
| 3 | 设备 | devices | 设备信息 |
| 4 | 设备绑定 | device_bindings | 用户与设备绑定关系 |
| 5 | 皮肤传感器数据 | skin_sensor_data | 皮肤监测数据 |
| 6 | 环境传感器数据 | environment_sensor_data | 环境监测数据 |
| 7 | 每日统计数据 | daily_statistics | 每日汇总统计 |
| 8 | 健康报告 | health_reports | 健康分析报告 |
| 9 | 社区帖子 | community_posts | 社区动态 |
| 10 | 帖子评论 | post_comments | 帖子评论 |
| 11 | 消息通知 | notifications | 系统通知 |
| 12 | 用户积分 | user_points | 积分记录 |
| 13 | 护肤产品 | skincare_products | 产品库 |
| 14 | 护肤记录 | user_skincare_records | 用户使用记录 |
| 15 | 系统配置 | system_configs | 系统参数 |

---

### 第三步：为每个实体添加属性（Attributes）

> 💡 **这是最耗时的步骤，需要仔细对照SQL脚本**

#### 3.1 打开实体属性对话框

**双击** 实体框，弹出属性对话框

#### 3.2 填写General标签页

- **Name**: 实体中文名（如"用户"）
- **Code**: 实体英文名（如"users"）
- **Comment**: 实体描述（如"存储用户基本信息"）

#### 3.3 添加字段（Attributes标签页）

点击 **Add Attribute** 按钮（或按 Insert 键）

**以 users 表为例，添加以下字段：**

| Name（中文名） | Code（英文名） | Data Type | Primary | Mandatory | Comment |
|---------------|---------------|-----------|---------|-----------|---------|
| 用户ID | id | Integer | ✓ | ✓ | 主键，自增 |
| 用户名 | username | String(50) | | ✓ | 登录用户名 |
| 密码哈希 | password_hash | String(255) | | ✓ | BCrypt加密 |
| 昵称 | nickname | String(50) | | | 显示名称 |
| 手机号 | phone | String(20) | | | 联系方式 |
| 邮箱 | email | String(100) | | | 电子邮箱 |
| 头像URL | avatar_url | String(255) | | | 头像地址 |
| 角色 | role | String(20) | | | admin/user |
| 状态 | status | String(20) | | | active/inactive |
| 创建时间 | created_at | DateTime | | | 注册时间 |
| 更新时间 | updated_at | DateTime | | | 最后修改时间 |

**操作步骤：**
1. 点击 **Add Attribute**（或Insert键）
2. 填写Name、Code、Data Type
3. 勾选Primary（主键）、Mandatory（必填）
4. 填写Comment（注释）
5. 点击 **OK** 保存该字段
6. 重复添加所有字段

#### 3.4 数据类型对照表

| SQL类型 | PD CDM类型 | 示例 |
|---------|-----------|------|
| INT | Integer | id |
| BIGINT | BigInt | id (大数据量表) |
| VARCHAR(50) | String(50) | username |
| VARCHAR(255) | String(255) | password_hash |
| TEXT | Text | content |
| DATE | Date | install_date |
| DATETIME | DateTime | created_at |
| FLOAT | Float | temperature |
| DOUBLE | Double | score |
| TINYINT(1) | Boolean | is_read |
| JSON | Text | content_json |

---

### 第四步：建立实体间关系（Relationships）

> 💡 **关系对应数据库的外键约束**

#### 4.1 创建关系的方法

**工具栏操作：**
1. 点击左侧工具栏 **Relationship** 图标（看起来像一条连线）
2. 从**父实体**拖拽到**子实体**
3. 释放鼠标，自动生成关系线

#### 4.2 需要创建的14个关系

根据外键约束，创建以下关系：

| 父实体 | 子实体 | 关系类型 | 说明 |
|--------|--------|---------|------|
| users | user_profiles | 1:1 | 一个用户对应一份资料 |
| users | device_bindings | 1:n | 一个用户可绑定多个设备 |
| devices | device_bindings | 1:n | 一个设备可被多个用户绑定 |
| users | health_reports | 1:n | 一个用户有多份报告 |
| users | community_posts | 1:n | 一个用户发多个帖子 |
| community_posts | post_comments | 1:n | 一个帖子有多个评论 |
| users | post_comments | 1:n | 一个用户发多条评论 |
| users | notifications | 1:n | 一个用户收到多条通知 |
| users | user_points | 1:n | 一个用户有多条积分记录 |
| users | user_skincare_records | 1:n | 一个用户有多条护肤记录 |
| skincare_products | user_skincare_records | 1:n | 一个产品被多个用户使用 |
| devices | skin_sensor_data | 1:n | 一个设备采集多条数据 |
| devices | environment_sensor_data | 1:n | 一个设备采集多条环境数据 |
| devices | daily_statistics | 1:n | 一个设备对应多条统计 |

#### 4.3 设置关系属性

**双击关系线**，打开属性对话框：

**General标签页：**
- **Name**: 关系名称（如"用户拥有设备"）
- **Cardinality**: 
  - 父端: `1,1`（必须有一个）
  - 子端: `0,n`（可以有零个或多个）

**Joins标签页：**
- 确认关联字段正确（如 users.id = device_bindings.user_id）

---

### 第五步：检查和完善CDM

#### 5.1 布局优化

**自动布局：**
```
Tools → Auto Layout
或按 F6
```

**手动调整：**
- 拖动实体框，使关系线不交叉
- 相关实体放在一起（如users和user_profiles靠近）

#### 5.2 完整性检查

```
Tools → Check Model
```

检查项：
- ✓ 所有实体都有主键
- ✓ 所有关系都有正确的基数
- ✓ 没有孤立实体
- ✓ 命名规范一致

---

### 第六步：从CDM生成PDM（物理数据模型）

#### 6.1 生成PDM

```
Tools → Generate Physical Data Model
或按 Ctrl+G
```

**配置对话框：**

**General标签页：**
- **Physical Data Model name**: `SkinHealthSystem_PDM`
- **DBMS**: 选择 **MySQL 8.0**

**Options标签页：**
勾选以下选项：
- ✓ Generate tables
- ✓ Generate views（如果有视图）
- ✓ Generate indexes
- ✓ Generate foreign keys
- ✓ Generate checks
- ✓ Generate comments

**Detail标签页：**
- **Table prefix**: 留空（不使用前缀）
- **Column naming**: Keep original names

点击 **OK** 生成PDM

---

### 第七步：在PDM中优化细节

#### 7.1 设置自增主键

**对每个表的主键：**
1. 双击表，打开表属性
2. 切换到 **Columns** 标签页
3. 找到主键列（如id）
4. 双击该列，打开列属性
5. 切换到 **Standard checks** 标签页
6. 勾选 **Identity**（自增）
7. 点击 **OK**

#### 7.2 添加索引

**对频繁查询的字段：**
1. 双击表
2. 切换到 **Indexes** 标签页
3. 点击 **Add Index**
4. 填写：
   - **Name**: idx_device_id
   - **Unique**: 不勾选（非唯一索引）
   - **Columns**: 选择 device_id
5. 点击 **OK**

**需要添加索引的字段：**
- skin_sensor_data: device_id, sensor_time
- environment_sensor_data: device_id, sensor_time
- daily_statistics: device_id, stat_date
- community_posts: user_id, created_at
- notifications: user_id, is_read

#### 7.3 设置外键约束

**检查所有外键：**
1. 双击表
2. 切换到 **References** 标签页
3. 确认每个外键都设置了：
   - **Delete rule**: CASCADE 或 SET NULL
   - **Update rule**: CASCADE

---

### 第八步：生成SQL脚本

#### 8.1 打开生成对话框

```
Database → Generate Database
或按 Ctrl+Shift+G
```

#### 8.2 配置生成选项

**Generation标签页：**
- **Directory**: 选择输出目录
  ```
  D:\学习\软件设计\data-server\scripts
  ```
- **File name**: `init_mysql_from_pd.sql`
- **Format**: SQL Script

**Options标签页：**
勾选：
- ✓ Generate DROP statements first（先生成DROP语句）
- ✓ Generate CREATE statements（生成CREATE语句）
- ✓ Generate ALTER statements（生成ALTER语句）
- ✓ Generate INSERT statements（如果有初始数据）
- ✓ Generate comments（生成注释）
- ✓ Use schema qualifier（使用数据库名前缀）

**Selection标签页：**
- ✓ All tables
- ✓ All views（如果有）
- ✓ All procedures（如果有）

点击 **OK** 生成SQL文件

---

### 第九步：验证生成的SQL

#### 9.1 对比两个SQL文件

**打开两个文件：**
- `init_mysql_week8.sql`（原有的）
- `init_mysql_from_pd.sql`（新生成的）

**检查差异：**
- 表结构是否一致
- 字段类型是否正确
- 索引是否完整
- 外键约束是否正确

#### 9.2 在MySQL中测试执行

```bash
# SSH连接服务器
ssh root@47.103.108.47

# 备份原数据库
mysqldump -u root -padmin software_design > backup_before_pd.sql

# 删除旧数据库
mysql -u root -padmin -e "DROP DATABASE IF EXISTS software_design;"

# 执行新生成的SQL
mysql -u root -padmin < /path/to/init_mysql_from_pd.sql

# 验证表数量
mysql -u root -padmin -e "USE software_design; SHOW TABLES;" | wc -l
# 应该返回 16（15个表 + 标题行）
```

---

### 第十步：保存和提交

#### 10.1 保存PowerDesigner文件

```
File → Save As
```

**保存位置：**
```
D:\学习\软件设计\docs\powerdesigner_models\
```

**文件名：**
- CDM: `SkinHealthSystem_CDM.cdm`
- PDM: `SkinHealthSystem_PDM.pdm`

#### 10.2 导出ER图为图片

```
File → Export Image
```

**配置：**
- **Format**: PNG
- **Resolution**: 300 DPI
- **File name**: `database_er_diagram.png`
- **Directory**: `D:\学习\软件设计\docs\images\`

#### 10.3 提交到Git

```bash
cd "d:\学习\软件设计"

# 添加PowerDesigner文件
git add docs/powerdesigner_models/*.cdm
git add docs/powerdesigner_models/*.pdm
git add docs/images/database_er_diagram.png
git add data-server/scripts/init_mysql_from_pd.sql

# 提交
git commit -m "feat: 添加PowerDesigner数据库模型文件和ER图

- 新增CDM概念数据模型
- 新增PDM物理数据模型（MySQL 8.0）
- 导出高清ER图
- 生成SQL建表脚本"

# 推送到GitHub
git push origin week8
```

---

## 🎨 ER图美化技巧

### 颜色编码

**为不同类型的实体设置不同颜色：**

1. 选中实体
2. 右键 → Format
3. Fill Color 选择颜色：
   - 🔵 蓝色: 核心业务表（users, devices）
   - 🟢 绿色: 数据采集表（sensor_data）
   - 🟡 黄色: 统计分析表（statistics, reports）
   - 🟣 紫色: 社区功能表（posts, comments）
   - ⚪ 灰色: 系统配置表（configs）

### 分组布局

**将相关实体放在一起：**

```
┌─────────────────┐
│   用户模块       │
│ users           │
│ user_profiles   │
│ user_points     │
└─────────────────┘
        ↓
┌─────────────────┐
│   设备模块       │
│ devices         │
│ device_bindings │
└─────────────────┘
        ↓
┌─────────────────┐
│   数据模块       │
│ skin_sensor_..  │
│ env_sensor_..   │
│ daily_stats     │
└─────────────────┘
```

---

## ⏱️ 预计时间安排

| 步骤 | 预计耗时 | 难度 |
|------|---------|------|
| 创建15个实体 | 30分钟 | ⭐⭐ |
| 添加所有字段属性 | 2小时 | ⭐⭐⭐ |
| 建立14个关系 | 30分钟 | ⭐⭐ |
| 生成PDM并优化 | 1小时 | ⭐⭐⭐ |
| 生成SQL并验证 | 30分钟 | ⭐⭐ |
| 导出图片和文档 | 20分钟 | ⭐ |
| **总计** | **约4.5小时** | |

---

## ❓ 常见问题

### Q1: 字段太多，一个一个添加太慢了怎么办？

**A:** 可以使用批量导入：
1. 先在Excel中整理好字段列表
2. 复制Excel内容
3. 在PD中粘贴（部分版本支持）

或者使用脚本生成（高级用法）。

### Q2: 中文注释显示乱码？

**A:** 
1. Tools → Options → General
2. 设置 Character set: UTF-8
3. 重新添加注释

### Q3: 生成的SQL和原来的不一致？

**A:** 
1. 检查PD中的数据类型是否正确
2. 检查索引和外键是否设置
3. 手动调整生成的SQL

### Q4: 关系线交叉太多，很难看？

**A:** 
1. 使用自动布局: F6
2. 手动拖动实体，减少交叉
3. 使用Orthogonal连线样式

### Q5: PowerDesigner崩溃了怎么办？

**A:** 
1. PD有自动保存功能
2. 查找 `.autosave` 文件
3. 定期手动保存（Ctrl+S）

---

## ✅ 验收标准

完成PowerDesigner设计后，你应该有：

- [ ] `SkinHealthSystem_CDM.cdm` - 概念数据模型文件
- [ ] `SkinHealthSystem_PDM.pdm` - 物理数据模型文件
- [ ] `database_er_diagram.png` - 高清ER图
- [ ] `init_mysql_from_pd.sql` - 生成的SQL脚本
- [ ] SQL脚本能成功在MySQL中执行
- [ ] 15个表全部创建成功
- [ ] 所有外键关系正确
- [ ] 所有索引已添加
- [ ] 所有字段有中文注释

---

## 📚 参考资料

- **PowerDesigner教程**: `docs/POWERDESIGNER_TUTORIAL.md`
- **小程序功能规划**: `docs/WEEK8_MINIPROGRAM_PLAN.md`
- **原有SQL脚本**: `data-server/scripts/init_mysql_week8.sql`
- **数据库设计总结**: `docs/WEEK8_COMPLETION_SUMMARY.md`

---

## 🎯 下一步

完成PowerDesigner设计后：

1. ✅ 将.pdm和.cdm文件提交到Git
2. ✅ 将ER图插入到项目文档中
3. ✅ 更新README.md，添加数据库设计章节
4. ✅ 准备演示材料（ER图截图）
5. ✅ 编写数据库设计说明文档

祝你顺利完成PowerDesigner设计！💪
