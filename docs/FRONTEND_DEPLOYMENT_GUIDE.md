# 前端页面部署指南

> **版本**: v1.0  
> **最后更新**: 2026-04-29  
> **作者**: 卓越工程师学院项目开发团队

---

## 📋 目录

- [1. 概述](#1-概述)
- [2. 技术栈](#2-技术栈)
- [3. 功能特性](#3-功能特性)
- [4. 部署方案](#4-部署方案)
- [5. 快速开始](#5-快速开始)
- [6. 常见问题](#6-常见问题)

---

## 1. 概述

本项目为**皮肤健康监测系统**开发了一个现代化的Web前端页面，用于展示和测试API接口。前端采用原生HTML5 + Bootstrap 5构建，无需复杂的构建工具，可直接在浏览器中运行。

### 项目特点

✅ **零依赖**: 无需Node.js/npm，直接打开HTML即可运行  
✅ **响应式设计**: 支持PC、平板、手机访问  
✅ **完整功能**: 包含登录、设备管理、数据查询等核心功能  
✅ **美观界面**: 使用Bootstrap 5 + Font Awesome图标  
✅ **数据可视化**: 集成Chart.js图表库  

---

## 2. 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| HTML5 | - | 页面结构 |
| CSS3 | - | 样式设计 |
| JavaScript | ES6+ | 业务逻辑 |
| Bootstrap | 5.3.0 | UI框架 |
| Font Awesome | 6.4.0 | 图标库 |
| Chart.js | 4.4.0 | 数据图表 |

---

## 3. 功能特性

### 3.1 认证模块

- ✅ 用户注册
- ✅ 用户登录
- ✅ JWT Token自动管理
- ✅ Token过期自动跳转登录

### 3.2 仪表板

- ✅ 统计卡片（设备数、在线数、数据量、通知数）
- ✅ 快捷操作按钮
- ✅ 最近7天数据趋势图
- ✅ 最新动态列表

### 3.3 设备管理

- ✅ 设备列表展示
- ✅ 绑定新设备
- ✅ 查看设备状态详情
- ✅ 设备状态实时监控

### 3.4 数据查询

- ✅ 皮肤数据查询（分页、时间范围筛选）
- ⏳ 环境数据查询（开发中）
- ⏳ 统计分析（开发中）

### 3.5 其他功能

- ⏳ 健康报告（开发中）
- ⏳ 通知中心（开发中）

---

## 4. 部署方案

### 方案1: Flask静态文件服务（推荐用于开发测试）⭐⭐⭐⭐

**优点**: 
- 简单快速
- 与后端API同源，无跨域问题
- 适合开发和演示

**缺点**:
- 性能较低
- 不适合生产环境

**部署步骤**:

1. **确保Flask服务已启动**

```bash
ssh root@47.103.108.47
cd /root/course-project/data-server

# 检查Flask是否运行
ps aux | grep flask | grep -v grep
```

2. **上传前端文件到服务器**

```bash
# 从本地上传
scp "d:\学习\软件设计\data-server\static\index.html" root@47.103.108.47:/root/course-project/data-server/static/
```

3. **配置Flask提供静态文件**

编辑 `app_simple.py`，确保有静态文件路由：

```python
from flask import Flask, send_from_directory

app = Flask(__name__, static_folder='static', static_url_path='/static')

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')
```

4. **重启Flask服务**

```bash
pkill -f "python3.*app_simple" || true
sleep 2
nohup python3 app_simple.py > /tmp/flask.log 2>&1 &
```

5. **访问前端页面**

```
http://47.103.108.47:5000/
```

---

### 方案2: Nginx独立部署（推荐用于生产环境）⭐⭐⭐⭐⭐

**优点**:
- 高性能
- 支持HTTPS
- 可配置缓存
- 专业Web服务器

**缺点**:
- 需要额外安装Nginx
- 需要配置跨域（CORS）

**部署步骤**:

1. **安装Nginx**

```bash
ssh root@47.103.108.47

# CentOS/RHEL
yum install -y nginx

# Ubuntu/Debian
apt-get install -y nginx
```

2. **创建网站目录**

```bash
mkdir -p /var/www/skin-monitor
cp /root/course-project/data-server/static/index.html /var/www/skin-monitor/
```

3. **配置Nginx**

```bash
cat > /etc/nginx/conf.d/skin-monitor.conf << 'EOF'
server {
    listen 80;
    server_name skin-monitor.example.com;  # 替换为你的域名
    
    root /var/www/skin-monitor;
    index index.html;
    
    # 前端页面
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API代理（解决跨域）
    location /api/ {
        proxy_pass http://localhost:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS配置
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods 'GET, POST, PUT, DELETE, OPTIONS';
        add_header Access-Control-Allow-Headers 'Content-Type, Authorization';
        
        if ($request_method = 'OPTIONS') {
            return 204;
        }
    }
}
EOF
```

4. **重启Nginx**

```bash
systemctl restart nginx
systemctl enable nginx
```

5. **访问前端页面**

```
http://47.103.108.47/
或
http://skin-monitor.example.com/
```

---

### 方案3: GitHub Pages（适合演示分享）⭐⭐⭐

**优点**:
- 免费托管
- 易于分享
- 自动HTTPS

**缺点**:
- API需要支持CORS
- 无法自定义域名（免费版）

**部署步骤**:

1. **修改API基础URL**

编辑 `index.html`，将API地址改为完整URL：

```javascript
const API_BASE_URL = 'http://47.103.108.47:5000/api/miniprogram';
```

2. **确保Flask支持CORS**

在Flask中添加CORS支持：

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许所有跨域请求
```

3. **推送到GitHub**

```bash
cd "d:\学习\软件设计"
git add data-server/static/index.html
git commit -m "feat: 添加前端页面"
git push origin main
```

4. **启用GitHub Pages**

- 进入GitHub仓库设置
- 找到 "Pages" 选项
- 选择分支和文件夹（如 `main` / `/data-server/static`）
- 保存后等待部署完成

5. **访问页面**

```
https://MOONFISH2233.github.io/software-design-project/
```

---

## 5. 快速开始

### 5.1 本地测试（最简单）

1. **直接在浏览器打开HTML文件**

```
双击打开: d:\学习\软件设计\data-server\static\index.html
```

⚠️ **注意**: 由于浏览器的安全策略，直接打开可能无法发送API请求。建议使用本地服务器。

2. **使用Python简易服务器**

```bash
cd "d:\学习\软件设计\data-server\static"
python -m http.server 8080
```

然后访问: `http://localhost:8080`

---

### 5.2 服务器部署（推荐）

**一键部署脚本**:

```bash
#!/bin/bash
# deploy_frontend.sh

echo "========================================"
echo "  前端页面部署脚本"
echo "========================================"

# 1. 上传文件
echo "1. 上传前端文件..."
scp "d:\学习\软件设计\data-server\static\index.html" root@47.103.108.47:/root/course-project/data-server/static/

# 2. SSH到服务器执行后续操作
ssh root@47.103.108.47 << 'SSH_EOF'
cd /root/course-project/data-server

# 3. 备份旧文件
if [ -f static/index.html.bak ]; then
    rm static/index.html.bak
fi
cp static/index.html static/index.html.bak

# 4. 重启Flask服务
echo "2. 重启Flask服务..."
pkill -f "python3.*app_simple" || true
sleep 2
nohup python3 app_simple.py > /tmp/flask.log 2>&1 &
sleep 5

# 5. 检查服务状态
echo "3. 检查服务状态..."
if ps aux | grep "[p]ython3.*app_simple" > /dev/null; then
    echo "✅ Flask服务运行正常"
else
    echo "❌ Flask服务启动失败"
    tail -20 /tmp/flask.log
    exit 1
fi

# 6. 测试访问
echo "4. 测试访问..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 前端页面可访问"
else
    echo "❌ 访问失败，HTTP状态码: $HTTP_CODE"
    exit 1
fi

echo ""
echo "========================================"
echo "  部署完成！"
echo "  访问地址: http://47.103.108.47:5000/"
echo "========================================"
SSH_EOF
```

**使用方法**:

```bash
# Windows PowerShell
.\deploy_frontend.ps1

# Linux/Mac
chmod +x deploy_frontend.sh
./deploy_frontend.sh
```

---

## 6. 常见问题

### Q1: 页面显示空白或无法加载

**原因**: API请求失败或CORS跨域问题

**解决方案**:
1. 打开浏览器开发者工具（F12）
2. 查看Console标签的错误信息
3. 检查Network标签的API请求状态
4. 如果是CORS问题，参考方案2配置Nginx代理

---

### Q2: 登录后提示"网络错误"

**原因**: API地址配置错误或服务器未启动

**解决方案**:
1. 检查 `API_BASE_URL` 是否正确
2. 确认Flask服务正在运行: `ps aux | grep flask`
3. 测试API是否可访问: `curl http://47.103.108.47:5000/api/health`

---

### Q3: 图表不显示

**原因**: Chart.js库加载失败或数据格式错误

**解决方案**:
1. 检查网络连接，确保能访问CDN
2. 查看Console是否有JavaScript错误
3. 确认API返回的数据格式正确

---

### Q4: 移动端显示异常

**原因**: 响应式布局问题

**解决方案**:
1. 清除浏览器缓存
2. 检查viewport meta标签是否正确
3. 使用Chrome DevTools的设备模拟功能调试

---

### Q5: Token过期后无法自动跳转

**原因**: 401错误处理逻辑有问题

**解决方案**:
1. 检查API响应的状态码是否为401
2. 确认 `handleLogout()` 函数被正确调用
3. 查看Console是否有JavaScript错误

---

## 7. 开发建议

### 7.1 代码组织

当前采用单文件架构，适合小型项目。如果功能继续扩展，建议拆分为：

```
static/
├── index.html          # 主页面
├── css/
│   ├── style.css       # 自定义样式
│   └── responsive.css  # 响应式样式
├── js/
│   ├── app.js          # 主应用逻辑
│   ├── auth.js         # 认证模块
│   ├── devices.js      # 设备管理
│   ├── data.js         # 数据查询
│   └── utils.js        # 工具函数
└── assets/
    ├── images/         # 图片资源
    └── icons/          # 图标文件
```

### 7.2 性能优化

1. **启用Gzip压缩** (Nginx配置)
```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript;
```

2. **启用浏览器缓存**
```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|ico)$ {
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

3. **使用CDN加速**
- Bootstrap: https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/
- Font Awesome: https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/
- Chart.js: https://cdn.jsdelivr.net/npm/chart.js@4.4.0/

### 7.3 安全建议

1. **启用HTTPS**: 使用Let's Encrypt免费证书
2. **Content Security Policy**: 防止XSS攻击
3. **输入验证**: 前端和后端都要验证用户输入
4. **Token存储**: 考虑使用HttpOnly Cookie而非localStorage

---

## 8. 后续规划

### 短期（1-2周）

- [ ] 完成环境数据查询页面
- [ ] 完成统计分析页面（图表展示）
- [ ] 完成健康报告页面
- [ ] 完成通知中心页面
- [ ] 添加数据导出功能（CSV/Excel）

### 中期（1个月）

- [ ] 实现实时数据推送（WebSocket）
- [ ] 添加数据对比功能
- [ ] 实现自定义报表
- [ ] 添加用户偏好设置
- [ ] 多语言支持（中英文切换）

### 长期（3个月）

- [ ] 迁移到Vue.js/React框架
- [ ] 实现PWA（离线访问）
- [ ] 添加数据AI分析
- [ ] 社交分享功能
- [ ] 移动端App（uni-app打包）

---

## 9. 联系与支持

如有问题，请联系开发团队或查看项目文档。

**项目地址**: https://github.com/MOONFISH2233/software-design-project  
**服务器地址**: http://47.103.108.47:5000  
**前端演示**: http://47.103.108.47:5000/

---

**文档版本**: v1.0  
**最后更新**: 2026-04-29  
**维护者**: 卓越工程师学院项目开发团队