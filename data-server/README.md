# Sensor Data Server - 高性能传感器数据服务平台

[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![Gunicorn](https://img.shields.io/badge/Gunicorn-Production-orange.svg)](https://gunicorn.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个**生产级**的传感器数据采集与处理平台，支持高并发、安全认证和实时数据处理。

---

## 🎯 项目概述

本项目是一个完整的传感器数据服务系统，采用**微服务架构**设计，包含：

- 🔐 **安全 API 服务** - JWT/API Key 认证 + AES-256 加密
- 📨 **消息队列处理** - Redis Stream 异步解耦
- 📊 **数据存储管理** - 结构化 JSON 文件存储
- 🧪 **压力测试套件** - 100% 成功率验证
- 🚀 **生产级部署** - Gunicorn + Systemd 自动管理

### 核心应用场景

- 💆 **皮肤传感器监测** - 水分、油亮度实时采集
- 🌡️ **环境传感器监测** - 温度、湿度、光照强度
- 🔒 **安全数据传输** - 端到端加密保护
- 📈 **高并发数据处理** - 支持 170+ QPS

---

## ✨ 核心特性

### 🔐 安全特性

- ✅ **JWT Token 认证** - 基于用户名/密码的动态令牌
- ✅ **API Key 认证** - 静态密钥快速访问
- ✅ **AES-256 加密** - 请求体端到端加密传输
- ✅ **速率限制** - Flask-Limiter 防止滥用
- ✅ **输入验证** - 严格的数据格式校验

### 🚀 性能特性

- ✅ **Gunicorn + Gevent** - 异步 Worker 高并发处理
- ✅ **Redis 消息队列** - 解耦接收、验证、写入流程
- ✅ **异步日志系统** - 独立线程零阻塞
- ✅ **智能日志采样** - 10% 采样率减少 I/O
- ✅ **慢请求检测** - >100ms 自动告警

### 📊 监控与维护

- ✅ **Systemd 服务管理** - 开机自启、故障自动重启
- ✅ **完整日志系统** - 结构化 JSON 日志便于分析
- ✅ **性能监控脚本** - 实时监控 CPU/内存/QPS
- ✅ **健康检查接口** - `/api/health` 快速诊断

---

## 📦 快速开始

### 前置要求

- Python 3.6+
- Redis 6.0+
- Linux 服务器（推荐 CentOS 7+/Ubuntu 18.04+）

### 安装依赖

```bash
cd data-server
pip install flask gunicorn gevent redis flask-limiter cryptography
```

### 启动 Redis

```bash
# 启动 Redis 服务
redis-server --daemonize yes

# 验证连接
redis-cli ping
# 应返回: PONG
```

### 方式一：开发模式（快速测试）

```bash
python app.py
```

服务将在 `http://localhost:5000` 启动。

### 方式二：生产模式（推荐）

```bash
# 使用 Gunicorn 启动（5个 Worker）
gunicorn -c config/gunicorn_config.py app:app

# 或使用 Systemd（开机自启）
sudo cp config/gunicorn-flask-data-server.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start gunicorn-flask-data-server
sudo systemctl enable gunicorn-flask-data-server
```

### 方式三：MQ 多模块模式

```bash
# 一键启动所有模块（接收器、验证器、写入器、模拟器）
python start_all_modules.py
```

---

## 🔧 API 接口

### 1. 健康检查

```bash
curl http://localhost:5000/api/health
```

响应:
```json
{
  "status": "healthy",
  "service": "Sensor Data Server v3.0",
  "timestamp": "2026-04-08T09:30:00",
  "features": ["JWT Auth", "API Key", "AES Encryption"]
}
```

### 2. 用户登录（获取 JWT Token）

```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user1", "password": "user123"}'
```

响应:
```json
{
  "status": "success",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600
}
```

### 3. 接收加密数据（JWT 认证）

```bash
curl -X POST http://localhost:5000/api/receive/encrypted \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "encrypted_data": "U2FsdGVkX1+...",
    "iv": "abc123...",
    "sensor_type": "skin"
  }'
```

响应:
```json
{
  "status": "success",
  "message": "加密数据接收成功",
  "filename": "data_20260408_093000_123456.json",
  "process_time_ms": 15.23
}
```

### 4. 接收数据（API Key 认证）

```bash
curl -X POST http://localhost:5000/api/receive/apikey \
  -H "X-API-Key: key_user1_001" \
  -H "Content-Type: application/json" \
  -d '{"sensor_type": "environment", "data": {...}}'
```

### 5. 查看统计信息

```bash
curl http://localhost:5000/api/stats
```

---

## 🧪 压力测试

### 运行完整测试套件

```bash
cd tests

# 测试 1: 普通模式（无认证）
python jmeter_test.py --url http://localhost:5000 --duration 60 --users 10 --type normal

# 测试 2: JWT 加密模式
python jmeter_test.py --url http://localhost:5000 --duration 60 --users 10 \
  --username user1 --password user123 --type encrypted

# 测试 3: API Key 模式
python jmeter_test.py --url http://localhost:5000 --duration 60 --users 10 \
  --apikey key_user1_001 --type apikey
```

### 测试结果（实际数据）

| 测试模式 | QPS | 成功率 | 平均响应时间 | P95 响应时间 |
|---------|-----|--------|-------------|-------------|
| NORMAL | **175.42** | **100%** | 37.10ms | 72.58ms |
| ENCRYPTED (JWT) | **170.77** | **100%** | 38.44ms | 74.06ms |
| APIKEY | **174.02** | **100%** | 37.53ms | 73.88ms |

**测试环境**: 阿里云 2核CPU / 1.8GB 内存  
**结论**: ✅ 完全满足小型企业应用需求（日活 1000-5000 用户）

---

## 📁 项目结构

```
data-server/
├── app.py                      # 🚀 Flask 主应用（路由、认证）
├── security_enhanced.py        # 🔐 安全模块（JWT、AES、API Key）
├── module_receiver.py          # 📦 MQ 接收模块
├── module_validator.py         # 🔍 MQ 验证模块
├── module_writer.py            # 💾 MQ 写入模块
├── module_logger.py            # 📝 MQ 日志模块
├── mq_utils.py                 # 🔧 MQ 工具函数
│
├── config/                     # ⚙️ 配置文件
│   ├── gunicorn_config.py      # Gunicorn 配置
│   ├── gunicorn-flask-data-server.service  # Systemd 服务
│   └── requirements.txt        # Python 依赖
│
├── docs/                       # 📚 文档资料
│   ├── WEEK5_TASK_COMPLETION_REPORT.md     # 第五周任务报告
│   ├── PRODUCTION_DEPLOYMENT_REPORT.md     # 生产部署报告
│   ├── PRESSURE_TEST_GUIDE.md              # 压力测试指南
│   └── DIRECTORY_STRUCTURE.md              # 目录结构说明
│
├── scripts/                    # 🛠️ 运维脚本
│   ├── deploy_production.sh    # 生产部署脚本
│   ├── monitor_performance.sh  # 性能监控面板
│   └── organize_project.py     # 项目整理脚本
│
├── tests/                      # 🧪 测试文件
│   ├── jmeter_test.py          # 压力测试工具
│   ├── acceptance_demo.py      # 验收演示脚本
│   └── verify_security.py      # 安全功能验证
│
├── examples/                   # 💡 示例代码
│   ├── simulator_mq.py         # MQ 版传感器模拟器
│   └── sample_data/            # 示例数据
│
├── security/                   # 🔒 安全配置
│   └── keys/                   # 加密密钥存储
│
├── data/                       # 📊 数据存储
│   ├── skin_sensor/            # 皮肤传感器数据
│   └── environment/            # 环境传感器数据
│
├── logs/                       # 📝 日志文件
│   ├── server_*.log            # 应用日志
│   └── error_*.log             # 错误日志
│
└── backups/                    # 💾 备份文件
    └── legacy_code/            # 历史代码备份
```

详细说明请参考 [docs/DIRECTORY_STRUCTURE.md](docs/DIRECTORY_STRUCTURE.md)

---

## 🚀 生产部署

### 一键部署脚本

```bash
# 在服务器上执行
cd /root/course-project/week5/data-server
chmod +x scripts/deploy_production.sh
bash scripts/deploy_production.sh
```

该脚本会自动：
1. 安装 Python 依赖（gunicorn、gevent）
2. 配置 Systemd 服务
3. 启动 Gunicorn 服务
4. 验证服务状态

### 监控服务状态

```bash
# 查看服务状态
systemctl status gunicorn-flask-data-server

# 查看实时日志
journalctl -u gunicorn-flask-data-server -f

# 运行性能监控面板
bash scripts/monitor_performance.sh
```

---

## 📊 性能指标

### 当前性能（2核/1.8GB 服务器）

| 指标 | 数值 | 评级 |
|------|------|------|
| **QPS** | 170-175 | ⭐⭐⭐⭐ |
| **成功率** | 100% | ⭐⭐⭐⭐⭐ |
| **平均响应时间** | 37-38ms | ⭐⭐⭐⭐⭐ |
| **P95 响应时间** | 72-74ms | ⭐⭐⭐⭐⭐ |
| **并发支持** | 20+ 用户 | ⭐⭐⭐⭐ |
| **资源占用** | CPU 45%, 内存 13% | ⭐⭐⭐⭐ |

### 优化潜力

如需更高性能，可考虑：
- 🔄 升级到 4核/4GB 服务器 → QPS 预计 300-400
- 🗄️ 添加 Redis 缓存层 → QPS 预计 500-800
- 🌐 Nginx 负载均衡（多实例）→ QPS 预计 1000+

详见 [docs/PRODUCTION_DEPLOYMENT_REPORT.md](docs/PRODUCTION_DEPLOYMENT_REPORT.md)

---

## 🛠️ 故障排查

### 常见问题

#### 1. 服务无法启动

```bash
# 检查端口占用
sudo lsof -i :5000

# 查看详细错误日志
journalctl -u gunicorn-flask-data-server -n 50
```

#### 2. Redis 连接失败

```bash
# 检查 Redis 状态
redis-cli ping

# 启动 Redis
redis-server --daemonize yes
```

#### 3. 压力测试失败

```bash
# 检查防火墙
sudo firewall-cmd --list-ports

# 开放 5000 端口
sudo firewall-cmd --add-port=5000/tcp --permanent
sudo firewall-cmd --reload
```

更多问题参考 [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

## 📝 更新日志

### v3.0 (2026-04-08) - 第五周任务完成版

**新增功能**:
- ✅ JWT Token 认证系统
- ✅ API Key 静态密钥认证
- ✅ AES-256 端到端加密
- ✅ Redis Stream 消息队列架构
- ✅ 多模块异步处理（接收/验证/写入）

**性能优化**:
- ✅ Gunicorn + Gevent 生产级部署
- ✅ 压力测试通过率 100%
- ✅ QPS 稳定在 170+

**文档完善**:
- ✅ 完整的部署文档
- ✅ 压力测试指南
- ✅ 故障排查手册

### v2.0 (2026-03-27) - 高性能优化版

- ✅ 异步日志系统
- ✅ 智能日志采样
- ✅ 慢请求检测

详见 [CHANGELOG.md](docs/CHANGELOG.md)

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 👨‍💻 技术支持

- 📧 邮箱: [your-email@example.com]
- 🐛 问题反馈: [GitHub Issues](https://github.com/your-repo/issues)
- 📖 详细文档: [docs/](docs/)

---

## 🎓 课程项目说明

本项目是《软件设计》课程第五周任务成果，主要学习目标：

1. ✅ 实现安全的 API 认证机制
2. ✅ 掌握数据加密传输技术
3. ✅ 理解高并发系统设计
4. ✅ 学习生产级部署实践
5. ✅ 完成压力测试与性能优化

指导教师: [教师姓名]  
完成时间: 2026年4月8日
