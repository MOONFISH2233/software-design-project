# 皮肤健康监测系统 - 数据库设计完整说明文档

**项目名称**: 皮肤健康监测小程序  
**文档版本**: V1.0  
**创建日期**: 2026-04-27  
**数据库**: MySQL 8.0  
**表数量**: 15个表 + 2个视图

---

## 目录

1. [数据库整体架构](#1-数据库整体架构)
2. [模块一：数据采集层](#2-模块一数据采集层)
3. [模块二：用户管理层](#3-模块二用户管理层)
4. [模块三：设备关联层](#4-模块三设备关联层)
5. [模块四：社区互动层](#5-模块四社区互动层)
6. [模块五：系统功能层](#6-模块五系统功能层)
7. [完整ER关系图](#7-完整er关系图)
8. [核心业务流程](#8-核心业务流程)
9. [数据字典总览](#9-数据字典总览)

---

## 1. 数据库整体架构

### 1.1 设计原则

本数据库采用**模块化分层设计**，将15个表划分为5大功能模块：

```
┌─────────────────────────────────────────────────┐
│           皮肤健康监测系统数据库架构              │
├─────────────────────────────────────────────────┤
│                                                 │
│  【数据采集层】4个表                             │
│  devices, skin_sensor_data,                     │
│  environment_sensor_data, daily_statistics      │
│                                                 │
│  【用户管理层】3个表                             │
│  users, user_profiles, health_reports           │
│                                                 │
│  【设备关联层】1个表                             │
│  device_bindings                                │
│                                                 │
│  【社区互动层】2个表                             │
│  community_posts, post_comments                 │
│                                                 │
│  【系统功能层】5个表                             │
│  notifications, user_points,                    │
│  skincare_products, user_skincare_records,      │
│  system_configs                                 │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 1.2 模块职责

| 模块 | 表数量 | 核心职责 | 数据量级 |
|------|--------|---------|---------|
| 数据采集层 | 4 | 设备数据采集与统计分析 | 百万级/天 |
| 用户管理层 | 3 | 用户账号与个人档案管理 | 万级 |
| 设备关联层 | 1 | 用户与设备绑定关系 | 万级 |
| 社区互动层 | 2 | 用户社区动态与评论 | 十万级 |
| 系统功能层 | 5 | 通知、积分、产品管理等 | 万级 |

---

## 2. 模块一：数据采集层

**模块定位**: 负责IoT设备数据的采集、存储和统计分析  
**数据特点**: 高频写入、海量数据、时序性强  
**核心表**: 4个

### 2.1 devices（设备信息表）

#### 表说明
存储所有皮肤监测设备的基本信息和状态

#### 字段定义

| 字段名 | 数据类型 | 约束 | 说明 | 示例 |
|--------|---------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 主键ID | 1 |
| device_id | VARCHAR(20) | UNIQUE, NOT NULL | 设备唯一标识 | "DEV001" |
| device_type | VARCHAR(50) | - | 设备类型 | "皮肤检测仪" |
| firmware_version | VARCHAR(20) | - | 固件版本 | "v2.1.0" |
| install_date | DATE | - | 安装日期 | 2026-01-15 |
| location | VARCHAR(100) | - | 安装位置 | "客厅" |
| status | VARCHAR(20) | DEFAULT 'online' | 设备状态 | online/offline/maintenance |
| battery_level | INT | - | 电池电量(%) | 85 |
| signal_strength | INT | - | 信号强度 | -65 |
| last_heartbeat | DATETIME | - | 最后心跳时间 | 2026-04-27 20:00:00 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 | - |
| updated_at | DATETIME | ON UPDATE | 更新时间 | - |

#### 索引设计
- `idx_device_id`: 设备ID索引（唯一）
- `idx_status`: 状态索引（查询在线设备）

#### 实际场景
```
设备注册流程：
1. 新设备首次连接服务器
2. 自动在devices表插入记录
3. 设备每分钟发送心跳包更新last_heartbeat
4. 超过5分钟未收到心跳，状态自动变为offline
```

#### 数据量预估
- 小型系统: 10-100台设备
- 中型系统: 100-1000台设备
- 大型系统: 1000+台设备

---

### 2.2 skin_sensor_data（皮肤传感器数据表）

#### 表说明
存储皮肤监测的原始数据，包括水分、油脂、温度等指标

#### 字段定义

| 字段名 | 数据类型 | 约束 | 说明 | 示例 |
|--------|---------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键ID | 100001 |
| device_id | VARCHAR(20) | NOT NULL, FK | 设备ID | "DEV001" |
| moisture | INT | NOT NULL | 皮肤水分含量 | 65 |
| oiliness | INT | NOT NULL | 皮肤油脂度 | 42 |
| temperature | FLOAT | - | 皮肤温度(°C) | 33.5 |
| sensor_time | DATETIME | NOT NULL | 传感器采集时间 | 2026-04-27 14:30:00 |
| received_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 服务器接收时间 | - |
| client_ip | VARCHAR(45) | - | 客户端IP地址 | 192.168.1.100 |
| request_id | VARCHAR(100) | - | 请求追踪ID | "req_abc123" |
| validated | BOOLEAN | DEFAULT TRUE | 是否通过验证 | TRUE |
| quality_score | FLOAT | - | 数据质量评分 | 0.95 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 记录创建时间 | - |

#### 索引设计
- `idx_device_id`: 设备ID索引（高频查询）
- `idx_sensor_time`: 采集时间索引（时间范围查询）
- `idx_received_at`: 接收时间索引（数据同步）

#### 实际场景
```
数据采集流程：
1. 设备DEV001每秒采集一次皮肤数据
2. 通过MQTT/HTTP发送到服务器
3. 服务器验证数据后写入本表
4. 一天产生86400条记录（每秒1条）

查询示例：
-- 查询某设备今天的平均水分
SELECT AVG(moisture) FROM skin_sensor_data
WHERE device_id='DEV001' 
  AND DATE(sensor_time)='2026-04-27';
```

#### 数据量预估
- 1台设备/天: 86,400条
- 10台设备/天: 864,000条
- 100台设备/天: 8,640,000条
- **建议**: 按月分表或使用时序数据库优化

---

### 2.3 environment_sensor_data（环境传感器数据表）

#### 表说明
存储环境监测数据，包括温度、湿度、PM2.5、CO2等

#### 字段定义

| 字段名 | 数据类型 | 约束 | 说明 | 示例 |
|--------|---------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键ID | 200001 |
| device_id | VARCHAR(20) | NOT NULL, FK | 设备ID | "DEV001" |
| temperature | FLOAT | - | 环境温度(°C) | 25.3 |
| humidity | FLOAT | - | 环境湿度(%) | 55 |
| pm25 | INT | - | PM2.5浓度(μg/m³) | 35 |
| co2 | INT | - | CO2浓度(ppm) | 450 |
| location | VARCHAR(100) | - | 地理位置 | "客厅" |
| latitude | FLOAT | - | 纬度 | 39.9042 |
| longitude | FLOAT | - | 经度 | 116.4074 |
| sensor_time | DATETIME | NOT NULL | 采集时间 | 2026-04-27 14:30:00 |
| received_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 接收时间 | - |
| client_ip | VARCHAR(45) | - | 客户端IP | 192.168.1.100 |
| request_id | VARCHAR(100) | - | 请求追踪ID | "req_def456" |
| validated | BOOLEAN | DEFAULT TRUE | 是否通过验证 | TRUE |
| quality_score | FLOAT | - | 数据质量评分 | 0.98 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 | - |

#### 索引设计
- `idx_device_id`: 设备ID索引
- `idx_sensor_time`: 采集时间索引
- `idx_received_at`: 接收时间索引

#### 实际场景
```
环境数据分析：
1. 环境湿度低 → 可能导致皮肤干燥
2. PM2.5高 → 可能影响皮肤健康
3. 温度变化 → 影响皮脂分泌

关联查询：
-- 查询某时段的环境与皮肤数据对比
SELECT 
    esd.humidity,
    ssd.moisture,
    ssd.oiliness
FROM environment_sensor_data esd
JOIN skin_sensor_data ssd 
  ON esd.device_id = ssd.device_id 
  AND esd.sensor_time = ssd.sensor_time
WHERE esd.device_id='DEV001'
  AND esd.sensor_time BETWEEN '2026-04-27 08:00' AND '2026-04-27 20:00';
```

#### 数据量预估
与skin_sensor_data相同，建议采用相同的数据管理策略

---

### 2.4 daily_statistics（每日统计表）

#### 表说明
每天凌晨2点定时任务自动生成的统计数据，用于快速查询和历史趋势分析

#### 字段定义

| 字段名 | 数据类型 | 约束 | 说明 | 示例 |
|--------|---------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 主键ID | 1 |
| stat_date | DATE | UNIQUE, NOT NULL | 统计日期 | 2026-04-26 |
| total_records | INT | DEFAULT 0 | 总记录数 | 864000 |
| active_devices | INT | DEFAULT 0 | 活跃设备数 | 95 |
| avg_moisture | FLOAT | - | 平均水分含量 | 62.5 |
| avg_oiliness | FLOAT | - | 平均油脂度 | 45.2 |
| avg_temperature | FLOAT | - | 平均温度 | 33.8 |
| avg_humidity | FLOAT | - | 平均湿度 | 58.3 |
| avg_pm25 | FLOAT | - | 平均PM2.5 | 42.1 |
| avg_co2 | FLOAT | - | 平均CO2 | 480 |
| max_records_device | VARCHAR(20) | - | 记录最多的设备 | "DEV001" |
| min_records_device | VARCHAR(20) | - | 记录最少的设备 | "DEV089" |
| calculated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 计算时间 | 2026-04-27 02:00:00 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 | - |

#### 索引设计
- `idx_stat_date`: 统计日期索引（唯一）

#### 定时任务逻辑
```python
# tasks/daily_statistics.py
@staticmethod
def calculate_daily_stats():
    """每日凌晨2点执行"""
    yesterday = (datetime.now() - timedelta(days=1)).date()
    
    sql = """
    INSERT INTO daily_statistics (
        stat_date, total_records, active_devices,
        avg_moisture, avg_oiliness, avg_temperature
    )
    SELECT 
        %s,
        COUNT(*),
        COUNT(DISTINCT device_id),
        AVG(moisture),
        AVG(oiliness),
        AVG(temperature)
    FROM skin_sensor_data
    WHERE DATE(sensor_time) = %s
    """
    
    db.execute(sql, (yesterday, yesterday))
```

#### 实际场景
```
查询最近7天的趋势：
SELECT stat_date, avg_moisture, avg_oiliness
FROM daily_statistics
WHERE stat_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
ORDER BY stat_date;

结果：
┌────────────┬──────────────┬──────────────┐
│ stat_date  │ avg_moisture │ avg_oiliness │
├──────────────────────────────────────────┤
│ 2026-04-21 │     61.2     │     46.8     │
│ 2026-04-22 │     62.5     │     45.3     │
│ 2026-04-23 │     63.1     │     44.9     │
│ ...        │     ...      │     ...      │
└────────────┴──────────────┴──────────────┘
```

#### 数据量预估
- 每天1条记录
- 一年365条
- 10年3650条
- **无需分表**

---

## 3. 模块二：用户管理层

**模块定位**: 负责用户账号管理、个人资料和健康报告  
**数据特点**: 用户核心数据、安全性要求高  
**核心表**: 3个

### 3.1 users（用户基础表）⭐核心表

#### 表说明
存储用户登录和基础信息，是整个系统的核心表

#### 字段定义

| 字段名 | 数据类型 | 约束 | 说明 | 示例 |
|--------|---------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 主键ID | 1 |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 用户名 | "xiaoming" |
| password_hash | VARCHAR(255) | NOT NULL | 密码哈希 | "$2b$12$..." |
| nickname | VARCHAR(50) | - | 昵称 | "小明" |
| phone | VARCHAR(20) | - | 手机号 | "13800138000" |
| email | VARCHAR(100) | - | 邮箱 | "xiaoming@example.com" |
| avatar_url | VARCHAR(255) | - | 头像URL | "/uploads/avatar_1.jpg" |
| role | VARCHAR(20) | DEFAULT 'user' | 角色 | admin/user |
| status | VARCHAR(20) | DEFAULT 'active' | 状态 | active/inactive/banned |
| last_login | DATETIME | - | 最后登录时间 | 2026-04-27 19:30:00 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 | - |
| updated_at | DATETIME | ON UPDATE | 更新时间 | - |

#### 索引设计
- `idx_username`: 用户名索引（唯一，登录查询）
- `idx_phone`: 手机号索引（手机号登录）

#### 安全设计
```python
# 密码加密
from werkzeug.security import generate_password_hash, check_password_hash

# 注册时加密
password_hash = generate_password_hash('user_password')

# 登录时验证
if check_password_hash(stored_hash, input_password):
    login_success()
```

#### 实际场景
```sql
-- 用户注册
INSERT INTO users (username, password_hash, phone, nickname)
VALUES ('xiaoming', '$2b$12$encrypted...', '13800138000', '小明');

-- 用户登录
SELECT id, username, role, status FROM users
WHERE username='xiaoming' AND status='active';

-- 更新最后登录时间
UPDATE users SET last_login=NOW() WHERE id=1;
```

#### 关联关系
此表是**中心表**，被以下表引用：
- user_profiles (1:1)
- health_reports (1:n)
- device_bindings (1:n)
- community_posts (1:n)
- post_comments (1:n)
- notifications (1:n)
- user_points (1:1)
- user_skincare_records (1:n)

---

### 3.2 user_profiles（用户详细档案表）

#### 表说明
存储用户肤质、身体数据等详细个人信息

#### 字段定义

| 字段名 | 数据类型 | 约束 | 说明 | 示例 |
|--------|---------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 主键ID | 1 |
| user_id | INT | NOT NULL, FK, UNIQUE | 用户ID | 1 |
| skin_type | VARCHAR(20) | - | 肤质类型 | oily/dry/mixed/sensitive |
| skincare_goals | JSON | - | 护肤目标 | ["控油", "保湿"] |
| age | INT | - | 年龄 | 25 |
| gender | VARCHAR(10) | - | 性别 | male/female/other |
| birthday | DATE | - | 生日 | 1999-05-15 |
| height | FLOAT | - | 身高(cm) | 175.5 |
| weight | FLOAT | - | 体重(kg) | 68.5 |
| allergies | TEXT | - | 过敏史 | "对酒精过敏" |
| medical_conditions | TEXT | - | 健康状况 | "无特殊疾病" |
| register_date | DATETIME | DEFAULT CURRENT_TIMESTAMP | 注册日期 | - |
| last_update | DATETIME | ON UPDATE | 最后更新 | - |

#### 外键约束
```sql
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
```
- 当用户删除时，档案自动删除

#### 索引设计
- `uk_user_id`: 用户ID唯一索引
- `idx_skin_type`: 肤质索引（推荐产品）

#### 设计理由
**为什么分开users和user_profiles？**

| 对比项 | users表 | user_profiles表 |
|--------|---------|----------------|
| 用途 | 登录认证 | 个性化服务 |
| 数据量 | 少（10个字段） | 多（13个字段） |
| 访问频率 | 高（每次登录） | 中（查看资料时） |
| 安全级别 | 高（密码） | 中（个人资料） |
| 性能影响 | 小 | 大 |

**好处**:
1. 登录时只查询users表，速度快
2. 个人资料更新不影响登录
3. 数据库结构清晰，职责分离

#### 实际场景
```sql
-- 完善个人资料
INSERT INTO user_profiles (
    user_id, skin_type, skincare_goals, age, gender, allergies
)
VALUES (
    1, 
    'oily', 
    '["控油", "保湿", "抗衰老"]',
    25, 
    'female',
    '对酒精、果酸过敏'
);

-- 根据肤质推荐产品
SELECT * FROM skincare_products
WHERE JSON_CONTAINS(suitable_skin_type, '"oily"')
LIMIT 10;
```

---

### 3.3 health_reports（健康报告表）

#### 表说明
自动生成或手动创建的健康分析报告，支持日报、周报、月报、年报

#### 字段定义

| 字段名 | 数据类型 | 约束 | 说明 | 示例 |
|--------|---------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键ID | 1001 |
| user_id | INT | NOT NULL, FK | 用户ID | 1 |
| report_type | VARCHAR(20) | NOT NULL | 报告类型 | daily/weekly/monthly/yearly |
| report_date | DATE | NOT NULL | 报告日期 | 2026-04-26 |
| start_date | DATE | - | 起始日期 | 2026-04-20 |
| end_date | DATE | - | 结束日期 | 2026-04-26 |
| content_json | JSON | - | 报告内容 | {详细数据} |
| score | FLOAT | - | 综合评分(0-100) | 85.5 |
| suggestions | TEXT | - | 改善建议 | "建议增加保湿" |
| is_generated | BOOLEAN | DEFAULT FALSE | 是否已生成 | TRUE |
| generated_at | DATETIME | - | 生成时间 | 2026-04-27 03:00:00 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 | - |

#### 外键约束
```sql
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
```

#### 索引设计
- `idx_user_id`: 用户ID索引
- `idx_report_type`: 报告类型索引
- `idx_report_date`: 报告日期索引
- `uk_user_report`: 联合唯一索引(user_id, report_type, report_date)

#### 报告生成逻辑
```python
def generate_daily_report(user_id, report_date):
    """生成日报"""
    # 1. 查询当日皮肤数据
    skin_data = db.query("""
        SELECT AVG(moisture) as avg_moisture,
               AVG(oiliness) as avg_oiliness,
               AVG(temperature) as avg_temp
        FROM skin_sensor_data
        WHERE user_id IN (
            SELECT device_id FROM device_bindings WHERE user_id=%s
        )
        AND DATE(sensor_time) = %s
    """, (user_id, report_date))
    
    # 2. 计算评分
    score = calculate_health_score(skin_data)
    
    # 3. 生成建议
    suggestions = generate_suggestions(skin_data)
    
    # 4. 组装报告内容
    content = {
        'skin_data': skin_data,
        'environment_data': env_data,
        'trend_analysis': trend,
        'score_breakdown': score_detail
    }
    
    # 5. 写入数据库
    db.execute("""
        INSERT INTO health_reports 
        (user_id, report_type, report_date, content_json, score, suggestions)
        VALUES (%s, 'daily', %s, %s, %s, %s)
    """, (user_id, report_date, json.dumps(content), score, suggestions))
    
    # 6. 推送通知
    send_notification(user_id, '您的日报已生成', report_id)
```

#### 实际场景
```sql
-- 查询用户的报告历史
SELECT report_type, report_date, score, suggestions
FROM health_reports
WHERE user_id = 1
ORDER BY report_date DESC
LIMIT 10;

结果：
┌────────────┬────────────┬───────┬──────────────────┐
│ report_type│report_date │ score │   suggestions    │
├────────────────────────────────────────────────────┤
│ daily      │ 2026-04-26 │ 85.5  │ 皮肤状态良好     │
│ daily      │ 2026-04-25 │ 82.3  │ 油脂分泌略高     │
│ weekly     │ 2026-04-20 │ 83.8  │ 需要注意保湿     │
│ monthly    │ 2026-04-01 │ 80.5  │ 建议调整护肤方案 │
└────────────┴────────────┴───────┴──────────────────┘
```

#### 报告内容示例(JSON)
```json
{
  "skin_data": {
    "avg_moisture": 65.2,
    "avg_oiliness": 42.8,
    "avg_temperature": 33.5
  },
  "environment_data": {
    "avg_humidity": 55.3,
    "avg_pm25": 35.2
  },
  "trend_analysis": {
    "moisture_trend": "上升",
    "oiliness_trend": "下降"
  },
  "score_breakdown": {
    "moisture_score": 88,
    "oiliness_score": 82,
    "overall_score": 85.5
  }
}
```

---

## 4. 模块三：设备关联层

**模块定位**: 管理用户与设备的绑定关系  
**核心表**: 1个

### 4.1 device_bindings（设备绑定关系表）⭐关键表

#### 表说明
记录用户与设备的绑定关系，是多对多关系的中间表

#### 字段定义

| 字段名 | 数据类型 | 约束 | 说明 | 示例 |
|--------|---------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 主键ID | 1 |
| user_id | INT | NOT NULL, FK | 用户ID | 1 |
| device_id | VARCHAR(20) | NOT NULL, FK | 设备ID | "DEV001" |
| bind_time | DATETIME | DEFAULT CURRENT_TIMESTAMP | 绑定时间 | 2026-04-01 10:00:00 |
| is_primary | BOOLEAN | DEFAULT FALSE | 是否主设备 | TRUE |
| status | VARCHAR(20) | DEFAULT 'active' | 状态 | active/inactive/unbound |
| unbind_time | DATETIME | - | 解绑时间 | 2026-05-01 15:30:00 |
| notes | TEXT | - | 备注 | "客厅主设备" |

#### 外键约束
```sql
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE
```

#### 索引设计
- `uk_user_device`: 联合唯一索引(user_id, device_id)
- `idx_user_id`: 用户ID索引
- `idx_device_id`: 设备ID索引

#### 实际场景

**场景1: 家庭共享设备**
```
小明家：
├─ 小明 (user_id=1)
│   ├─ DEV001 (主设备) ✓
│   └─ DEV002
└─ 妈妈 (user_id=2)
    └─ DEV003 (共用DEV001)

绑定关系：
┌─────────┬───────────┬────────────┬──────────┐
│ user_id │ device_id │ is_primary │  status  │
├──────────────────────────────────────────────┤
│    1    │  DEV001   │    TRUE    │  active  │  ← 小明的主设备
│    1    │  DEV002   │   FALSE    │  active  │
│    2    │  DEV001   │    TRUE    │  active  │  ← 妈妈也绑定DEV001
│    2    │  DEV003   │    TRUE    │  active  │
└─────────┴───────────┴────────────┴──────────┘
```

**场景2: 设备更换**
```sql
-- 绑定新设备
INSERT INTO device_bindings (user_id, device_id, is_primary, notes)
VALUES (1, 'DEV004', TRUE, '新购买的设备');

-- 将旧设备设为非主设备
UPDATE device_bindings 
SET is_primary = FALSE, status = 'inactive'
WHERE user_id = 1 AND device_id = 'DEV001';

-- 解绑设备
UPDATE device_bindings
SET status = 'unbound', unbind_time = NOW()
WHERE user_id = 1 AND device_id = 'DEV002';
```

**场景3: 查询用户的设备列表**
```sql
-- 查询用户的所有活跃设备
SELECT 
    d.device_id,
    d.device_type,
    d.status,
    db.is_primary,
    db.bind_time
FROM devices d
JOIN device_bindings db ON d.device_id = db.device_id
WHERE db.user_id = 1 
  AND db.status = 'active'
ORDER BY db.is_primary DESC, db.bind_time DESC;

结果：
┌───────────┬────────────┬────────┬────────────┬─────────────────────┐
│ device_id │device_type │ status │ is_primary │     bind_time       │
├────────────────────────────────────────────────────────────────────┤
│  DEV001   │皮肤检测仪  │ online │    TRUE    │ 2026-04-01 10:00:00 │
│  DEV002   │环境检测仪  │ online │   FALSE    │ 2026-04-05 14:30:00 │
└───────────┴────────────┴────────┴────────────┴─────────────────────┘
```

---

## 5. 模块四：社区互动层

**模块定位**: 实现用户社区功能，类似微信朋友圈/小红书  
**核心表**: 2个

### 5.1 community_posts（社区帖子表）

#### 表说明
存储用户发布的帖子、动态、经验分享等内容

#### 字段定义

| 字段名 | 数据类型 | 约束 | 说明 | 示例 |
|--------|---------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键ID | 1001 |
| user_id | INT | NOT NULL, FK | 发帖用户ID | 1 |
| title | VARCHAR(200) | NOT NULL | 帖子标题 | "我的控油经验分享" |
| content | TEXT | NOT NULL | 帖子内容 | "用了某某产品后..." |
| images_json | JSON | - | 图片列表 | ["url1.jpg","url2.jpg"] |
| tags | JSON | - | 标签列表 | ["控油","经验分享"] |
| category | VARCHAR(50) | - | 分类 | experience/question/review/share |
| like_count | INT | DEFAULT 0 | 点赞数 | 128 |
| comment_count | INT | DEFAULT 0 | 评论数 | 35 |
| view_count | INT | DEFAULT 0 | 浏览数 | 2580 |
| share_count | INT | DEFAULT 0 | 分享数 | 45 |
| is_top | BOOLEAN | DEFAULT FALSE | 是否置顶 | FALSE |
| is_essence | BOOLEAN | DEFAULT FALSE | 是否精华 | TRUE |
| status | VARCHAR(20) | DEFAULT 'published' | 状态 | published/draft/deleted |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 | - |
| updated_at | DATETIME | ON UPDATE | 更新时间 | - |

#### 外键约束
```sql
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
```

#### 索引设计
- `idx_user_id`: 用户ID索引
- `idx_category`: 分类索引
- `idx_created_at`: 创建时间索引（排序）
- `ft_content`: 全文索引（搜索）

#### 实际场景

**发布帖子**
```sql
INSERT INTO community_posts (
    user_id, title, content, images_json, tags, category
)
VALUES (
    1,
    '我的控油经验分享',
    '今天试了新方法，效果不错！分享给大家...',
    '["https://img.example.com/post_1001_1.jpg", 
      "https://img.example.com/post_1001_2.jpg"]',
    '["控油", "经验分享", "护肤心得"]',
    'experience'
);
```

**热门帖子排行**
```sql
SELECT 
    p.id,
    p.title,
    u.nickname,
    p.like_count,
    p.comment_count,
    p.created_at
FROM community_posts p
JOIN users u ON p.user_id = u.id
WHERE p.status = 'published'
ORDER BY p.like_count DESC
LIMIT 10;
```

**点赞功能**
```sql
-- 点赞
UPDATE community_posts 
SET like_count = like_count + 1
WHERE id = 1001;

-- 取消点赞
UPDATE community_posts 
SET like_count = GREATEST(like_count - 1, 0)
WHERE id = 1001;
```

---

### 5.2 post_comments（帖子评论表）

#### 表说明
存储帖子的评论和回复，支持楼中楼功能

#### 字段定义

| 字段名 | 数据类型 | 约束 | 说明 | 示例 |
|--------|---------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键ID | 5001 |
| post_id | BIGINT | NOT NULL, FK | 帖子ID | 1001 |
| user_id | INT | NOT NULL, FK | 评论用户ID | 2 |
| parent_comment_id | BIGINT | FK | 父评论ID（回复用） | NULL或5001 |
| content | TEXT | NOT NULL | 评论内容 | "这个产品确实好用！" |
| images_json | JSON | - | 评论图片 | ["img1.jpg"] |
| like_count | INT | DEFAULT 0 | 点赞数 | 15 |
| status | VARCHAR(20) | DEFAULT 'published' | 状态 | published/deleted |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 | - |
| updated_at | DATETIME | ON UPDATE | 更新时间 | - |

#### 外键约束
```sql
FOREIGN KEY (post_id) REFERENCES community_posts(id) ON DELETE CASCADE
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
FOREIGN KEY (parent_comment_id) REFERENCES post_comments(id) ON DELETE CASCADE
```

#### 索引设计
- `idx_post_id`: 帖子ID索引
- `idx_user_id`: 用户ID索引
- `idx_parent_comment_id`: 父评论ID索引

#### 实际场景

**评论结构示例**
```
帖子 #1001: "我的控油经验分享"
│
├─ 评论#5001 (小红): "请问用的是什么产品？" 
│   │  parent_comment_id = NULL (直接评论帖子)
│   │
│   └─ 评论#5002 (小明): "用的是某某品牌的洁面乳"
│       │  parent_comment_id = 5001 (回复评论#5001)
│       │
│       └─ 评论#5005 (小红): "谢谢分享！"
│           │  parent_comment_id = 5002 (回复评论#5002)
│
├─ 评论#5003 (小李): "我也在用，效果不错！"
│   │  parent_comment_id = NULL
│
└─ 评论#5004 (小王): "敏感肌可以用吗？"
    │  parent_comment_id = NULL
    │
    └─ 评论#5006 (小明): "可以的，这个很温和"
        │  parent_comment_id = 5004
```

**查询帖子的所有评论**
```sql
SELECT 
    c.id,
    u.nickname,
    c.content,
    c.parent_comment_id,
    c.like_count,
    c.created_at
FROM post_comments c
JOIN users u ON c.user_id = u.id
WHERE c.post_id = 1001
  AND c.status = 'published'
ORDER BY c.created_at ASC;
```

**自引用设计要点**
```sql
-- parent_comment_id = NULL  → 直接评论帖子
-- parent_comment_id = 5001  → 回复评论#5001
-- 可以无限层级回复（实际建议限制3层）
```

---

## 6. 模块五：系统功能层

**模块定位**: 提供通知、积分、产品管理等系统级功能  
**核心表**: 5个

### 6.1 notifications（消息通知表）

#### 表说明
系统推送给用户的各类消息通知

#### 字段定义

| 字段名 | 数据类型 | 约束 | 说明 | 示例 |
|--------|---------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键ID | 10001 |
| user_id | INT | NOT NULL, FK | 接收用户ID | 1 |
| type | VARCHAR(20) | NOT NULL | 通知类型 | system/data/interaction/promotion |
| title | VARCHAR(200) | NOT NULL | 通知标题 | "您的日报已生成" |
| content | TEXT | - | 通知内容 | "点击查看详细内容" |
| related_id | VARCHAR(100) | - | 关联ID | "2001" (报告ID) |
| related_type | VARCHAR(50) | - | 关联类型 | post/report/device |
| is_read | BOOLEAN | DEFAULT FALSE | 是否已读 | FALSE |
| read_at | DATETIME | - | 阅读时间 | 2026-04-27 15:30:00 |
| action_url | VARCHAR(255) | - | 跳转链接 | "/reports/2001" |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 | - |
| expires_at | DATETIME | - | 过期时间 | 2026-05-27 00:00:00 |

#### 通知类型说明

| 类型 | 说明 | 示例 |
|------|------|------|
| system | 系统通知 | "系统维护通知" |
| data | 数据通知 | "日报已生成"、"设备离线" |
| interaction | 互动通知 | "有人回复了你的帖子" |
| promotion | 推广通知 | "签到送积分" |

#### 实际场景

**推送通知**
```python
def send_report_notification(user_id, report_id):
    """报告生成后推送通知"""
    db.execute("""
        INSERT INTO notifications 
        (user_id, type, title, content, related_id, related_type, action_url)
        VALUES (%s, 'data', '您的日报已生成', 
                '点击查看今日皮肤健康报告', %s, 'report', '/reports/%s')
    """, (user_id, report_id, report_id))
```

**查询未读通知**
```sql
SELECT 
    id, type, title, content, related_id, action_url, created_at
FROM notifications
WHERE user_id = 1
  AND is_read = FALSE
ORDER BY created_at DESC
LIMIT 20;
```

**标记已读**
```sql
UPDATE notifications
SET is_read = TRUE, read_at = NOW()
WHERE user_id = 1
  AND id IN (10001, 10002, 10003);
```

---

### 6.2 user_points（用户积分表）

#### 表说明
用户积分和等级系统，激励用户活跃

#### 字段定义

| 字段名 | 数据类型 | 约束 | 说明 | 示例 |
|--------|---------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 主键ID | 1 |
| user_id | INT | NOT NULL, FK, UNIQUE | 用户ID | 1 |
| total_points | INT | DEFAULT 0 | 总积分 | 1580 |
| available_points | INT | DEFAULT 0 | 可用积分 | 850 |
| used_points | INT | DEFAULT 0 | 已用积分 | 500 |
| expired_points | INT | DEFAULT 0 | 过期积分 | 230 |
| level | VARCHAR(20) | DEFAULT 'bronze' | 等级 | bronze/silver/gold/platinum |
| last_update | DATETIME | ON UPDATE | 最后更新 | - |

#### 等级规则

| 等级 | 积分范围 | 权益 |
|------|---------|------|
| bronze 青铜 | 0-500 | 基础功能 |
| silver 白银 | 501-2000 | 解锁高级报告 |
| gold 黄金 | 2001-5000 | 专属客服 |
| platinum 铂金 | 5000+ | 产品试用资格 |

#### 积分获取规则

| 行为 | 积分 | 说明 |
|------|------|------|
| 每日签到 | +10 | 每天限1次 |
| 发布帖子 | +20 | 每次 |
| 帖子被点赞 | +5 | 每次 |
| 连续打卡7天 | +50 | 额外奖励 |
| 完善资料 | +100 | 一次性 |
| 邀请好友 | +200 | 每邀请1人 |

#### 实际场景

**签到获得积分**
```python
def daily_checkin(user_id):
    """每日签到"""
    # 增加积分
    db.execute("""
        UPDATE user_points 
        SET total_points = total_points + 10,
            available_points = available_points + 10
        WHERE user_id = %s
    """, (user_id,))
    
    # 检查等级升级
    check_level_upgrade(user_id)
    
    # 推送通知
    send_notification(user_id, '签到成功', '获得10积分')
```

**等级升级**
```python
def check_level_upgrade(user_id):
    """检查等级升级"""
    points = db.query("SELECT total_points FROM user_points WHERE user_id=%s", (user_id,))
    
    new_level = 'bronze'
    if points >= 5000:
        new_level = 'platinum'
    elif points >= 2000:
        new_level = 'gold'
    elif points >= 500:
        new_level = 'silver'
    
    db.execute("UPDATE user_points SET level=%s WHERE user_id=%s", (new_level, user_id))
```

---

### 6.3 skincare_products（护肤品数据库）

#### 表说明
产品库，类似商品目录，支持搜索和推荐

#### 字段定义

| 字段名 | 数据类型 | 约束 | 说明 | 示例 |
|--------|---------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 主键ID | 1 |
| name | VARCHAR(100) | NOT NULL | 产品名称 | "保湿精华液" |
| brand | VARCHAR(50) | - | 品牌 | "品牌A" |
| category | VARCHAR(50) | - | 分类 | cleanser/toner/serum/moisturizer/sunscreen |
| ingredients | JSON | - | 成分列表 | ["透明质酸","甘油"] |
| suitable_skin_type | JSON | - | 适用肤质 | ["dry","mixed"] |
| price | DECIMAL(10,2) | - | 价格 | 299.00 |
| rating | FLOAT | - | 评分(0-5) | 4.5 |
| review_count | INT | DEFAULT 0 | 评价数 | 1250 |
| description | TEXT | - | 产品描述 | "深层补水..." |
| image_url | VARCHAR(255) | - | 产品图片 | "/products/1.jpg" |
| status | VARCHAR(20) | DEFAULT 'active' | 状态 | active/inactive |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 | - |
| updated_at | DATETIME | ON UPDATE | 更新时间 | - |

#### 索引设计
- `idx_brand`: 品牌索引
- `idx_category`: 分类索引
- `ft_product`: 全文索引（搜索）

#### 实际场景

**根据肤质推荐产品**
```sql
-- 为油性皮肤用户推荐产品
SELECT name, brand, price, rating
FROM skincare_products
WHERE JSON_CONTAINS(suitable_skin_type, '"oily"')
  AND status = 'active'
ORDER BY rating DESC
LIMIT 10;
```

**搜索产品**
```sql
-- 全文搜索
SELECT * FROM skincare_products
WHERE MATCH(name, description) AGAINST('保湿 精华' IN NATURAL LANGUAGE MODE)
LIMIT 20;
```

---

### 6.4 user_skincare_records（用户护肤记录表）

#### 表说明
用户记录每天使用的护肤品，形成个人护肤日记

#### 字段定义

| 字段名 | 数据类型 | 约束 | 说明 | 示例 |
|--------|---------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键ID | 100001 |
| user_id | INT | NOT NULL, FK | 用户ID | 1 |
| product_id | INT | FK | 产品ID | 1 |
| product_name | VARCHAR(100) | - | 产品名称 | "保湿精华液" |
| usage_time | DATETIME | NOT NULL | 使用时间 | 2026-04-27 08:00:00 |
| usage_amount | VARCHAR(50) | - | 使用量 | "2泵" |
| skin_feel | TEXT | - | 使用感受 | "吸收很快，不油腻" |
| effect_rating | INT | - | 效果评分(1-5) | 4 |
| notes | TEXT | - | 备注 | "早上使用" |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 | - |

#### 外键约束
```sql
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
FOREIGN KEY (product_id) REFERENCES skincare_products(id) ON DELETE SET NULL
```

#### 实际场景

**记录护肤**
```sql
INSERT INTO user_skincare_records (
    user_id, product_id, product_name, usage_time, 
    usage_amount, skin_feel, effect_rating
)
VALUES (
    1, 1, '保湿精华液', '2026-04-27 08:00:00',
    '2泵', '吸收很快，不油腻', 4
);
```

**查看护肤历史**
```sql
SELECT 
    usr.usage_time,
    sp.name,
    sp.brand,
    usr.effect_rating,
    usr.skin_feel
FROM user_skincare_records usr
LEFT JOIN skincare_products sp ON usr.product_id = sp.id
WHERE usr.user_id = 1
  AND usr.usage_time >= DATE_SUB(NOW(), INTERVAL 7 DAY)
ORDER BY usr.usage_time DESC;
```

---

### 6.5 system_configs（系统配置表）

#### 表说明
存储系统参数，无需修改代码即可调整配置

#### 字段定义

| 字段名 | 数据类型 | 约束 | 说明 | 示例 |
|--------|---------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 主键ID | 1 |
| config_key | VARCHAR(100) | UNIQUE, NOT NULL | 配置键 | "data.retention_days" |
| config_value | TEXT | - | 配置值 | "365" |
| config_type | VARCHAR(20) | DEFAULT 'string' | 配置类型 | string/int/float/boolean/json |
| description | VARCHAR(255) | - | 配置说明 | "数据保留天数" |
| is_public | BOOLEAN | DEFAULT FALSE | 是否公开 | FALSE |
| updated_by | INT | FK | 更新人ID | 1 |
| updated_at | DATETIME | ON UPDATE | 更新时间 | - |

#### 配置示例

| config_key | config_value | config_type | description |
|------------|-------------|-------------|-------------|
| app.name | "皮肤健康监测小程序" | string | 应用名称 |
| app.version | "1.0.0" | string | 应用版本 |
| data.retention_days | "365" | int | 数据保留天数 |
| report.auto_generate | "true" | boolean | 自动生成报告 |
| notification.enabled | "true" | boolean | 启用通知 |

#### 使用方式
```python
# 获取配置
def get_config(key):
    result = db.query("SELECT config_value, config_type FROM system_configs WHERE config_key=%s", (key,))
    value = result['config_value']
    config_type = result['config_type']
    
    # 类型转换
    if config_type == 'int':
        return int(value)
    elif config_type == 'boolean':
        return value.lower() == 'true'
    elif config_type == 'json':
        return json.loads(value)
    else:
        return value

# 使用配置
retention_days = get_config('data.retention_days')  # 返回 365
auto_generate = get_config('report.auto_generate')  # 返回 True
```

---

## 7. 完整ER关系图

### 7.1 总体架构

```
┌─────────────────────────────────────────────────────────┐
│                    用户模块                              │
│                                                         │
│  users (1) ←→ (1) user_profiles                         │
│    │                                                    │
│    ├─ (n) health_reports          ← 健康报告           │
│    ├─ (n) device_bindings         ← 设备绑定           │
│    ├─ (n) community_posts         ← 社区帖子           │
│    ├─ (n) post_comments           ← 帖子评论           │
│    ├─ (n) notifications           ← 消息通知           │
│    ├─ (1) user_points             ← 用户积分           │
│    └─ (n) user_skincare_records   ← 护肤记录           │
│                                                         │
└─────────────────────────────────────────────────────────┘
                            ↕
                    device_bindings (中间表)
                            ↕
┌─────────────────────────────────────────────────────────┐
│                    设备模块                              │
│                                                         │
│  devices (1)                                            │
│    ├─ (n) skin_sensor_data          ← 皮肤数据         │
│    ├─ (n) environment_sensor_data   ← 环境数据         │
│    └─ (n) daily_statistics          ← 每日统计         │
│                                                         │
└─────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────┐
│                    社区模块                              │
│                                                         │
│  community_posts (1) ←→ (n) post_comments               │
│                                                         │
└─────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────┐
│                    产品模块                              │
│                                                         │
│  skincare_products (1) ←→ (n) user_skincare_records     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 7.2 数据流向

```
用户操作 → Flask API → MySQL数据库
              ↓
        定时任务（每日统计）
              ↓
        自动生成报告 → 推送通知
              ↓
        用户查看 → 社区分享 → 获得积分
```

---

## 8. 核心业务流程

### 8.1 场景：小明的一天

#### 8:00 AM - 登录系统
```sql
-- 验证密码
SELECT id, username, role, status FROM users
WHERE username='xiaoming' AND status='active';

-- 加载个人资料
SELECT * FROM user_profiles WHERE user_id=1;
```

#### 8:05 AM - 记录护肤
```sql
INSERT INTO user_skincare_records (
    user_id, product_id, usage_time, effect_rating
)
VALUES (1, 1, '2026-04-27 08:05:00', 4);
```

#### 8:10 AM - 设备采集数据
```sql
-- 皮肤数据（每秒1条）
INSERT INTO skin_sensor_data (device_id, moisture, oiliness, temperature)
VALUES ('DEV001', 65, 42, 33.5);

-- 环境数据
INSERT INTO environment_sensor_data (device_id, temperature, humidity, pm25)
VALUES ('DEV001', 25.3, 55, 35);
```

#### 12:00 PM - 查看社区
```sql
-- 浏览最新帖子
SELECT * FROM community_posts 
ORDER BY created_at DESC 
LIMIT 20;

-- 点赞
UPDATE community_posts 
SET like_count=like_count+1 
WHERE id=1001;
```

#### 2:00 PM - 收到通知
```sql
-- 查询未读通知
SELECT * FROM notifications 
WHERE user_id=1 AND is_read=FALSE;

-- 标记已读
UPDATE notifications 
SET is_read=TRUE, read_at=NOW() 
WHERE id=5001;
```

#### 11:00 PM - 发布心得
```sql
-- 发布帖子
INSERT INTO community_posts (user_id, title, content)
VALUES (1, '我的控油经验分享', '今天试了新方法...');

-- 获得积分
UPDATE user_points 
SET total_points=total_points+20,
    available_points=available_points+20
WHERE user_id=1;
```

#### 凌晨2:00 AM - 定时任务
```sql
-- 统计今日数据
INSERT INTO daily_statistics (
    stat_date, total_records, avg_moisture, avg_oiliness
)
SELECT 
    DATE(sensor_time),
    COUNT(*),
    AVG(moisture),
    AVG(oiliness)
FROM skin_sensor_data
WHERE sensor_time >= '2026-04-27 00:00:00'
  AND sensor_time < '2026-04-28 00:00:00'
GROUP BY DATE(sensor_time);

-- 生成健康报告
INSERT INTO health_reports (
    user_id, report_type, report_date, score, suggestions
)
VALUES (1, 'daily', '2026-04-27', 85.5, '皮肤状态良好，继续保持');

-- 推送通知
INSERT INTO notifications (
    user_id, type, title, related_id, related_type
)
VALUES (1, 'data', '您的日报已生成', 2001, 'report');
```

---

## 9. 数据字典总览

### 9.1 表清单

| 序号 | 表名 | 中文名称 | 模块 | 数据量级 |
|------|------|---------|------|---------|
| 1 | devices | 设备信息表 | 数据采集 | 百级 |
| 2 | skin_sensor_data | 皮肤传感器数据表 | 数据采集 | 百万级/天 |
| 3 | environment_sensor_data | 环境传感器数据表 | 数据采集 | 百万级/天 |
| 4 | daily_statistics | 每日统计表 | 数据采集 | 百级/年 |
| 5 | users | 用户基础表 | 用户管理 | 万级 |
| 6 | user_profiles | 用户详细档案表 | 用户管理 | 万级 |
| 7 | health_reports | 健康报告表 | 用户管理 | 十万级 |
| 8 | device_bindings | 设备绑定关系表 | 设备关联 | 万级 |
| 9 | community_posts | 社区帖子表 | 社区互动 | 十万级 |
| 10 | post_comments | 帖子评论表 | 社区互动 | 百万级 |
| 11 | notifications | 消息通知表 | 系统功能 | 十万级 |
| 12 | user_points | 用户积分表 | 系统功能 | 万级 |
| 13 | skincare_products | 护肤品数据库 | 系统功能 | 千级 |
| 14 | user_skincare_records | 用户护肤记录表 | 系统功能 | 十万级 |
| 15 | system_configs | 系统配置表 | 系统功能 | 百级 |

### 9.2 索引汇总

| 表名 | 索引字段 | 索引类型 | 用途 |
|------|---------|---------|------|
| devices | device_id | UNIQUE | 设备唯一标识 |
| devices | status | INDEX | 查询在线设备 |
| skin_sensor_data | device_id | INDEX | 按设备查询 |
| skin_sensor_data | sensor_time | INDEX | 时间范围查询 |
| users | username | UNIQUE | 登录查询 |
| users | phone | INDEX | 手机号登录 |
| user_profiles | user_id | UNIQUE | 用户档案 |
| device_bindings | (user_id,device_id) | UNIQUE | 绑定关系唯一 |
| community_posts | created_at | INDEX | 排序查询 |
| post_comments | post_id | INDEX | 帖子评论 |
| notifications | (user_id,is_read) | INDEX | 未读通知 |

---

## 附录

### A. 数据库配置

```sql
-- 创建数据库
CREATE DATABASE IF NOT EXISTS software_design 
    DEFAULT CHARACTER SET utf8mb4 
    DEFAULT COLLATE utf8mb4_unicode_ci;

-- 用户权限
GRANT ALL PRIVILEGES ON software_design.* TO 'app_user'@'%' IDENTIFIED BY 'password';
FLUSH PRIVILEGES;
```

### B. 性能优化建议

1. **大表分表策略**
   - skin_sensor_data: 按月分表 (skin_sensor_202604)
   - environment_sensor_data: 按月分表
   - 使用分区表或分库分表中间件

2. **读写分离**
   - 主库: 写入操作
   - 从库: 查询操作
   - 使用MySQL主从复制

3. **缓存策略**
   - Redis缓存: 用户信息、系统配置
   - 查询缓存: 热门帖子、产品列表

4. **定时清理**
   ```sql
   -- 删除30天前的原始数据（保留统计表）
   DELETE FROM skin_sensor_data 
   WHERE sensor_time < DATE_SUB(NOW(), INTERVAL 30 DAY);
   ```

---

**文档维护记录**

| 版本 | 日期 | 修改内容 | 修改人 |
|------|------|---------|--------|
| V1.0 | 2026-04-27 | 初始版本 | - |

---

**联系方式**
- 项目负责人: [待填写]
- 技术支持: [待填写]
- 文档维护: [待填写]