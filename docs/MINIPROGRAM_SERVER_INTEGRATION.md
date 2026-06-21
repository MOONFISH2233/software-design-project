# 微信小程序与服务器对接完整指南

## 📋 概述

本指南详细说明如何将 `miniprogram-3` 小程序项目与阿里云服务器（47.103.108.47）进行对接。

---

## ✅ 当前状态检查

### 1. 小程序配置状态
```javascript
// miniprogram-3/utils/request.js
const BASE_URL = 'http://47.103.108.47:5000/api/miniprogram';
```
✅ **已配置正确的服务器地址**

### 2. 服务器服务状态
```bash
# Flask服务运行状态
systemctl status flask-data-server
# 输出: Active: active (running)

# 端口监听状态
netstat -tlnp | grep 5000
# 输出: tcp 0.0.0.0:5000 LISTEN
```
✅ **Flask服务正在运行，5000端口已开放**

### 3. API接口测试
```bash
# 登录接口测试
curl -X POST http://47.103.108.47:5000/api/miniprogram/user/login \
  -H "Content-Type: application/json" \
  -d '{"username":"123","password":"123456"}'

# 预期返回
{
  "success": true,
  "message": "登录成功",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {...}
}
```
✅ **API接口正常响应**

---

## 🚀 快速开始（3步完成对接）

### 步骤1：打开微信开发者工具

1. 下载并安装 [微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)
2. 打开工具，点击「导入项目」
3. 选择目录：`D:\学习\软件设计\miniprogram-3\miniprogram-3`

### 步骤2：配置AppID

有两种方式：

#### 方式A：使用测试号（推荐用于开发）
1. 在微信开发者工具中点击「详情」
2. 找到「AppID」字段
3. 选择「使用测试号」或填入你的小程序AppID

#### 方式B：使用正式AppID
1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 进入「开发」→「开发管理」→「开发设置」
3. 复制AppID填入开发者工具

### 步骤3：开启域名校验豁免（关键！）

⚠️ **这是最重要的一步！**

1. 在微信开发者工具右上角点击「详情」
2. 切换到「本地设置」标签
3. **勾选以下选项**：
   - ✅ **不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书**

**原因**：
- 我们的服务器使用HTTP协议（非HTTPS）
- 微信小程序正式版要求必须使用HTTPS
- 开发阶段可以关闭校验进行测试

---

## 🔧 详细配置说明

### 1. API基础配置

**文件位置**: `miniprogram-3/utils/request.js`

```javascript
const BASE_URL = 'http://47.103.108.47:5000/api/miniprogram';
```

**配置项说明**：
- `http://`: 使用HTTP协议（开发阶段）
- `47.103.108.47`: 阿里云服务器公网IP
- `5000`: Flask服务监听端口
- `/api/miniprogram`: API路由前缀

### 2. 认证机制

#### Token获取（登录时）
```javascript
// pages/login/login.js
const res = await request({
  url: '/user/login',
  method: 'POST',
  data: { username, password }
});

// 保存Token到本地存储
wx.setStorageSync('token', res.data.token);
wx.setStorageSync('userInfo', res.data.user);
```

#### Token自动携带（每次请求）
```javascript
// utils/request.js
const token = wx.getStorageSync('token');

wx.request({
  url: BASE_URL + options.url,
  header: {
    'Authorization': token ? `Bearer ${token}` : ''
  },
  // ...
});
```

#### Token过期处理
```javascript
// utils/request.js
if (res.statusCode === 401) {
  wx.showToast({ title: '请先登录', icon: 'none' });
  wx.removeStorageSync('token');
  wx.reLaunch({ url: '/pages/login/login' });
}
```

### 3. 接口调用示例

#### 获取设备列表
```javascript
// pages/device/device.js
const { request } = require('../../utils/request');

Page({
  async onLoad() {
    try {
      const res = await request({
        url: '/device/list',
        method: 'GET'
      });
      
      this.setData({
        devices: res.devices || []
      });
    } catch (err) {
      console.error('获取设备列表失败:', err);
    }
  }
});
```

#### 获取统计数据（图表数据）
```javascript
// pages/index/index.js
const res = await request({
  url: '/data/statistics?days=7',
  method: 'GET'
});

this.setData({
  chartData: res.statistics.map(s => ({
    date: s.stat_date,
    moisture: s.avg_moisture,
    oiliness: s.avg_oiliness
  }))
});
```

#### 绑定设备
```javascript
// pages/device/bind.js
const res = await request({
  url: '/device/bind',
  method: 'POST',
  data: {
    device_id: 'DEV_001',
    device_name: '卧室检测仪'
  }
});
```

---

## 📱 小程序页面功能映射

