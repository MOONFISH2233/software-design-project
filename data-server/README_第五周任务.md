# 第五周任务 - 快速开始指南

## 🎯 任务目标

1. ✅ 实现数据传输过程的加密和鉴权
2. ✅ 在至少 3 台本地电脑上，使用 JMeter 进行压力测试
3. ✅ 准备第二阶段验收

---

## ⚡ 5 分钟快速开始

### 步骤 1: 启动服务器

```bash
cd d:\学习\软件设计\data-server
python app.py
```

看到以下信息表示成功：
```
============================================================
Flask 数据服务器 v3.0 - 安全增强版
============================================================
默认用户账户：
  - admin / admin123 (管理员)
  - user1 / user123 (普通用户)
  - user2 / user123 (普通用户)
  - user3 / user123 (普通用户)
============================================================
```

### 步骤 2: 运行快速测试

打开新的命令行窗口：
```bash
.\quick_test.bat
```

等待测试完成，查看生成的 `stress_test_results.csv`。

---

## 📋 详细使用说明

### 1. 测试加密和鉴权功能

#### 1.1 登录获取 Token

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"user1\",\"password\":\"user123\"}"
```

响应：
```json
{
  "status": "success",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 24
}
```

#### 1.2 加密数据

```bash
curl -X POST http://localhost:5000/api/encrypt \
  -H "Content-Type: application/json" \
  -d "{\"temperature\":25.5,\"humidity\":60}"
```

#### 1.3 发送加密数据

使用上一步获取的 token 和加密数据：
```bash
curl -X POST http://localhost:5000/api/receive/secure \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d "{\"data\":\"<encrypted_data>\",\"encrypted\":true}"
```

---

### 2. 压力测试

#### 单机测试

**测试普通模式:**
```bash
python jmeter_test.py --url http://localhost:5000 --duration 60 --users 10 --type normal
```

**测试 JWT 认证模式:**
```bash
python jmeter_test.py --url http://localhost:5000 --duration 60 --users 10 --username user1 --password user123 --type encrypted
```

**测试 API Key 模式:**
```bash
python jmeter_test.py --url http://localhost:5000 --duration 60 --users 10 --apikey key_user1_001 --type apikey
```

#### 运行所有测试

```bash
.\run_all_tests.bat
```

#### 生成测试报告

```bash
python generate_report.py
```

查看报告：
- Markdown: `test_report.md`
- HTML: `test_report.html`

---

### 3. 多机压力测试（3 台电脑）

#### 准备工作

1. **获取服务器 IP 地址**
   ```bash
   ipconfig
   ```
   假设服务器 IP 为：`192.168.1.100`

2. **在三台电脑上安装依赖**
   ```bash
   pip install requests
   ```

3. **复制测试脚本**
   将 `jmeter_test.py` 复制到三台电脑

#### 执行测试

**电脑 1 (192.168.1.101):**
```bash
python jmeter_test.py \
  --url http://192.168.1.100:5000 \
  --duration 120 \
  --users 20 \
  --username user1 \
  --password user123 \
  --type encrypted
```

**电脑 2 (192.168.1.102):**
```bash
python jmeter_test.py \
  --url http://192.168.1.100:5000 \
  --duration 120 \
  --users 20 \
  --username user2 \
  --password user123 \
  --type encrypted
```

**电脑 3 (192.168.1.103):**
```bash
python jmeter_test.py \
  --url http://192.168.1.100:5000 \
  --duration 120 \
  --users 20 \
  --username user3 \
  --password user123 \
  --type encrypted
