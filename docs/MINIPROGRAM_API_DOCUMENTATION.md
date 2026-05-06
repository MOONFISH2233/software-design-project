# 皮肤健康监测系统 - 小程序API接口文档

> **版本**: v1.0  
> **最后更新**: 2026-04-29  
> **基础URL**: `http://47.103.108.47:5000/api/miniprogram`

---

## 📋 目录

- [1. 概述](#1-概述)
- [2. 认证机制](#2-认证机制)
- [3. 用户模块](#3-用户模块)
- [4. 设备管理模块](#4-设备管理模块)
- [5. 数据查询模块](#5-数据查询模块)
- [6. 健康报告模块](#6-健康报告模块)
- [7. 通知模块](#7-通知模块)
- [8. 错误码说明](#8-错误码说明)
- [9. Postman集合](#9-postman集合)

---

## 1. 概述

### 1.1 接口规范

| 项目 | 说明 |
|------|------|
| **协议** | HTTP/HTTPS |
| **数据格式** | JSON |
| **字符编码** | UTF-8 |
| **请求方式** | GET / POST / PUT / DELETE |
| **响应格式** | 统一JSON格式 |

### 1.2 通用响应格式

```json
{
    "success": true,
    "message": "操作成功",
    "data": {
        // 具体数据内容
    }
}
```

**字段说明**:
- `success`: boolean - 请求是否成功
- `message`: string - 提示信息
- `data`: object/array - 返回的数据（可选）

### 1.3 分页响应格式

```json
{
    "success": true,
    "message": "查询成功",
    "data": {
        "items": [],      // 数据列表
        "total": 100,     // 总记录数
        "page": 1,        // 当前页码
        "per_page": 20,   // 每页数量
        "pages": 5        // 总页数
    }
}
```

---

## 2. 认证机制

### 2.1 JWT Token认证

所有需要认证的接口都需要在请求头中携带JWT Token。

**获取Token**: 通过登录接口获取

**使用方式**: 在请求头中添加 `Authorization` 字段

```
Authorization: Bearer <your_jwt_token>
```

### 2.2 Token有效期

- **默认有效期**: 7天
- **过期处理**: 返回401状态码，需重新登录获取新Token

---

## 3. 用户模块

### 3.1 用户注册

**接口地址**: `POST /api/miniprogram/user/register`

**是否需要认证**: ❌ 否

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| username | string | ✅ | 用户名（唯一） |
| password | string | ✅ | 密码（最少6位） |
| phone | string | ✅ | 手机号 |
| nickname | string | ❌ | 昵称 |
| avatar | string | ❌ | 头像URL |

**请求示例**:

```json
{
    "username": "user001",
    "password": "password123",
    "phone": "13800138000",
    "nickname": "小明",
    "avatar": "https://example.com/avatar.jpg"
}
```

**响应示例**:

```json
{
    "success": true,
    "message": "注册成功",
    "data": {
        "user_id": 1,
        "username": "user001",
        "nickname": "小明",
        "phone": "13800138000",
        "created_at": "2026-04-29T00:00:00"
    }
}
```

**错误响应**:

```json
{
    "success": false,
    "message": "用户名已存在"
}
```

---

### 3.2 用户登录

**接口地址**: `POST /api/miniprogram/user/login`

**是否需要认证**: ❌ 否

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| username | string | ✅ | 用户名或手机号 |
| password | string | ✅ | 密码 |

**请求示例**:

```json
{
    "username": "user001",
    "password": "password123"
}
```

**响应示例**:

```json
{
    "success": true,
    "message": "登录成功",
    "data": {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "user": {
            "user_id": 1,
            "username": "user001",
            "nickname": "小明",
            "phone": "13800138000",
            "avatar": "https://example.com/avatar.jpg"
        }
    }
}
```

**重要提示**: 
- 登录后必须保存 `token` 字段
- 后续请求需在Header中携带此Token

---

### 3.3 获取个人信息

**接口地址**: `GET /api/miniprogram/user/profile`

**是否需要认证**: ✅ 是

**请求头**:

```
Authorization: Bearer <token>
```

**请求参数**: 无

**响应示例**:

```json
{
    "success": true,
    "message": "查询成功",
    "data": {
        "user_id": 1,
        "username": "user001",
        "nickname": "小明",
        "phone": "13800138000",
        "avatar": "https://example.com/avatar.jpg",
        "gender": "male",
        "age": 25,
        "skin_type": "oily",
        "created_at": "2026-04-29T00:00:00",
        "updated_at": "2026-04-29T12:00:00"
    }
}
```

---

### 3.4 更新个人信息

**接口地址**: `PUT /api/miniprogram/user/profile`

**是否需要认证**: ✅ 是

**请求头**:

```
Authorization: Bearer <token>
Content-Type: application/json
```

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| nickname | string | ❌ | 昵称 |
| avatar | string | ❌ | 头像URL |
| gender | string | ❌ | 性别（male/female） |
| age | integer | ❌ | 年龄 |
| skin_type | string | ❌ | 肤质（oily/dry/combination/sensitive） |

**请求示例**:

```json
{
    "nickname": "大明",
    "avatar": "https://example.com/new_avatar.jpg",
    "gender": "male",
    "age": 26,
    "skin_type": "combination"
}
```

**响应示例**:

```json
{
    "success": true,
    "message": "更新成功",
    "data": {
        "user_id": 1,
        "nickname": "大明",
        "avatar": "https://example.com/new_avatar.jpg",
        "updated_at": "2026-04-29T12:30:00"
    }
}
```

---

## 4. 设备管理模块

### 4.1 绑定设备

**接口地址**: `POST /api/miniprogram/device/bind`

**是否需要认证**: ✅ 是

**请求头**:

```
Authorization: Bearer <token>
Content-Type: application/json
```

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| device_id | string | ✅ | 设备ID |
| device_name | string | ❌ | 设备名称 |
| location | string | ❌ | 使用位置 |

**请求示例**:

```json
{
    "device_id": "DEV_001",
    "device_name": "我的皮肤检测仪",
    "location": "家中"
}
```

**响应示例**:

```json
{
    "success": true,
    "message": "设备绑定成功",
    "data": {
        "binding_id": 1,
        "device_id": "DEV_001",
        "device_name": "我的皮肤检测仪",
        "location": "家中",
        "bind_time": "2026-04-29T12:00:00"
    }
}
```

**错误响应**:

```json
{
    "success": false,
    "message": "设备不存在"
}
```

---

### 4.2 获取设备列表

**接口地址**: `GET /api/miniprogram/device/list`

**是否需要认证**: ✅ 是

**请求头**:

```
Authorization: Bearer <token>
```

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | integer | ❌ | 页码，默认1 |
| per_page | integer | ❌ | 每页数量，默认20 |

**请求示例**:

```
GET /api/miniprogram/device/list?page=1&per_page=10
```

**响应示例**:

```json
{
    "success": true,
    "message": "查询成功",
    "data": {
        "items": [
            {
                "binding_id": 1,
                "device_id": "DEV_001",
                "device_name": "我的皮肤检测仪",
                "device_type": "skin_sensor",
                "status": "online",
                "battery_level": 85,
                "signal_strength": -45,
                "location": "家中",
                "last_heartbeat": "2026-04-29T12:00:00",
                "bind_time": "2026-04-29T10:00:00"
            }
        ],
        "total": 1,
        "page": 1,
        "per_page": 20,
        "pages": 1
    }
}
```

---

### 4.3 获取设备状态

**接口地址**: `GET /api/miniprogram/device/status/{device_id}`

**是否需要认证**: ✅ 是

**请求头**:

```
Authorization: Bearer <token>
```

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| device_id | string | ✅ | 设备ID |

**请求示例**:

```
GET /api/miniprogram/device/status/DEV_001
```

**响应示例**:

```json
{
    "success": true,
    "message": "查询成功",
    "data": {
        "device_id": "DEV_001",
        "device_name": "我的皮肤检测仪",
        "status": "online",
        "battery_level": 85,
        "signal_strength": -45,
        "firmware_version": "v1.0.0",
        "last_heartbeat": "2026-04-29T12:00:00",
        "install_date": "2026-04-01",
        "location": "家中"
    }
}
```

---

## 5. 数据查询模块

### 5.1 查询皮肤数据

**接口地址**: `GET /api/miniprogram/data/skin`

**是否需要认证**: ✅ 是

**请求头**:

```
Authorization: Bearer <token>
```

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| device_id | string | ❌ | 设备ID（不传则查询所有设备） |
| start_date | string | ❌ | 开始日期（YYYY-MM-DD） |
| end_date | string | ❌ | 结束日期（YYYY-MM-DD） |
| days | integer | ❌ | 最近N天（与start_date/end_date二选一） |
| page | integer | ❌ | 页码，默认1 |
| per_page | integer | ❌ | 每页数量，默认20 |

**请求示例**:

```
# 查询最近7天的数据
GET /api/miniprogram/data/skin?days=7&page=1&per_page=20

# 查询指定日期范围
GET /api/miniprogram/data/skin?start_date=2026-04-01&end_date=2026-04-28
```

**响应示例**:

```json
{
    "success": true,
    "message": "查询成功",
    "data": {
        "items": [
            {
                "id": 1,
                "device_id": "DEV_001",
                "moisture": 65.2,
                "oiliness": 42.1,
                "temperature": 36.5,
                "sensor_time": "2026-04-28T12:00:00",
                "received_at": "2026-04-28T12:00:05"
            }
        ],
        "total": 100,
        "page": 1,
        "per_page": 20,
        "pages": 5
    }
}
```

---

### 5.2 查询环境数据

**接口地址**: `GET /api/miniprogram/data/environment`

**是否需要认证**: ✅ 是

**请求头**:

```
Authorization: Bearer <token>
```

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| device_id | string | ❌ | 设备ID |
| start_date | string | ❌ | 开始日期（YYYY-MM-DD） |
| end_date | string | ❌ | 结束日期（YYYY-MM-DD） |
| days | integer | ❌ | 最近N天 |
| page | integer | ❌ | 页码，默认1 |
| per_page | integer | ❌ | 每页数量，默认20 |

**请求示例**:

```
GET /api/miniprogram/data/environment?days=7&page=1&per_page=20
```

**响应示例**:

```json
{
    "success": true,
    "message": "查询成功",
    "data": {
        "items": [
            {
                "id": 1,
                "device_id": "DEV_001",
                "temperature": 25.5,
                "humidity": 55.2,
                "pm25": 35,
                "co2": 450,
                "sensor_time": "2026-04-28T12:00:00",
                "received_at": "2026-04-28T12:00:05"
            }
        ],
        "total": 80,
        "page": 1,
        "per_page": 20,
        "pages": 4
    }
}
```

---

### 5.3 查询统计数据

**接口地址**: `GET /api/miniprogram/data/statistics`

**是否需要认证**: ✅ 是

**请求头**:

```
Authorization: Bearer <token>
```

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| days | integer | ❌ | 最近N天，默认7 |
| start_date | string | ❌ | 开始日期 |
| end_date | string | ❌ | 结束日期 |

**请求示例**:

```
GET /api/miniprogram/data/statistics?days=30
```

**响应示例**:

```json
{
    "success": true,
    "message": "查询成功",
    "data": [
        {
            "stat_date": "2026-04-28",
            "avg_moisture": 64.5,
            "avg_oiliness": 43.2,
            "avg_temperature": 36.8,
            "avg_humidity": 52.1,
            "active_devices": 5,
            "total_records": 150
        },
        {
            "stat_date": "2026-04-27",
            "avg_moisture": 63.8,
            "avg_oiliness": 44.1,
            "avg_temperature": 36.5,
            "avg_humidity": 51.5,
            "active_devices": 4,
            "total_records": 120
        }
    ]
}
```

---

## 6. 健康报告模块

### 6.1 获取报告列表

**接口地址**: `GET /api/miniprogram/report/list`

**是否需要认证**: ✅ 是

**请求头**:

```
Authorization: Bearer <token>
```

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | integer | ❌ | 页码，默认1 |
| per_page | integer | ❌ | 每页数量，默认10 |
| report_type | string | ❌ | 报告类型（daily/weekly/monthly） |

**请求示例**:

```
GET /api/miniprogram/report/list?page=1&per_page=10
```

**响应示例**:

```json
{
    "success": true,
    "message": "查询成功",
    "data": {
        "items": [
            {
                "report_id": 1,
                "report_type": "daily",
                "title": "2026-04-28 皮肤健康日报",
                "generate_time": "2026-04-29T02:00:00",
                "summary": "今日皮肤状态良好，水分充足",
                "score": 85
            }
        ],
        "total": 30,
        "page": 1,
        "per_page": 10,
        "pages": 3
    }
}
```

---

### 6.2 获取报告详情

**接口地址**: `GET /api/miniprogram/report/detail/{report_id}`

**是否需要认证**: ✅ 是

**请求头**:

```
Authorization: Bearer <token>
```

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| report_id | integer | ✅ | 报告ID |

**请求示例**:

```
GET /api/miniprogram/report/detail/1
```

**响应示例**:

```json
{
    "success": true,
    "message": "查询成功",
    "data": {
        "report_id": 1,
        "report_type": "daily",
        "title": "2026-04-28 皮肤健康日报",
        "generate_time": "2026-04-29T02:00:00",
        "summary": "今日皮肤状态良好，水分充足",
        "score": 85,
        "details": {
            "moisture_analysis": {
                "average": 65.2,
                "trend": "stable",
                "evaluation": "水分充足"
            },
            "oiliness_analysis": {
                "average": 42.1,
                "trend": "decreasing",
                "evaluation": "油脂分泌正常"
            },
            "recommendations": [
                "继续保持当前的护肤习惯",
                "建议每天饮水2000ml以上",
                "注意防晒"
            ]
        }
    }
}
```

---

## 7. 通知模块

### 7.1 获取通知列表

**接口地址**: `GET /api/miniprogram/notification/list`

**是否需要认证**: ✅ 是

**请求头**:

```
Authorization: Bearer <token>
```

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | integer | ❌ | 页码，默认1 |
| per_page | integer | ❌ | 每页数量，默认20 |
| is_read | boolean | ❌ | 是否已读（true/false/null） |

**请求示例**:

```
# 获取未读通知
GET /api/miniprogram/notification/list?is_read=false

# 获取所有通知
GET /api/miniprogram/notification/list?page=1&per_page=20
```

**响应示例**:

```json
{
    "success": true,
    "message": "查询成功",
    "data": {
        "items": [
            {
                "notification_id": 1,
                "title": "设备离线提醒",
                "content": "您的设备 DEV_001 已离线超过2小时",
                "type": "device_alert",
                "is_read": false,
                "create_time": "2026-04-29T10:00:00"
            },
            {
                "notification_id": 2,
                "title": "健康报告生成",
                "content": "您的每日健康报告已生成",
                "type": "report_ready",
                "is_read": true,
                "create_time": "2026-04-29T02:00:00"
            }
        ],
        "total": 15,
        "page": 1,
        "per_page": 20,
        "pages": 1
    }
}
```

---

### 7.2 标记通知为已读

**接口地址**: `PUT /api/miniprogram/notification/read/{notification_id}`

**是否需要认证**: ✅ 是

**请求头**:

```
Authorization: Bearer <token>
```

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| notification_id | integer | ✅ | 通知ID |

**请求示例**:

```
PUT /api/miniprogram/notification/read/1
```

**响应示例**:

```json
{
    "success": true,
    "message": "标记成功"
}
```

---

## 8. 错误码说明

### 8.1 HTTP状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（Token无效或过期） |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 8.2 业务错误码

| 错误信息 | 说明 | 解决方案 |
|----------|------|----------|
| 缺少认证token | 请求头未携带Token | 检查Authorization header |
| Token已过期 | Token超过有效期 | 重新登录获取新Token |
| 无效的Token | Token格式错误或签名验证失败 | 检查Token是否正确 |
| 用户不存在 | 用户ID对应的用户不存在 | 检查用户是否已注册 |
| 用户名已存在 | 注册时用户名重复 | 更换用户名 |
| 设备不存在 | 设备ID无效 | 检查设备ID是否正确 |
| 设备未绑定 | 尝试访问未绑定的设备 | 先绑定设备 |

---

## 9. Postman集合

### 9.1 导入方式

1. 打开Postman
2. 点击左上角 `Import`
3. 选择 `Link` 标签
4. 输入以下URL（待上传到GitHub后提供）

或者手动创建Collection，按照上述接口文档添加请求。

### 9.2 环境变量配置

在Postman中设置环境变量：

```json
{
    "base_url": "http://47.103.108.47:5000",
    "token": ""
}
```

### 9.3 使用示例

**登录并保存Token**:

1. 发送登录请求
2. 在Tests标签中添加脚本自动保存Token：

```javascript
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    pm.environment.set("token", jsonData.data.token);
}
```

**其他请求自动携带Token**:

在Collection的Pre-request Script中添加：

```javascript
pm.request.headers.add({
    key: 'Authorization',
    value: 'Bearer ' + pm.environment.get('token')
});
```

---

## 10. 快速测试

### 10.1 cURL命令示例

#### 注册

```bash
curl -X POST http://47.103.108.47:5000/api/miniprogram/user/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "password": "123456",
    "phone": "13800138000",
    "nickname": "测试用户"
  }'
```

#### 登录

```bash
curl -X POST http://47.103.108.47:5000/api/miniprogram/user/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "password": "123456"
  }'
```

#### 获取个人信息（替换YOUR_TOKEN）

```bash
curl -X GET http://47.103.108.47:5000/api/miniprogram/user/profile \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 绑定设备

```bash
curl -X POST http://47.103.108.47:5000/api/miniprogram/device/bind \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "DEV_001",
    "device_name": "我的设备",
    "location": "家中"
  }'
```

#### 查询皮肤数据

```bash
curl -X GET "http://47.103.108.47:5000/api/miniprogram/data/skin?days=7&page=1&per_page=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 11. 开发建议

### 11.1 小程序端实现要点

1. **Token管理**
   - 登录成功后将Token存储在本地存储（wx.setStorageSync）
   - 每次请求前从本地读取Token并添加到请求头
   - 收到401错误时自动跳转登录页

2. **错误处理**
   - 统一封装网络请求函数
   - 显示友好的错误提示
   - 网络超时重试机制

3. **数据缓存**
   - 频繁访问的数据（如用户信息）可缓存
   - 设置合理的缓存过期时间
   - 下拉刷新时强制更新

4. **分页加载**
   - 列表数据采用分页加载
   - 上拉加载更多
   - 显示加载状态

### 11.2 代码示例（微信小程序）

```javascript
// utils/request.js
const BASE_URL = 'http://47.103.108.47:5000/api/miniprogram';

function request(options) {
    return new Promise((resolve, reject) => {
        const token = wx.getStorageSync('token');
        
        wx.request({
            url: BASE_URL + options.url,
            method: options.method || 'GET',
            header: {
                'Content-Type': 'application/json',
                'Authorization': token ? `Bearer ${token}` : ''
            },
            data: options.data || {},
            success(res) {
                if (res.statusCode === 200) {
                    if (res.data.success) {
                        resolve(res.data);
                    } else {
                        wx.showToast({
                            title: res.data.message,
                            icon: 'none'
                        });
                        reject(res.data);
                    }
                } else if (res.statusCode === 401) {
                    // Token过期，跳转登录
                    wx.removeStorageSync('token');
                    wx.redirectTo({
                        url: '/pages/login/login'
                    });
                } else {
                    wx.showToast({
                        title: '网络错误',
                        icon: 'none'
                    });
                    reject(res);
                }
            },
            fail(err) {
                wx.showToast({
                    title: '网络请求失败',
                    icon: 'none'
                });
                reject(err);
            }
        });
    });
}

module.exports = {
    request
};
```

```javascript
// pages/index/index.js
const { request } = require('../../utils/request');

Page({
    data: {
        skinData: [],
        page: 1,
        loading: false
    },

    onLoad() {
        this.loadSkinData();
    },

    async loadSkinData() {
        if (this.data.loading) return;
        
        this.setData({ loading: true });
        
        try {
            const res = await request({
                url: `/data/skin?days=7&page=${this.data.page}&per_page=10`,
                method: 'GET'
            });
            
            this.setData({
                skinData: [...this.data.skinData, ...res.data.items],
                page: this.data.page + 1,
                loading: false
            });
        } catch (err) {
            this.setData({ loading: false });
        }
    },

    onReachBottom() {
        this.loadSkinData();
    }
});
```

---

## 12. 联系与支持

如有问题，请联系开发团队或查看项目文档。

**项目地址**: https://github.com/MOONFISH2233/software-design-project

**服务器地址**: http://47.103.108.47:5000

---

**文档版本**: v1.0  
**最后更新**: 2026-04-29  
**维护者**: 卓越工程师学院项目开发团队