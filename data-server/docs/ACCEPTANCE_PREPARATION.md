# 第二阶段验收准备文档

## 验收目标

展示数据传输系统的完整功能，包括：
1. ✅ 数据传输加密和鉴权
2. ✅ 多机压力测试
3. ✅ 系统性能和稳定性

---

## 一、演示环境准备

### 1.1 服务器配置

**硬件要求:**
- CPU: 4 核心以上
- 内存：8GB 以上
- 网络：100Mbps 以上

**软件环境:**
- Python 3.8+
- Flask 2.0+
- Redis (可选，用于缓存)

### 1.2 启动服务器

```bash
cd d:\学习\软件设计\data-server

# 1. 启动 Redis (可选)
start_redis.bat

# 2. 启动数据服务器
python app.py
```

### 1.3 验证服务器运行

打开浏览器访问：
- 健康检查：http://localhost:5000/api/health
- 查看日志：http://localhost:5000/api/logs

---

## 二、功能演示脚本

### 演示 1: 用户认证（JWT Token）

**步骤:**
1. 打开 Postman 或命令行
2. 调用登录接口
3. 获取 Token
4. 使用 Token 访问受保护接口

**Postman 请求:**
```
POST http://localhost:5000/api/auth/login
Content-Type: application/json

{
  "username": "user1",
  "password": "user123"
}
```

**响应示例:**
```json
{
  "status": "success",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 24
}
```

**使用 Token:**
```
GET http://localhost:5000/api/user/list
Authorization: Bearer <token>
```

---

### 演示 2: 数据加密传输

**步骤:**
1. 准备明文数据
2. 调用加密接口
3. 发送加密数据到接收接口
4. 验证解密功能

**Postman 请求 1 - 加密:**
```
POST http://localhost:5000/api/encrypt
Content-Type: application/json

{
  "temperature": 25.5,
  "humidity": 60,
  "device_id": "sensor_001"
}
```

**响应:**
```json
{
  "status": "success",
  "encrypted_data": "gAAAAABh..."
}
```

**Postman 请求 2 - 发送加密数据:**
```
POST http://localhost:5000/api/receive/secure
Authorization: Bearer <token>
Content-Type: application/json

{
  "data": "gAAAAABh...",
  "encrypted": true
}
```

---

### 演示 3: API Key 认证

**步骤:**
1. 使用 JWT Token 生成 API Key
2. 使用 API Key 发送数据
3. 验证数据接收

**生成 API Key:**
```
POST http://localhost:5000/api/auth/apikey
Authorization: Bearer <token>
```

**使用 API Key 发送数据:**
```
POST http://localhost:5000/api/receive/apikey
X-API-Key: key_user1_001
Content-Type: application/json

{
  "temperature": 26.5,
  "humidity": 65
}
```

---

### 演示 4: 实时压力测试

**现场演示:**
1. 启动 3 台电脑（或 3 个终端）
2. 同时运行压力测试脚本
3. 实时监控服务器状态
4. 查看测试结果报告

**启动命令（3 个终端）:**

终端 1:
```bash
python jmeter_test.py --url http://localhost:5000 --duration 60 --users 10 --username user1 --password user123 --type encrypted
```

终端 2:
```bash
python jmeter_test.py --url http://localhost:5000 --duration 60 --users 10 --username user2 --password user123 --type encrypted
```

终端 3:
```bash
python jmeter_test.py --url http://localhost:5000 --duration 60 --users 10 --username user3 --password user123 --type encrypted
```

---

## 三、性能指标展示

### 3.1 准备测试数据

运行完整测试套件：
```bash
# 运行所有测试模式
.\run_all_tests.bat
```

### 3.2 生成测试报告

```bash
# 生成 HTML 报告
python generate_report.py
```

### 3.3 关键指标

准备以下数据用于展示：

| 指标 | 普通模式 | JWT 认证 | 加密模式 | API Key |
|------|----------|----------|----------|---------|
| QPS | ___ | ___ | ___ | ___ |
| 平均响应时间 | ___ | ___ | ___ | ___ |
| 成功率 | ___ | ___ | ___ | ___ |
| 95 百分位响应时间 | ___ | ___ | ___ | ___ |

---

## 四、代码和架构说明

### 4.1 系统架构图

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  客户端     │─────▶│  数据服务器  │─────▶│  文件系统   │
│  (Web/App)  │      │  (Flask)     │      │  (JSON)     │
└─────────────┘      └──────────────┘      └─────────────┘
       │                    │
       │                    │
       ▼                    ▼