```

**同时启动三台电脑的测试:**
在服务器上运行：
```powershell
.\multi_pc_test.ps1
```

---

## 📁 文件说明

### 核心文件
- `app.py` - 主应用（800+ 行，包含加密和鉴权）
- `jmeter_test.py` - 压力测试脚本（300+ 行）
- `generate_report.py` - 测试报告生成

### 测试脚本
- `quick_test.bat` - 快速测试（一键执行）
- `run_all_tests.bat` - 完整测试套件
- `multi_pc_test.ps1` - 多机测试脚本

### 文档
- `PRESSURE_TEST_GUIDE.md` - 详细压力测试指南
- `ACCEPTANCE_PREPARATION.md` - 验收准备文档
- `WEEK5_TASK_SUMMARY.md` - 任务完成总结
- `README_第五周任务.md` - 本文档

---

## 🔑 默认配置

### 用户账户
| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员 |
| user1 | user123 | 普通用户 |
| user2 | user123 | 普通用户 |
| user3 | user123 | 普通用户 |

### API Keys
| API Key | 用户 | 用途 |
|---------|------|------|
| key_admin_001 | admin | 管理员 API Key |
| key_user1_001 | user1 | 用户 1 API Key |
| key_user2_001 | user2 | 用户 2 API Key |
| key_user3_001 | user3 | 用户 3 API Key |

### 接口地址
| 接口 | 地址 | 认证方式 |
|------|------|----------|
| 登录 | `/api/auth/login` | 无 |
| 加密 | `/api/encrypt` | 无 |
| 解密 | `/api/decrypt` | 无 |
| 数据接收（普通） | `/api/receive` | 无 |
| 数据接收（JWT） | `/api/receive/secure` | JWT Token |
| 数据接收（API Key） | `/api/receive/apikey` | API Key |

---

## 📊 性能指标

### 预期性能
| 指标 | 目标值 | 说明 |
|------|--------|------|
| QPS | > 500 | 每秒请求数 |
| 平均响应时间（普通） | < 100ms | 无认证模式 |
| 平均响应时间（JWT） | < 150ms | JWT 认证模式 |
| 平均响应时间（加密） | < 200ms | 加密传输模式 |
| 成功率 | > 99% | 所有模式 |

---

## 🛠️ 故障排查

### 问题 1: 服务器启动失败
**解决**: 
- 检查 Python 版本（需要 3.8+）
- 安装依赖：`pip install flask flask-httpauth flask-limiter cryptography PyJWT`
- 检查 5000 端口是否被占用

### 问题 2: 测试失败
**解决**:
- 确认服务器已启动
- 检查网络连接
- 查看服务器日志：`logs/server_*.log`
- 降低并发用户数

### 问题 3: 多机测试网络不通
**解决**:
- 关闭防火墙
- 确认服务器监听地址为 `0.0.0.0`
- 检查路由器设置

---

## 📚 参考文档

1. **API 文档**: `API 文档.md`
2. **压力测试指南**: `PRESSURE_TEST_GUIDE.md`
3. **验收准备**: `ACCEPTANCE_PREPARATION.md`
4. **任务总结**: `WEEK5_TASK_SUMMARY.md`

---

## ✅ 验收检查清单

### 功能演示
- [ ] 用户登录和 Token 获取
- [ ] 数据加密和解密
- [ ] JWT 认证数据接收
- [ ] API Key 认证数据接收
- [ ] 压力测试演示

### 文档准备
- [ ] API 文档完整
- [ ] 测试报告生成
- [ ] 使用指南清晰
- [ ] 代码注释充分

### 性能指标
- [ ] QPS > 500
- [ ] 平均响应时间 < 200ms
- [ ] 成功率 > 99%
- [ ] 支持 30+ 并发

---

## 🎓 学习资源

- Flask 文档：https://flask.palletsprojects.com/
- JWT 介绍：https://jwt.io/introduction/
- 加密学：https://en.wikipedia.org/wiki/Advanced_Encryption_Standard
- JMeter 教程：https://jmeter.apache.org/usermanual/index.html

---

## 💬 常见问题

**Q: 如何修改 Token 过期时间？**
A: 编辑 `app.py`，修改 `JWT_EXPIRATION_HOURS` 配置

**Q: 如何添加新用户？**
A: 使用 `/api/user/register` 接口或编辑 `security/users.json`

**Q: 如何重置所有配置？**
A: 删除 `security/` 目录，重启服务器

**Q: 加密密钥在哪里？**
A: 存储在 `security/encryption.key` 文件中

---

**祝使用愉快！验收顺利！** 🎉

---

*最后更新：2026-04-03*
*版本：v3.0 - 安全增强版*
