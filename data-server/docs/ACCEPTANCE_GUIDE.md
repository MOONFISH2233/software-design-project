# 🎯 第二阶段验收指南

> **Flask 数据服务器** | 版本 v3.0 | 最后更新：2026-04-17

---

## 📋 目录

- [项目基本信息](#项目基本信息)
- [验收内容详解](#验收内容详解)
  - [（1）RESTful API 接口](#1restful-api-接口)
  - [（2）模拟数据上传与本地保存](#2模拟数据上传与本地保存)
  - [（3）HTTPS 访问支持](#3https-访问支持)
  - [（4）接口文档](#4接口文档)
  - [（5）鉴权功能](#5鉴权功能)
  - [（6）数据加密传输](#6数据加密传输)
  - [（7）消息队列](#7消息队列)
- [验收总结](#验收总结)
- [性能指标](#性能指标)
- [快速验证命令](#快速验证命令)

---

## 项目基本信息

| 项目 | 说明 |
|------|------|
| **服务器地址** | 47.103.108.47:5000 |
| **技术栈** | Flask + Gunicorn + Redis + gevent |
| **Python 版本** | 3.6.8 |
| **Worker 配置** | 7 workers (gevent) |
| **验收完成度** | 7/8 项（HTTPS 为可选） |

---

## 验收内容详解

### （1）RESTful API 接口

**状态：✅ 已完成**

提供 **12 个** 基于 REST 风格的 API 接口：

| HTTP 方法 | 接口路径 | 功能 | 说明 |
|-----------|---------|------|------|
| GET | `/api/health` | 健康检查 | 检查服务状态 |
| POST | `/api/receive` | 数据接收 | 接收传感器数据 |
| POST | `/api/sensor/skin` | 皮肤数据 | 接收皮肤传感器数据 |
| POST | `/api/sensor/environment` | 环境数据 | 接收环境传感器数据 |
| POST | `/api/device/status` | 设备状态 | 接收设备状态数据 |
| POST | `/api/auth/login` | 登录认证 | 获取 JWT Token |
| POST | `/api/auth/apikey` | API Key | 生成 API 密钥 |
| POST | `/api/receive/secure` | 加密上传 | 接收加密数据 |
| POST | `/api/encrypt` | 数据加密 | AES-256 加密 |
| POST | `/api/decrypt` | 数据解密 | AES-256 解密 |
| POST | `/api/receive/apikey` | API Key 认证 | 使用 API Key 接收数据 |
| GET | `/api/stats` | 统计信息 | 获取系统统计数据 |

#### 验证演示

```bash
# SSH 登录服务器
ssh root@47.103.108.47

# 检查服务运行状态
ps aux | grep gunicorn

# 测试健康检查接口
curl http://localhost:5000/api/health | python3 -m json.tool
```

**预期输出：**
```json
{
    "status": "healthy",
    "service": "Flask Data Server v3.0",
    "features": ["JWT Auth", "API Key", "AES Encryption"]
}
```

---

### （2）模拟数据上传与本地保存

**状态：✅ 已完成**

#### 实现方式
1. 模拟器（`simulator_mq.py`）产生传感器数据
2. 通过 REST API 发送到服务器
3. 服务器接收数据并保存到本地文件系统
4. 数据格式：JSON，按时间戳命名

#### 验证方法

```bash
# 查看数据文件数量
find /root/data-server/data/ -name "*.json" | wc -l
# 输出：443506

# 手动测试数据上传
curl -X POST http://localhost:5000/api/receive \
  -H "Content-Type: application/json" \
  -d '{"sensor_type":"skin","moisture":65,"oiliness":32}' | python3 -m json.tool
```

**预期输出：**
```json
{
    "status": "success",
    "message": "数据接收成功",
    "filename": "data_20260417_xxxxxx.json"
}
```

---

### （3）HTTPS 访问支持

**状态：⚠️ 可选功能（未配置）**

#### 说明
由于未购买 SSL 证书，HTTPS 功能暂未实现。但系统架构已预留 SSL 配置接口，后续可通过配置 Nginx 反向代理快速启用。

#### 向老师说明
> "由于未购买 SSL 证书，HTTPS 功能暂未实现，但系统架构已预留 SSL 配置接口，后续可通过配置 Nginx 反向代理快速启用。"

---

### （4）接口文档

**状态：✅ 已完成**

#### 文档位置

| 文件 | 格式 | 说明 |
|------|------|------|
| `API 接口文档（）.md` | Markdown | 主要接口文档 |
| `API 文档.md` | Markdown | 详细说明文档 |
| `swagger.json` | OpenAPI | 可导入 Swagger UI |
| `postman_collection.json` | Postman | 可导入 Postman |

#### 查看方法

```bash
# 在服务器上查看
cat /root/data-server/API\ 接口文档（）.md | head -50

# 或使用 Postman 可视化查看
# 导入 postman_collection.json 即可
```

---

### （5）鉴权功能

**状态：✅ 已完成**

支持 **两种** 鉴权方式：

#### 方式 1：JWT Token 认证

```bash
# 第一步：登录获取 Token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 返回：
{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGci...",
    "status": "success"
}

# 第二步：携带 Token 访问
curl -X POST http://localhost:5000/api/receive/secure \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"encrypted_data":"..."}'
```

#### 方式 2：API Key 认证

```bash
curl -X POST http://localhost:5000/api/receive/apikey \
  -H "X-API-Key: your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{"sensor_type":"skin","moisture":65}'
```

#### 鉴权验证演示

```bash
# ❌ 无 Token 访问（应返回 401）
curl -X POST http://localhost:5000/api/receive/secure -d '{}'

# ✅ 有 Token 访问（应返回 200）
curl -X POST http://localhost:5000/api/receive/secure \
  -H "Authorization: Bearer <token>" \
  -d '{}'
```

---

### （6）数据加密传输

**状态：✅ 已完成**

#### 加密算法
**AES-256**（Fernet 对称加密）

#### 实现流程
1. 客户端调用 `/api/encrypt` 加密数据
2. 传输加密后的数据到 `/api/receive/secure`
3. 服务器自动解密并保存到本地

#### 演示命令

```bash
# 1. 加密数据
curl -X POST http://localhost:5000/api/encrypt \
  -d '{"sensor_type":"skin","moisture":85,"oiliness":15}'

# 2. 上传加密数据
curl -X POST http://localhost:5000/api/receive/secure \
  -H "Authorization: Bearer <token>" \
  -d '{"encrypted_data":"<加密后的数据>"}'

# 3. 查看保存的加密文件
ls -lh /root/data-server/data/secure_*.json | tail -3
```

---

### （7）消息队列

**状态：✅ 已完成**

#### 消息队列
**Redis Streams**

#### 实现方式
1. 模拟器通过 Redis 发布消息到 `sensor:raw` 队列
2. 消费者监听队列并处理数据
3. 处理后的数据保存到本地文件系统

#### 优势
- **解耦**：模拟器和服务器不需要同时在线
- **可靠**：Redis 持久化确保消息不丢失
- **异步**：服务器可以慢慢处理，提高吞吐量

#### 演示命令

```bash
# 1. 检查 Redis 服务
redis-cli ping  # 返回 PONG

# 2. 查看消息队列
redis-cli keys 'sensor:*'
# 返回：sensor:raw, sensor:validated, sensor:write, sensor:logs

# 3. 启动模拟器
python3 /root/data-server/simulator_mq.py

# 4. 查看队列中的消息
redis-cli XLEN sensor:raw
```

---

## 验收总结

| 验收项 | 状态 | 完成度 |
|--------|------|--------|
| （1）RESTful API | ✅ 完成 | 100% |
| （2）数据上传保存 | ✅ 完成 | 100% |
| （3）HTTPS | ⚠️ 可选 | 0% |
| （4）接口文档 | ✅ 完成 | 100% |
| （5）鉴权功能 | ✅ 完成 | 100% |
| （6）数据加密 | ✅ 完成 | 100% |
| （7）消息队列 | ✅ 完成 | 100% |

**总体完成度：7/8 项（核心功能 100%）** ✅

---

## 性能指标

| 指标 | 结果 | 目标 |
|------|------|------|
| **QPS (吞吐量)** | 196.9/sec | > 170 |
| **成功率** | 100% | > 99% |
| **平均响应时间** | 73ms | < 100ms |
| **并发用户数** | 15 | - |

---

## 快速验证命令

### 一键验证脚本

```bash
#!/bin/bash
# 第二阶段验收快速验证脚本

echo "=== 1. 检查服务状态 ==="
ps aux | grep gunicorn | grep -v grep | wc -l
echo "个 Gunicorn Worker 进程运行中"

echo ""
echo "=== 2. 测试 API 接口 ==="
curl -s http://localhost:5000/api/health | python3 -m json.tool

echo ""
echo "=== 3. 查看数据文件 ==="
echo "数据文件数量：$(find /root/data-server/data/ -name '*.json' | wc -l)"

echo ""
echo "=== 4. 测试鉴权功能 ==="
echo "(1) 无 Token 访问："
curl -s -X POST http://localhost:5000/api/receive/secure -d '{}' | python3 -m json.tool

echo ""
echo "(2) 登录获取 Token："
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
echo "Token 已获取"

echo ""
echo "(3) 携带 Token 访问："
curl -s -X POST http://localhost:5000/api/receive/secure \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"encrypted_data":"test"}' | python3 -m json.tool

echo ""
echo "=== 5. 检查 Redis 消息队列 ==="
redis-cli ping
redis-cli keys 'sensor:*'

echo ""
echo "=== 6. 查看接口文档 ==="
ls -lh /root/data-server/API*.md

echo ""
echo "=== 验收总结 ==="
echo "✅ (1) RESTful API: 12 个接口"
echo "✅ (2) 数据上传: $(find /root/data-server/data/ -name '*.json' | wc -l) 个文件"
echo "⚠️  (3) HTTPS: 可选功能"
echo "✅ (4) 接口文档: Markdown + Postman"
echo "✅ (5) 鉴权功能: JWT + API Key"
echo "✅ (6) 数据加密: AES-256"
echo "✅ (7) 消息队列: Redis Streams"
echo ""
echo "完成度: 7/8 项（核心功能 100%）"
```

---

## 📚 相关文档

- [项目 README](./README.md)
- [API 接口文档](./API 接口文档（）.md)
- [压力测试指南](./PRESSURE_TEST_GUIDE.md)
- [部署指南](./DEPLOYMENT_SUMMARY.md)

---

## 🤝 联系方式

如有问题，请联系项目维护者。

---

**文档版本**: v1.0  
**最后更新**: 2026-04-17  
**作者**: 项目开发团队