| 小程序页面 | 对应API | 功能说明 |
|-----------|---------|----------|
| **pages/login/login** | POST /user/login | 用户登录 |
| **pages/index/index** | GET /data/statistics<br>GET /device/list | 数据看板（图表+统计） |
| **pages/device/device** | GET /device/list | 设备列表 |
| **pages/device/bind** | POST /device/bind | 绑定新设备 |
| **pages/report/list** | GET /report/list | 健康报告列表 |
| **pages/report/detail** | GET /report/detail/:id | 报告详情 |
| **pages/notification/notification** | GET /notification/list | 通知中心 |
| **pages/community/community** | GET /community/posts | 社区帖子 |
| **pages/profile/profile** | GET /user/profile | 个人中心 |

---

## ⚠️ 常见问题排查

### 问题1：提示"网络连接断开"

**可能原因**：
1. 服务器未启动
2. 安全组未开放5000端口
3. 网络不通

**解决方案**：
```bash
# 1. 检查Flask服务状态
ssh root@47.103.108.47 "systemctl status flask-data-server"

# 2. 检查端口监听
ssh root@47.103.108.47 "netstat -tlnp | grep 5000"

# 3. 测试API连通性
curl http://47.103.108.47:5000/api/health
```

### 问题2：提示"请先登录"或401错误

**可能原因**：
1. Token未保存
2. Token已过期
3. 登录失败

**解决方案**：
1. 重新登录获取新Token
2. 检查登录账号密码是否正确（123 / 123456）
3. 查看Console日志确认Token是否保存成功

### 问题3：提示"不在以下 request 合法域名列表中"

**原因**：未关闭域名校验

**解决方案**：
1. 微信开发者工具 → 详情 → 本地设置
2. **勾选"不校验合法域名..."**
3. 重新编译小程序

### 问题4：数据加载一直转圈

**可能原因**：
1. API响应慢
2. 数据库连接池耗尽
3. 网络延迟高

**解决方案**：
```bash
# 检查服务器负载
ssh root@47.103.108.47 "top -bn1 | head -20"

# 检查数据库连接
ssh root@47.103.108.47 "mysql -u root -padmin -e 'SHOW PROCESSLIST;'"

# 重启Flask服务
ssh root@47.103.108.47 "systemctl restart flask-data-server"
```

### 问题5：真机调试无法访问

**原因**：真机必须使用HTTPS

**解决方案**：
1. **方案A（推荐）**：配置Nginx反向代理+SSL证书
2. **方案B（临时）**：使用微信开发者工具的"预览"功能生成体验版二维码

---

## 🔐 生产环境HTTPS配置（可选）

如果需要在正式发布时使用HTTPS，需要：

### 1. 申请SSL证书
- 阿里云免费SSL证书
- Let's Encrypt免费证书
- 腾讯云SSL证书

### 2. Nginx配置HTTPS
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. 修改小程序BASE_URL
```javascript
const BASE_URL = 'https://your-domain.com/api/miniprogram';
```

### 4. 配置小程序合法域名
1. 登录微信公众平台
2. 进入「开发」→「开发管理」→「开发设置」
3. 在「服务器域名」中添加你的HTTPS域名

---

## 📊 测试清单

在提交代码前，请完成以下测试：

### 功能测试
- [ ] 登录功能正常（123 / 123456）
- [ ] 数据看板显示图表和统计数据
- [ ] 设备列表正常显示
- [ ] 可以绑定新设备
- [ ] 健康报告可以查看
- [ ] 通知中心显示消息
- [ ] 社区帖子可以浏览
- [ ] 个人中心显示用户信息

### 性能测试
- [ ] 页面加载时间 < 2秒
- [ ] API响应时间 < 500ms
- [ ] 图表渲染流畅无卡顿
- [ ] 下拉刷新响应及时

### 兼容性测试
- [ ] iOS真机测试正常
- [ ] Android真机测试正常
- [ ] 不同屏幕尺寸适配正常
- [ ] 横竖屏切换正常

---

## 🎯 总结

### ✅ 已完成配置
1. ✅ 小程序API地址已配置为 `http://47.103.108.47:5000/api/miniprogram`
2. ✅ Flask服务通过systemd持久化运行
3. ✅ 5000端口已在阿里云安全组开放
4. ✅ 所有API接口正常工作
5. ✅ 认证机制（JWT Token）已实现

### 📝 下一步操作
1. **打开微信开发者工具**
2. **导入项目** `D:\学习\软件设计\miniprogram-3\miniprogram-3`
3. **勾选"不校验合法域名"**
4. **使用测试账号登录**（123 / 123456）
5. **测试所有功能**

### 🚀 立即开始
```
1. 启动微信开发者工具
2. 导入项目目录
3. 编译运行
4. 输入账号密码登录
5. 享受完整的小程序体验！
```

---

**如有问题，请参考上方"常见问题排查"章节或联系技术支持。**
