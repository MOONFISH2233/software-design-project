# 智能皮肤健康监测系统

基于云端部署的智能皮肤检测数据监控与分析平台

## 项目概述

本项目是一个完整的智能皮肤健康监测系统，包含后端服务、微信小程序和Web管理后台三个部分。系统部署在阿里云ECS服务器上，支持高并发数据采集、存储、分析和可视化。

## 技术架构

- **后端**：Python + Flask + gunicorn + gevent
- **数据库**：MySQL 8.0 (Docker容器)
- **前端**：React + Vite + TailwindCSS
- **小程序**：微信小程序
- **服务器**：阿里云ECS (47.103.108.47)
- **部署方式**：Docker容器化 + systemd服务管理

## 项目结构

```
├── data-server/          # Flask后端服务
│   ├── app.py           # 主应用入口
│   ├── routes/          # API路由
│   ├── scripts/         # 部署和运维脚本
│   ├── config/          # 配置文件
│   └── static/          # 静态文件
│
├── frontend-react/       # React Web管理后台
│   ├── src/
│   │   ├── pages/       # 页面组件
│   │   ├── components/ # 公共组件
│   │   └── api/         # API封装
│   └── package.json
│
├── miniprogram-3/        # 微信小程序
│   ├── pages/           # 小程序页面
│   └── utils/           # 工具函数
│
└── docs/                # 项目文档
    ├── ppt/             # 演示PPT
    ├── 系统架构图.drawio
    ├── 部署拓扑图.drawio
    └── 操作手册.txt
```

## 核心功能

### 1. 数据采集与处理
- 传感器数据实时接收（皮肤湿度、温度、油脂）
- 环境数据采集（温度、湿度、PM2.5、CO2）
- 数据加密存储（AES加密）
- 高并发支持（66+ QPS）

### 2. 用户管理
- 用户注册与登录（JWT认证）
- 用户资料管理
- 设备绑定与解绑
- 个人皮肤健康报告

### 3. 设备管理
- 设备注册与状态监控
- 设备位置管理（地域地图）
- 设备数据绑定（用户-设备关系）

### 4. 数据分析
- 皮肤健康趋势分析
- 环境因素影响分析
- 用户行为分析
- 数据可视化图表

## API接口

| 接口 | 方法 | 功能 |
|------|------|------|
| /api/auth/login | POST | 用户登录 |
| /api/receive | POST | 数据接收 |
| /api/sensor/skin | POST | 皮肤数据 |
| /api/device/status | POST | 设备状态 |
| /api/stats | GET | 统计数据 |
| /api/encrypt | POST | 数据加密 |
| /api/health | GET | 健康检查 |

## 部署信息

### 服务器信息
- **IP**: 47.103.108.47
- **系统**: Alibaba Cloud Linux 3.2104
- **配置**: 2核CPU / 2GB内存 / 40GB SSD

### 运行服务
| 服务 | 端口 | 状态 |
|------|------|------|
| Flask API | 5000 | 运行中 |
| Adminer | 8082 | 运行中 |
| MySQL | 3306 | 运行中 |

### 访问地址
- **API服务**: http://47.103.108.47:5000
- **健康检查**: http://47.103.108.47:5000/api/health
- **数据管理**: http://47.103.108.47:8082

## 性能指标

- **QPS**: 66+ requests/second
- **并发数**: 20+ concurrent threads
- **成功率**: 100%
- **平均响应**: 280-300ms

## 快速开始

### 后端部署
```bash
cd data-server
pip install -r requirements.txt
gunicorn -c config/gunicorn_config.py wsgi:app
```

### 前端部署
```bash
cd frontend-react
npm install
npm run dev
```

### 小程序开发
1. 使用微信开发者工具打开 miniprogram-3 目录
2. 配置服务器域名
3. 开始开发

## 数据库

- **sensor_project**: 传感器数据
- **software_design**: 用户和设备数据

### 主要数据表
- users: 用户表
- devices: 设备表
- user_device_bindings: 用户设备绑定表
- skin_sensor_data: 皮肤传感器数据
- environment_sensor_data: 环境传感器数据

## 运维管理

### 服务管理
```bash
systemctl status flask-data-server
systemctl restart flask-data-server
```

### 日志查看
```bash
tail -f /var/log/flask-access.log
tail -f /var/log/flask-error.log
```

### 数据库备份
```bash
docker exec mysql-server mysqldump -uroot -padmin sensor_project > backup.sql
```

## 文档

详细文档请参考 docs 目录：
- [系统架构图.drawio](docs/系统架构图.drawio)
- [部署拓扑图.drawio](docs/部署拓扑图.drawio)
- [操作手册.txt](docs/操作手册.txt)

## 版本信息

- **版本**: v1.0.0
- **发布日期**: 2026-06-21
- **分支**: final-delivery-v1.0

## 作者

软件系统架构技术课程项目

## 许可证

MIT License