┌─────────────┐      ┌──────────────┐
│  认证服务   │      │  加密服务    │
│  (JWT/API)  │      │  (AES-256)  │
└─────────────┘      └──────────────┘
```

### 4.2 核心模块

1. **认证模块** (`app.py`)
   - JWT Token 生成和验证
   - API Key 管理
   - 用户管理系统

2. **加密模块** (`SecurityManager` 类)
   - AES-256 加密/解密
   - 密钥管理
   - 安全数据存储

3. **数据接收模块**
   - 多模式数据接收
   - 并发处理
   - 异步日志

4. **压力测试模块** (`jmeter_test.py`)
   - 多线程并发
   - 结果统计
   - 报告生成

---

## 五、验收演示流程

### 5.1 演示大纲（45 分钟）

**第一部分：系统介绍（5 分钟）**
- 项目背景
- 技术架构
- 功能特性

**第二部分：功能演示（15 分钟）**
1. 用户注册和登录
2. JWT Token 认证
3. 数据加密和解密
4. API Key 生成和使用
5. 安全数据接收

**第三部分：压力测试演示（15 分钟）**
1. 单机测试（10 并发）
2. 三机并发测试（30 并发）
3. 实时性能监控
4. 测试结果分析

**第四部分：代码讲解（5 分钟）**
- 核心代码结构
- 安全实现细节
- 性能优化措施

**第五部分：问答环节（5 分钟）**

---

## 六、验收材料清单

### 6.1 必需材料

- [ ] 服务器运行正常
- [ ] 测试脚本准备就绪
- [ ] 测试数据准备完成
- [ ] Postman 集合导出
- [ ] 测试报告生成

### 6.2 文档材料

- [ ] API 文档（`API 文档.md`）
- [ ] 压力测试指南（`PRESSURE_TEST_GUIDE.md`）
- [ ] 快速开始指南（`快速开始.md`）
- [ ] 最佳实践文档（`BEST_PRACTICES.md`）

### 6.3 代码材料

- [ ] `app.py` - 主应用
- [ ] `jmeter_test.py` - 压力测试
- [ ] `security/` - 安全配置目录
- [ ] `logs/` - 日志目录
- [ ] `data/` - 数据目录

---

## 七、演示检查清单

### 7.1 演示前检查

- [ ] 服务器启动成功
- [ ] 默认用户存在（admin, user1, user2, user3）
- [ ] 加密密钥已生成
- [ ] API Keys 已创建
- [ ] 测试脚本可运行
- [ ] 网络连接正常

### 7.2 演示环境检查

- [ ] 投影仪/屏幕共享正常
- [ ] 音频正常（如需讲解）
- [ ] 网络稳定
- [ ] 备用电源准备

### 7.3 应急预案

- [ ] 录屏软件准备
- [ ] 备用服务器准备
- [ ] 离线演示材料准备
- [ ] 网络故障应对方案

---

## 八、常见问题预演

### Q1: 为什么选择 JWT 而不是 Session？
**答**: 
- JWT 无状态，更适合分布式系统
- 支持跨域认证
- 性能更好，无需服务器存储 session
- 天然支持移动端

### Q2: AES 加密的安全性如何保证？
**答**:
- 使用 AES-256 位加密
- 密钥本地安全存储
- 每次加密使用不同的 nonce
- 符合工业标准

### Q3: 系统如何扩展？
**答**:
- 水平扩展：使用 Nginx 负载均衡
- 数据库：可替换为 MongoDB/PostgreSQL
- 缓存：集成 Redis 提升性能
- 消息队列：使用 RabbitMQ/Kafka

### Q4: 压力测试结果如何解读？
**答**:
- QPS 反映系统吞吐能力
- 响应时间反映用户体验
- 成功率反映系统稳定性
- 95 百分位反映长尾延迟

---

## 九、验收成功标准

### 9.1 功能完整性
- ✅ 所有认证方式正常工作
- ✅ 加密解密功能正常
- ✅ 数据接收功能正常
- ✅ 压力测试工具可用

### 9.2 性能指标
- ✅ QPS > 500
- ✅ 平均响应时间 < 200ms（加密模式）
- ✅ 成功率 > 99%
- ✅ 支持 30+ 并发用户

### 9.3 文档完整性
- ✅ API 文档完整
- ✅ 测试报告完整
- ✅ 使用指南清晰
- ✅ 代码注释充分

---

## 十、后续优化方向

### 10.1 短期优化
1. 添加 Redis 缓存层
2. 实现数据库持久化
3. 添加监控告警系统
4. 完善错误处理

### 10.2 长期规划
1. 微服务架构改造
2. 容器化部署（Docker）
3. CI/CD 流水线
4. 自动化测试覆盖

---

## 联系方式

如有问题，请提前联系：
- 技术支持：查看项目文档
- 演示协调：提前 1 天测试环境

---

**祝验收顺利！** 🎉
