# 📁 项目目录结构说明

## 目录概览

```
data-server/
├── app.py                      # 🚀 主应用入口（Flask API 服务器）
├── security_enhanced.py        # 🔐 安全增强模块（JWT、API Key、加密）
├── module_*.py                 # 📦 MQ 消息队列模块
├── mq_utils.py                 # 🔧 MQ 工具函数
├── README*.md                  # 📖 项目文档
├── .gitignore                  # 🚫 Git 忽略配置
│
├── config/                     # ⚙️ 配置文件
│   ├── gunicorn_config.py      # Gunicorn 生产级配置
│   ├── gunicorn-flask-data-server.service  # Systemd 服务配置
│   ├── requirements.txt        # Python 依赖
│   ├── Jenkinsfile            # CI/CD 配置
│   ├── postman_collection.json # Postman API 集合
│   └── swagger.json           # API 文档（Swagger）
│
├── docs/                       # 📚 文档目录
│   ├── WEEK5_TASK_COMPLETION_REPORT.md    # 第五周任务完成报告
│   ├── PRODUCTION_DEPLOYMENT_REPORT.md    # 生产级部署报告
│   ├── PRESSURE_TEST_GUIDE.md             # 压力测试指南
│   ├── QUICK_REFERENCE.md                 # 快速参考
│   ├── API 文档.md                        # API 接口文档
│   └── ... (其他文档)
│
├── scripts/                    # 🛠️ 脚本工具
│   ├── deploy_production.sh    # 生产环境部署脚本
│   ├── monitor_performance.sh  # 性能监控脚本
│   ├── verify_*.sh/py         # 验证脚本
│   ├── *.bat                   # Windows 批处理脚本
│   └── *.ps1                   # PowerShell 脚本
│
├── tests/                      # 🧪 测试文件
│   ├── jmeter_test.py          # 压力测试工具
│   ├── load_test.py            # 负载测试工具
│   ├── acceptance_demo.py      # 验收演示脚本
│   ├── api_auto_test.py        # API 自动化测试
│   └── auto_test.py            # 自动测试脚本
│
├── examples/                   # 💡 示例代码
│   ├── simulator.py            # 数据模拟器
│   ├── simulator_mq.py         # MQ 模拟器
│   ├── cloud_to_cloud.py       # 云到云传输示例
│   └── local_to_cloud.py       # 本地到云传输示例
│
├── backups/                    # 💾 备份文件
│   ├── app_fix.py              # 应用修复脚本
│   └── temp_*.py              # 临时文件
│
├── security/                   # 🔒 安全配置
│   ├── users.json             # 用户账户配置
│   ├── api_keys.json          # API Key 配置
│   └── encryption.key         # 加密密钥（已忽略）
│
├── data/                       # 📊 数据存储
│   ├── environment/           # 环境传感器数据
│   ├── skin_sensor/           # 皮肤传感器数据
│   └── device/                # 设备数据
│
└── logs/                       # 📝 日志文件
    ├── server_*.log           # 服务器日志
    └── error_*.log            # 错误日志
```

## 核心文件说明

### 🚀 应用核心
- **app.py** - Flask 主应用，提供 RESTful API
- **security_enhanced.py** - 安全模块（JWT、API Key、AES 加密）

### 📦 MQ 模块
- **module_receiver.py** - 数据接收模块
- **module_validator.py** - 数据验证模块
- **module_writer.py** - 数据写入模块
- **module_logger.py** - 日志模块
- **mq_utils.py** - MQ 工具函数

### ⚙️ 配置文件
所有配置文件统一放在 `config/` 目录：
- Gunicorn 配置
- Systemd 服务配置
- 依赖管理
- CI/CD 配置

### 📚 文档
所有文档统一放在 `docs/` 目录：
- 任务报告
- 部署指南
- 测试指南
- API 文档

### 🛠️ 脚本
所有脚本统一放在 `scripts/` 目录：
- 部署脚本
- 监控脚本
- 验证脚本
- 批处理脚本

### 🧪 测试
所有测试文件统一放在 `tests/` 目录：
- 压力测试
- 负载测试
- 验收测试
- 自动化测试

### 💡 示例
所有示例代码统一放在 `examples/` 目录：
- 数据模拟器
- 传输示例
- 多机测试

## 快速开始

### 1. 启动服务器

```bash
# 开发模式
python app.py

# 生产模式（推荐）
systemctl start gunicorn-flask-data-server
```

### 2. 运行测试

```bash
# 压力测试
python tests/jmeter_test.py --url http://localhost:5000 --duration 60 --users 10 --username user1 --password user123 --type encrypted

# 验收测试
python tests/acceptance_demo.py --url http://localhost:5000
```

### 3. 查看文档

```bash
# 查看任务完成报告
cat docs/WEEK5_TASK_COMPLETION_REPORT.md

# 查看部署报告
cat docs/PRODUCTION_DEPLOYMENT_REPORT.md

# 查看压力测试指南
cat docs/PRESSURE_TEST_GUIDE.md
```

### 4. 监控性能

```bash
# 运行性能监控
bash scripts/monitor_performance.sh
```

## 常用命令

### 部署相关
```bash
# 生产环境部署
bash scripts/deploy_production.sh

# 查看服务状态
systemctl status gunicorn-flask-data-server

# 重启服务
systemctl restart gunicorn-flask-data-server
```

### 测试相关
```bash
# 运行所有测试
bash scripts/run_all_tests.bat  # Windows
bash scripts/run_all_tests.sh   # Linux

# 快速测试
bash scripts/quick_test.bat     # Windows
```

### 验证相关
```bash
# 本地验证
python tests/verify_local.py

# 远程验证
python tests/verify_remote_server.py
```

## 注意事项

1. **不要提交敏感信息**
   - `security/*.key` 已在 `.gitignore` 中忽略
   - `.env` 文件不会提交

2. **日志文件**
   - `logs/*.log` 不会提交到 Git
   - 定期清理旧日志文件

3. **测试数据**
   - `tests/stress_test_results_*.csv` 不会提交
   - 每次测试生成新文件

4. **备份文件**
   - `backups/` 目录不会提交
   - 仅用于本地恢复

## 维护建议

1. **定期清理**
   ```bash
   # 清理 Python 缓存
   find . -type d -name __pycache__ -exec rm -rf {} +
   
   # 清理旧日志
   find logs/ -name "*.log" -mtime +30 -delete
   ```

2. **更新依赖**
   ```bash
   pip install -r config/requirements.txt --upgrade
   ```

3. **备份数据**
   ```bash
   tar -czf backup_$(date +%Y%m%d).tar.gz data/ security/
   ```

---

**最后更新**: 2026-04-08  
**维护者**: 软件设计项目组
