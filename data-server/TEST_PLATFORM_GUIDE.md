# 🚀 数据服务器全功能测试平台使用指南

## 📋 概述

这是一个功能完整的Web测试平台，支持验证数据服务器的**所有核心功能**。

### ✅ 已实现的功能模块

1. **🔐 认证功能**
   - 用户登录（JWT Token获取）
   - API Key生成和管理

2. **🔒 加密解密**
   - AES-256数据加密
   - 数据解密验证

3. **📥 数据接收**
   - 普通公开接口
   - JWT认证安全接口
   - API Key认证接口

4. **🌡️ 传感器数据**
   - 皮肤传感器（湿度、油脂）
   - 环境传感器（温湿度、光照）
   - 设备状态监控

5. **📊 数据统计**
   - 文件数量统计
   - 存储空间分析
   - 目录分布查看

6. **⚡ 批量测试**
   - 一键式全功能测试
   - 实时进度显示
   - 测试结果汇总

---

## 🌐 访问地址

### 生产环境（阿里云服务器）
```
http://47.103.108.47:5000/test
```

### 本地开发环境
```
http://localhost:5000/test
```

---

## 🎯 快速开始

### 1️⃣ 打开测试页面

在浏览器中访问：`http://47.103.108.47:5000/test`

### 2️⃣ 确认服务器地址

确保页面顶部的"服务器地址"输入框显示：`http://47.103.108.47:5000`

点击 **"检查健康状态"** 按钮，确认服务正常运行。

### 3️⃣ 开始测试

有两种方式：

#### 方式一：逐个功能测试
1. 点击顶部的功能标签页（认证/加密/数据接收等）
2. 填写测试参数（已有默认值）
3. 点击对应的"测试"按钮
4. 查看测试结果

#### 方式二：一键式批量测试
1. 切换到 **"⚡ 批量测试"** 标签页
2. 点击 **"🎯 开始一键式全功能测试"** 按钮
3. 等待自动执行所有12项测试
4. 查看最终汇总结果

---

## 📖 详细功能说明

### 🔐 认证功能测试

#### 用户登录
- **接口**: `POST /api/auth/login`
- **参数**: 
  - 用户名: `admin`（默认）
  - 密码: `admin123`（默认）
- **返回**: JWT Token（用于后续认证）

#### 生成API Key
- **接口**: `POST /api/auth/apikey`
- **前置条件**: 需要先登录获取JWT Token
- **返回**: API Key（用于API Key认证）

---

### 🔒 加密解密测试

#### 数据加密
- **接口**: `POST /api/encrypt`
- **功能**: 使用AES-256加密JSON数据
- **返回**: Base64编码的加密数据

#### 数据解密
- **接口**: `POST /api/decrypt`
- **功能**: 解密AES加密的数据
- **前置条件**: 需要先加密数据
- **返回**: 原始JSON数据

---

### 📥 数据接收测试

#### 普通数据接收
- **接口**: `POST /api/receive`
- **认证**: 无需认证
- **保存目录**: `data/`

#### JWT认证数据接收
- **接口**: `POST /api/receive/secure`
- **认证**: Bearer Token（JWT）
- **保存目录**: `data/`（文件名带用户名）

#### API Key数据接收
- **接口**: `POST /api/receive/apikey`
- **认证**: X-API-Key请求头
- **保存目录**: `data/`（文件名带用户名）

---

### 🌡️ 传感器数据测试

#### 皮肤传感器
- **接口**: `POST /api/sensor/skin`
- **必填字段**:
  - `moisture`: 水分度（0-100）
  - `oiliness`: 油亮度（0-100）
- **保存目录**: `data/skin_sensor/`

#### 环境传感器
- **接口**: `POST /api/sensor/environment`
- **必填字段**:
  - `humidity`: 湿度（0-100）
  - `light_lux`: 光照度（Lux）
  - `temperature`: 温度（℃）
- **保存目录**: `data/environment/`

#### 设备状态
- **接口**: `POST /api/device/status`
- **必填字段**:
  - `device_id`: 设备ID
  - `status`: 状态（online/offline/running/error/standby）
- **选填字段**:
  - `battery`: 电量（0-100）
  - `cpu_usage`: CPU使用率
- **保存目录**: `data/device/`

---

### 📊 数据统计

