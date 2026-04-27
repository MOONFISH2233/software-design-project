# MongoDB Compass 客户端安装指南

## 什么是 MongoDB Compass？

MongoDB Compass 是 MongoDB 官方提供的**图形化数据库管理工具**，类似：
- MySQL 的 Navicat / MySQL Workbench
- PostgreSQL 的 pgAdmin
- SQL Server 的 SSMS

**作用**：不用写命令行，通过界面就能查看、管理MongoDB数据库。

---

## 📥 下载与安装

### 方法1: 官方网站下载（推荐）

**下载地址**：https://www.mongodb.com/try/download/compass

**选择版本**：
- 操作系统：Windows
- 包类型：ZIP（解压即用）或 MSI（安装包）
- 推荐：**Windows (64-bit) MSI**

**安装步骤**：
1. 下载完成后双击 `.msi` 文件
2. 点击"下一步" → "安装" → "完成"
3. 安装位置：`C:\Program Files\MongoDB\Compass`

### 方法2: 如果官网下载慢

**国内镜像下载**：
```
https://downloads.mongodb.com/compass/mongodb-compass-1.43.1-win32-x64.msi
```

---

## 🚀 连接到你的服务器

### 连接信息

安装完成后，打开 MongoDB Compass，填写连接信息：

```
连接字符串格式：
mongodb://<用户名>:<密码>@<IP地址>:<端口>/<数据库名>
```

**你的连接信息**：
```
mongodb://47.103.108.47:27017/sensor_data
```

**参数说明**：
- **IP地址**：47.103.108.47（你的服务器公网IP）
- **端口**：27017（MongoDB默认端口）
- **数据库名**：sensor_data（你的数据库）
- **用户名/密码**：无（当前未设置认证）

### 连接步骤

**Step 1: 打开 MongoDB Compass**

从开始菜单或桌面快捷方式打开

**Step 2: 填写连接信息**

在主界面选择 "New Connection" → 填写：

```
Connection String:
mongodb://47.103.108.47:27017/sensor_data
```

或分步填写：
- Hostname: 47.103.108.47
- Port: 27017
- Authentication: None（无认证）

**Step 3: 点击 "Connect" 连接**

连接成功后，左侧会显示数据库列表

**Step 4: 查看数据**

展开 `sensor_data` 数据库 → 查看集合：
- skin_sensor
- environment_sensor
- device_status

点击任一集合，右侧显示数据记录

---

## 🔧 如果连接失败

### 问题1: 连接超时

**原因**：阿里云安全组未开放27017端口

**解决方法**：
1. 登录阿里云控制台
2. 找到你的ECS实例
3. 进入"安全组" → "配置规则"
4. 添加入方向规则：
   - 端口：27017
   - 协议：TCP
   - 授权对象：0.0.0.0/0（或你的IP）
5. 保存后重试

### 问题2: 拒绝连接

**原因**：MongoDB只允许本地访问

**解决方法**：
```bash
# SSH登录服务器
ssh root@47.103.108.47

# 编辑MongoDB配置文件
vi /etc/mongod.conf

# 找到 bindIp 这一行
# 将 127.0.0.1 改为 0.0.0.0
bindIp: 0.0.0.0

# 保存退出后重启MongoDB
systemctl restart mongod
```

---

## 📸 向老师展示的截图

连接成功后，给老师展示以下截图：

### 截图1: 连接成功界面
- 显示连接字符串
- 显示连接状态"Connected"

### 截图2: 数据库集合列表
- 展开 sensor_data 数据库
- 显示3个集合：skin_sensor, environment_sensor, device_status

### 截图3: 数据记录查看
- 点击 skin_sensor 集合
- 显示数据记录列表
- 展示JSON格式数据

### 截图4: 索引管理
- 点击集合的 "Indexes" 标签
- 显示已创建的索引
- 证明索引设计已完成

---

## 🎯 向老师说明

```
老师好，这是MongoDB的图形化管理工具 Compass。

通过它我们可以：
1. 直观查看数据库中的集合和数据
2. 管理索引（已创建14个索引）
3. 执行查询和聚合操作
4. 监控数据库性能

连接信息：
- 服务器：47.103.108.47
- 端口：27017
- 数据库：sensor_data

目前已经连接成功，可以看到所有数据。
```

---

## 💡 其他MongoDB客户端选择

除了 Compass，还有其他选择：

| 工具 | 类型 | 优点 | 推荐度 |
|------|------|------|--------|
| **MongoDB Compass** | 官方图形工具 | 免费、功能全、官方支持 | ⭐⭐⭐⭐⭐ |
| **Navicat for MongoDB** | 商业软件 | 界面友好、功能强大 | ⭐⭐⭐⭐ |
| **Studio 3T** | 专业工具 | SQL查询支持、智能提示 | ⭐⭐⭐⭐ |
| **MongoDB Shell** | 命令行 | 灵活、脚本化 | ⭐⭐⭐ |
| **Robo 3T** | 轻量级工具 | 免费、简洁 | ⭐⭐⭐ |

**推荐：MongoDB Compass（官方、免费、功能够用）**

---

## ❓ 常见问题

### Q1: 需要用户名密码吗？
**A**: 当前你的MongoDB未设置认证，直接连接即可。

### Q2: 连接后能看到什么？
**A**: 
- 数据库列表（sensor_data）
- 集合列表（3个集合）
- 数据记录（JSON格式）
- 索引信息（14个索引）

### Q3: 能在Compass里执行命令吗？
**A**: 可以！Compass提供了查询界面，也可以执行聚合管道。

### Q4: 需要付费吗？
**A**: MongoDB Compass 完全免费！

---

**现在就下载并安装 MongoDB Compass 吧！🚀**
