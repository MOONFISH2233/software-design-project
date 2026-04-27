# PowerDesigner 数据库设计教程

## 📖 目录
1. [PowerDesigner简介](#powerdesigner简介)
2. [安装与配置](#安装与配置)
3. [创建概念数据模型(CDM)](#创建概念数据模型cdm)
4. [创建物理数据模型(PDM)](#创建物理数据模型pdm)
5. [生成SQL脚本](#生成sql脚本)
6. [反向工程](#反向工程)
7. [实战：皮肤健康系统数据库设计](#实战皮肤健康系统数据库设计)
8. [常见问题](#常见问题)

---

## PowerDesigner简介

**PowerDesigner** 是Sybase公司（现SAP）推出的企业级数据建模工具，支持：
- 概念数据模型（CDM）
- 物理数据模型（PDM）
- 面向对象模型（OOM）
- 业务流程模型（BPM）

### 主要功能
✅ 可视化ER图设计  
✅ 正向工程（模型→SQL）  
✅ 反向工程（数据库→模型）  
✅ 多数据库支持（MySQL、Oracle、SQL Server等）  
✅ 数据字典管理  
✅ 模型版本控制  

---

## 安装与配置

### 1. 下载安装
- **官网**: https://www.sap.com/products/powerdesigner.html
- **版本推荐**: PowerDesigner 16.7 或更高版本
- **系统要求**: Windows 7/10/11, 4GB+ RAM

### 2. 首次配置
1. 启动 PowerDesigner
2. Tools → Options
3. 设置默认DBMS: MySQL 8.0
4. 配置代码页: UTF-8

---

## 创建概念数据模型(CDM)

### 步骤1: 新建CDM
```
File → New Model → Conceptual Data Model
Model name: SkinHealthSystem
DBMS: 选择任意（CDM不依赖具体DBMS）
```

### 步骤2: 创建实体(Entity)

#### 方法1: 工具栏创建
1. 点击左侧工具栏 **Entity** 图标
2. 在画布空白处点击
3. 双击实体框编辑属性

#### 方法2: 菜单创建
```
Model → Entities → Add Entity
```

### 步骤3: 定义实体属性

双击实体打开属性对话框：

**General标签页:**
- **Name**: 实体中文名（如"用户信息"）
- **Code**: 实体英文名（如"user_info"，对应表名）
- **Comment**: 实体说明

**Attributes标签页:**
点击 **Add Attribute** 按钮添加字段：

| 字段 | 说明 | 示例 |
|------|------|------|
| Name | 字段中文名 | 用户ID |
| Code | 字段英文名 | user_id |
| Data Type | 数据类型 | Integer |
| Primary | 是否主键 | ✓ |
| Mandatory | 是否必填 | ✓ |
| Comment | 字段注释 | 主键，自增 |

**常用数据类型映射:**
```
Integer       → INT
String(n)     → VARCHAR(n)
Date          → DATE
DateTime      → DATETIME
Float         → FLOAT
Double        → DOUBLE
Boolean       → TINYINT(1)
Text          → TEXT
JSON          → JSON (MySQL 5.7+)
```

### 步骤4: 创建关系(Relationship)

#### 一对一关系 (1:1)
1. 点击工具栏 **Relationship** 图标
2. 从父实体拖拽到子实体
3. 双击关系线设置属性：
   - **Name**: 关系名称
   - **Cardinality**: 1,1 → 1,1

#### 一对多关系 (1:n)
1. 同上创建关系
2. 设置Cardinality: 1,1 → 0,n

#### 多对多关系 (m:n)
CDM中直接创建m:n关系，生成PDM时会自动创建中间表。

### 步骤5: 设置继承(Inheritance)
如果存在继承关系（如"普通用户"继承"用户"）：
```
Model → Inheritances → Add Inheritance
```

---

## 创建物理数据模型(PDM)

### 方法1: 从CDM生成PDM
```
Tools → Generate Physical Data Model
```

**配置选项:**
1. **DBMS**: 选择 MySQL 8.0
2. **Options**:
   - ✓ Generate tables
   - ✓ Generate views
   - ✓ Generate indexes
   - ✓ Generate foreign keys
   - ✓ Generate checks
3. **Naming Conventions**:
   - Table prefix: tbl_ (可选)
   - Column naming: 保持原样

点击 **OK** 生成PDM。

### 方法2: 直接创建PDM
```
File → New Model → Physical Data Model
DBMS: MySQL 8.0
```

后续操作同CDM，但可以直接设置数据库特性。

### PDM特有功能

#### 1. 设置索引
双击表 → Indexes标签页 → Add Index
- **Unique**: 唯一索引
- **Clustered**: 聚簇索引
- **Columns**: 选择索引列

#### 2. 设置触发器
双击表 → Triggers标签页 → Add Trigger

#### 3. 设置存储过程
```
Database → Stored Procedures → Add Procedure
```

#### 4. 设置视图
```
Database → Views → Add View
```

---

## 生成SQL脚本

### 步骤1: 打开生成对话框
```
Database → Generate Database
```

### 步骤2: 配置生成选项

**Generation标签页:**
- **Directory**: 选择输出目录
- **File name**: 输入文件名（如 skin_health.sql）
- **Format**: SQL Script

**Options标签页:**
- ✓ Generate DROP statements first
- ✓ Generate CREATE statements
- ✓ Generate ALTER statements
- ✓ Generate INSERT statements (如有初始数据)
- ✓ Generate comments

**Selection标签页:**
选择要生成的对象：
- ✓ All tables
- ✓ All views
- ✓ All procedures

### 步骤3: 生成SQL
点击 **OK**，生成 .sql 文件。

### 步骤4: 执行SQL
```bash
# 方法1: 命令行执行
mysql -u root -p < skin_health.sql

# 方法2: MySQL Workbench
File → Open SQL Script → 选择文件 → Execute

# 方法3: phpMyAdmin
导入 → 选择文件 → 执行
```

---

## 反向工程

### 从现有数据库导入模型

#### 步骤1: 连接数据库
```
File → Reverse Engineer → Database
```

#### 步骤2: 配置连接
**Connection标签页:**
- **DBMS**: MySQL 8.0
- **Connection profile**: 新建或选择已有配置
  - Host: localhost
  - Port: 3306
  - Database: software_design
  - User: root
  - Password: admin

#### 步骤3: 选择对象
**Selection标签页:**
- 勾选要导入的表
- 或点击 "Select All"

#### 步骤4: 执行导入
点击 **OK**，自动生成CDM/PDM。

### 从SQL脚本导入
```
File → Reverse Engineer → SQL Script File
选择 .sql 文件 → OK
```

---

## 实战：皮肤健康系统数据库设计

### 需求分析
设计一个皮肤健康监测系统的数据库，包含：
- 用户管理
- 设备管理
- 传感器数据采集
- 健康报告
- 社区功能
- 消息通知

### 设计步骤

#### 第1步: 创建CDM

1. **新建CDM**
   ```
   File → New Model → Conceptual Data Model
   Name: SkinHealthCDM
   ```

2. **创建核心实体**

   **实体1: 用户 (users)**
   - user_id (PK, Integer)
   - username (String(50))
   - password_hash (String(255))
   - nickname (String(50))
   - phone (String(20))
   - email (String(100))
   - avatar_url (String(255))
   - role (String(20))
   - status (String(20))
   - created_at (DateTime)

   **实体2: 设备 (devices)**
   - device_id (PK, String(20))
   - device_type (String(50))
   - firmware_version (String(20))
   - status (String(20))
   - battery_level (Integer)
   - last_heartbeat (DateTime)

   **实体3: 皮肤数据 (skin_sensor_data)**
   - id (PK, BigInt)
   - device_id (FK, String(20))
   - moisture (Integer)
   - oiliness (Integer)
   - temperature (Float)
   - sensor_time (DateTime)

   **实体4: 环境数据 (environment_sensor_data)**
   - id (PK, BigInt)
   - device_id (FK, String(20))
   - temperature (Float)
   - humidity (Float)
   - pm25 (Integer)
   - co2 (Integer)
   - sensor_time (DateTime)

   **实体5: 设备绑定 (device_bindings)**
   - id (PK, Integer)
   - user_id (FK, Integer)
   - device_id (FK, String(20))
   - bind_time (DateTime)
   - is_primary (Boolean)

   **实体6: 健康报告 (health_reports)**
   - id (PK, BigInt)
   - user_id (FK, Integer)
   - report_type (String(20))
   - report_date (Date)
   - content_json (JSON)
   - score (Float)

   **实体7: 社区帖子 (community_posts)**
   - id (PK, BigInt)
   - user_id (FK, Integer)
   - title (String(200))
   - content (Text)
   - like_count (Integer)
   - created_at (DateTime)

   **实体8: 帖子评论 (post_comments)**
   - id (PK, BigInt)
   - post_id (FK, BigInt)
   - user_id (FK, Integer)
   - parent_comment_id (FK, BigInt)
   - content (Text)
   - created_at (DateTime)

   **实体9: 消息通知 (notifications)**
   - id (PK, BigInt)
   - user_id (FK, Integer)
   - type (String(20))
   - title (String(200))
   - content (Text)
   - is_read (Boolean)
   - created_at (DateTime)

3. **创建关系**
   - users (1) → (n) device_bindings
   - devices (1) → (n) device_bindings
   - users (1) → (n) health_reports
   - users (1) → (n) community_posts
   - community_posts (1) → (n) post_comments
   - users (1) → (n) notifications
   - devices (1) → (n) skin_sensor_data
   - devices (1) → (n) environment_sensor_data

#### 第2步: 生成PDM

```
Tools → Generate Physical Data Model
DBMS: MySQL 8.0
Options: 全选
OK
```

#### 第3步: 优化PDM

1. **添加索引**
   - skin_sensor_data: idx_device_id, idx_sensor_time
   - environment_sensor_data: idx_device_id, idx_sensor_time
   - community_posts: idx_user_id, idx_created_at

2. **设置外键约束**
   确保所有FK都设置了 ON DELETE CASCADE 或 SET NULL

3. **添加注释**
   为每个表和字段添加中文注释

#### 第4步: 生成SQL

```
Database → Generate Database
Directory: D:\学习\软件设计\data-server\scripts
File name: init_mysql_week8.sql
Options: 全选
OK
```

#### 第5步: 验证SQL

在MySQL中执行生成的SQL，检查是否有错误。

---

## 常见问题

### Q1: 中文乱码怎么办？
**A:** 
1. 设置CDM/PDM编码为UTF-8
2. 生成SQL时选择UTF-8编码
3. MySQL数据库字符集设置为utf8mb4

### Q2: 如何批量修改字段类型？
**A:**
```
Edit → Find and Replace
搜索: 旧类型
替换: 新类型
范围: 当前模型
```

### Q3: 如何导出ER图为图片？
**A:**
```
File → Export Image
格式: PNG/JPG/SVG
分辨率: 300 DPI
```

### Q4: 如何处理循环依赖？
**A:**
1. 删除一个外键约束
2. 生成SQL后手动添加
3. 或使用延迟约束（DEFERRABLE）

### Q5: 如何比较两个模型的差异？
**A:**
```
Tools → Compare Models
选择模型1和模型2
生成差异报告
```

### Q6: PowerDesigner免费版有吗？
**A:**
官方无免费版，但可试用30天。替代方案：
- MySQL Workbench（免费）
- dbdiagram.io（在线，免费）
- Draw.io（在线，免费）
- ERDPlus（在线，免费）

### Q7: 如何设置自增主键？
**A:**
在PDM中：
1. 双击表
2. Columns标签页
3. 选择主键列
4. Properties → Identity: ✓ Autoincrement

### Q8: 如何添加枚举类型？
**A:**
MySQL不支持原生ENUM，建议：
1. 使用VARCHAR + CHECK约束
2. 或在应用层验证

---

## 最佳实践

### 1. 命名规范
- 表名: 小写+下划线（user_info）
- 字段名: 小写+下划线（user_id）
- 主键: id 或 表名_id
- 外键: 关联表名_id

### 2. 索引策略
- 主键自动创建索引
- 外键字段添加索引
- 频繁查询字段添加索引
- 避免过多索引（影响写入性能）

### 3. 数据类型选择
- ID: INT/BIGINT（根据数据量）
- 短文本: VARCHAR(n)
- 长文本: TEXT
- 金额: DECIMAL(10,2)
- 时间: DATETIME
- 布尔: TINYINT(1)

### 4. 注释完整
- 每个表添加注释
- 每个字段添加注释
- 便于团队协作和维护

### 5. 版本控制
- 定期保存 .pdm 文件
- 使用Git管理模型文件
- 记录每次变更

---

## 快速参考卡片

### 快捷键
```
Ctrl+N      新建模型
Ctrl+O      打开模型
Ctrl+S      保存模型
Ctrl+E      生成PDM
F4          属性对话框
F5          刷新显示
Delete      删除选中对象
```

### 常用菜单路径
```
新建CDM:     File → New Model → Conceptual Data Model
新建PDM:     File → New Model → Physical Data Model
生成PDM:     Tools → Generate Physical Data Model
生成SQL:     Database → Generate Database
反向工程:    File → Reverse Engineer → Database
导出图片:    File → Export Image
```

### 数据类型对照表
| CDM类型 | MySQL类型 | 说明 |
|---------|-----------|------|
| Integer | INT | 整数 |
| BigInt | BIGINT | 大整数 |
| String(n) | VARCHAR(n) | 变长字符串 |
| Char(n) | CHAR(n) | 定长字符串 |
| Date | DATE | 日期 |
| Time | TIME | 时间 |
| DateTime | DATETIME | 日期时间 |
| Float | FLOAT | 单精度浮点 |
| Double | DOUBLE | 双精度浮点 |
| Boolean | TINYINT(1) | 布尔值 |
| Text | TEXT | 长文本 |
| Binary | BLOB | 二进制 |

---

## 学习资源

### 官方文档
- SAP PowerDesigner Help: https://help.sap.com/viewer/p/POWERDESIGNER

### 视频教程
- B站搜索: "PowerDesigner教程"
- YouTube: "PowerDesigner Tutorial"

### 在线工具
- dbdiagram.io: 在线ER图设计
- Draw.io: 免费在线绘图
- MySQL Workbench: 官方免费工具

### 书籍推荐
- 《PowerDesigner数据库建模实战》
- 《数据库系统概念》

---

## 总结

通过本教程，你应该能够：
✅ 使用PowerDesigner创建CDM和PDM  
✅ 设计完整的ER图  
✅ 生成MySQL建表SQL脚本  
✅ 从数据库反向工程模型  
✅ 遵循数据库设计规范  

**下一步:**
1. 按照教程完成皮肤健康系统的数据库设计
2. 生成SQL脚本并在MySQL中执行
3. 将.pdm文件提交到Git仓库
4. 编写数据库设计文档

祝你学习愉快！🎉