- **接口**: `GET /api/stats`
- **功能**: 统计所有已接收文件
- **返回信息**:
  - 总文件数
  - 总大小（字节/MB）
  - 各目录文件分布

---

## 🎨 界面说明

### 标签页导航
- **🔐 认证功能**: 登录和API Key管理
- **🔒 加密解密**: 数据加密和解密测试
- **📥 数据接收**: 三种数据接收方式
- **🌡️ 传感器数据**: 三种传感器接口
- **📊 数据统计**: 文件统计信息
- **⚡ 批量测试**: 一键式全功能测试

### 状态徽章
- 🟡 **待测试**: 黄色徽章，等待测试
- 🟢 **通过**: 绿色徽章，测试成功
- 🔴 **失败**: 红色徽章，测试失败

### 结果展示
- **成功**: 绿色背景，格式化JSON
- **失败**: 红色背景，错误信息

---

## 🔧 常见问题

### Q1: 健康检查失败？
**A**: 检查以下几点：
1. 服务器地址是否正确（应该是 `http://47.103.108.47:5000`）
2. 浏览器是否阻止了跨域请求（已配置CORS，应该没问题）
3. 服务器是否正常运行：`ssh root@47.103.108.47 systemctl status gunicorn-flask-data-server`

### Q2: 登录失败？
**A**: 确认用户名和密码：
- 默认管理员: `admin` / `admin123`
- 普通用户: `user1` / `user123`

### Q3: 批量测试部分失败？
**A**: 批量测试有依赖关系：
- 登录失败 → API Key生成和数据接收会失败
- 加密失败 → 解密测试会失败
- 先单独测试失败的项，查看具体错误

### Q4: 如何修改测试数据？
**A**: 每个测试项都有输入框，可以直接修改：
- 用户名/密码
- 加密数据（JSON格式）
- 传感器数值

---

## 📞 服务器管理

### 查看服务状态
```bash
ssh root@47.103.108.47
systemctl status gunicorn-flask-data-server
```

### 重启服务
```bash
systemctl restart gunicorn-flask-data-server
```

### 查看日志
```bash
# 实时日志
journalctl -u gunicorn-flask-data-server -f

# 应用日志
tail -f /root/course-project/logs/server_*.log
```

### 更新代码
```bash
cd /root/course-project
git pull origin week5
systemctl restart gunicorn-flask-data-server
```

---

## 🎯 默认测试账户

| 用户名 | 密码 | 角色 | 说明 |
|--------|------|------|------|
| admin | admin123 | 管理员 | 所有权限 |
| user1 | user123 | 普通用户 | 基本权限 |
| user2 | user123 | 普通用户 | 基本权限 |
| user3 | user123 | 普通用户 | 基本权限 |

---

## 📝 API接口清单

| 接口路径 | 方法 | 认证 | 功能 |
|---------|------|------|------|
| `/api/health` | GET | 无 | 健康检查 |
| `/api/auth/login` | POST | 无 | 用户登录 |
| `/api/auth/apikey` | POST | JWT | 生成API Key |
| `/api/encrypt` | POST | 无 | 数据加密 |
| `/api/decrypt` | POST | 无 | 数据解密 |
| `/api/receive` | POST | 无 | 普通数据接收 |
| `/api/receive/secure` | POST | JWT | 安全数据接收 |
| `/api/receive/apikey` | POST | API Key | API Key数据接收 |
| `/api/sensor/skin` | POST | 无 | 皮肤传感器 |
| `/api/sensor/environment` | POST | 无 | 环境传感器 |
| `/api/device/status` | POST | 无 | 设备状态 |
| `/api/stats` | GET | 无 | 数据统计 |

---

## 🚀 技术栈

- **前端**: HTML5 + CSS3 + JavaScript (Fetch API)
- **后端**: Python 3.6 + Flask + Gunicorn
- **安全**: JWT + API Key + AES-256
- **部署**: Systemd + Gunicorn (5 workers)
- **跨域**: flask-cors

---

## 📚 相关文档

- [前端测试平台开发指南](./FRONTEND_TEST_GUIDE.md)
- [远程服务器部署指南](./DEPLOY_TO_SERVER.md)
- [快速开始](./QUICK_TEST_START.md)
- [项目文件清单](./FILES_CHECKLIST.md)

---

**祝你使用愉快！** 🎉

*最后更新: 2026-04-08*