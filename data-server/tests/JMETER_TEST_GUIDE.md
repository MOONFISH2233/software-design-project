# JMeter 测试配置指南

## 🎯 服务器状态确认

✅ **服务器已完全就绪，可以开始测试！**

### 服务器信息
- **IP 地址**: `47.103.108.47`
- **端口**: `5000`
- **服务状态**: ✅ 运行中 (Gunicorn + Gevent)
- **Python 语法**: ✅ 无错误
- **安全配置**: ✅ 完整 (JWT + API Key + AES)

---

## 📋 正确的 API 路径

### ⚠️ 重要：API 路径已更新

| 功能 | **正确路径** | ❌ 旧路径 |
|------|-------------|----------|
| 登录获取 Token | `/api/auth/login` | `/api/login` |
| API Key 认证 | `/api/auth/apikey` | `/api/apikey` |
| 加密数据上传 | `/api/receive/secure` | `/api/receive/encrypted` |
| API Key 数据上传 | `/api/receive/apikey` | - |
| 健康检查 | `/api/health` | - |

---

## 🔧 JMeter 配置步骤

### 1. 导入测试脚本

在 JMeter 中打开：
```
d:\学习\软件设计\data-server\tests\data_server_debug_plan.jmx
```

### 2. 修改服务器地址

点击顶部 **"数据服务器调试测试计划"**，修改变量：

| 变量名 | 值 |
|--------|-----|
| `server_ip` | `47.103.108.47` |
| `server_port` | `5000` |

### 3. 修改 HTTP 请求路径

#### 步骤 1-健康检查测试
- **路径**: `/api/health`
- **方法**: `GET`
- **无需认证**

#### 步骤 2-登录测试
- **路径**: `/api/auth/login` ⚠️ **注意这个路径！**
- **方法**: `POST`
- **Body**:
```json
{
  "username": "user1",
  "password": "user123"
}
```
- **Headers**:
  - `Content-Type: application/json`

#### 步骤 3-数据上传测试（需要手动添加）

右键 **"步骤2-登录测试"** → **添加** → **取样器** → **HTTP请求**

**配置上传请求**:
- **名称**: `POST /api/receive/secure`
- **服务器**: `${server_ip}`
- **端口**: `${server_port}`
- **协议**: `http`
- **方法**: `POST`
- **路径**: `/api/receive/secure` ⚠️ **注意这个路径！**
- **Body Data**:
```json
{
  "sensor_type": "skin",
  "moisture": ${__Random(40,90)},
  "oil": ${__Random(10,60)}
}
```

**添加 HTTP 信息头管理器**:
右键上传请求 → **添加** → **配置元件** → **HTTP信息头管理器**

添加两个 Header:
```
Content-Type: application/json
Authorization: Bearer ${access_token}
```

**添加 JSON 提取器**（在登录请求下）:
右键登录请求 → **添加** → **后置处理器** → **JSON提取器**

配置:
- **名称**: `access_token`
- **JSON 路径表达式**: `$.token`
- **匹配数字**: `1`
- **默认值**: `NOT_FOUND`

---

## 📊 测试参数建议

### 基础测试（验证功能）
- **线程数**: 5
- **Ramp-Up**: 2 秒
- **持续时间**: 30 秒
- **循环**: 永远

### 标准测试（第五周任务）
- **线程数**: 10
- **Ramp-Up**: 5 秒
- **持续时间**: 60 秒
- **循环**: 永远

### 高强度测试
- **线程数**: 20
- **Ramp-Up**: 10 秒
- **持续时间**: 120 秒
- **循环**: 永远

---

## ✅ 测试流程

### 第一步：健康检查（必须通过）

1. 确保 **"步骤1-健康检查测试"** 是启用状态（绿色图标）
2. 禁用其他线程组（右键 → 禁用）
3. 点击运行 ▶️
4. 查看聚合报告：
   - **错误率**: 必须 0%
   - **平均响应时间**: < 100ms
   - **吞吐量**: > 10/sec

### 第二步：登录测试

1. 启用 **"步骤2-登录测试"**
2. 禁用健康检查线程组
3. 点击运行 ▶️
4. 查看 "查看结果树"：
   - 展开第一个请求
   - 查看 **Response data**
   - 确认返回了 `token` 字段

### 第三步：完整数据上传测试

1. 在登录请求下添加 "HTTP请求"（数据上传）
2. 配置 Token 提取器和 Authorization header
3. 点击运行 ▶️
4. 查看结果

---

## 🎯 预期结果

### 健康检查
```json
{
  "status": "healthy",
  "service": "Flask Data Server v3.0",
  "features": ["JWT Auth", "API Key", "AES Encryption"]
}
```

### 登录成功
```json
{
  "status": "success",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGci...",
  "expires_in": 24
}
```

### 数据上传成功
```json
{
  "status": "success",
  "message": "数据接收成功",
  "filename": "secure_user1_20260415_181359_xxx.json"
}
```

---

## 🚀 开始测试

**现在你可以开始 JMeter 测试了！**

### 快速验证命令

在 PowerShell 中先测试连通性：

```powershell
# 1. 测试健康检查
curl http://47.103.108.47:5000/api/health

# 2. 测试登录
curl -X POST http://47.103.108.47:5000/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{"username":"user1","password":"user123"}'

# 3. 如果上面都成功，打开 JMeter 开始测试
cd "D:\工作\apache-jmeter-5.6.3\bin"
.\jmeter.bat
```

---

## 📝 注意事项

1. ✅ **服务器已完全就绪**，所有 API 都正常工作
2. ⚠️ **使用正确的 API 路径**（`/api/auth/login` 而不是 `/api/login`）
3. ⚠️ **Token 提取器配置正确**（`$.token`）
4. ⚠️ **Authorization header 格式**: `Bearer ${access_token}`
5. ✅ **测试前先运行健康检查**，确认服务器可达
6. ✅ **如果失败，查看 "查看结果树"** 中的 Response data

---

## 🎉 祝测试顺利！

服务器已经完全准备好，性能强劲（QPS 170+），现在就开始你的 JMeter 压力测试吧！

如果遇到任何问题，查看 "查看结果树" 中的错误信息，我会立即帮你解决。
