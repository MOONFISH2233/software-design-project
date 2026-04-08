# 🚀 远程服务器部署指南

## 📋 部署信息

- **服务器地址**: `47.103.108.47`
- **用户名**: `root`
- **密码**: `@Dierzu999`
- **项目路径**: `/root/course-project`
- **分支**: `week5`
- **GitHub仓库**: https://github.com/MOONFISH2233/software-design-project/tree/week5/data-server

## ✅ 已完成的工作

代码已成功推送到GitHub：
- Commit: `3b8e394`
- 分支: `week5`
- 新增文件: 9个（前端测试平台 + 文档）

## 🔧 部署步骤

### 方法1: 手动SSH部署（推荐）

```bash
# 1. SSH连接到服务器
ssh root@47.103.108.47
# 输入密码: @Dierzu999

# 2. 进入项目目录
cd /root/course-project

# 3. 拉取最新代码
git pull origin week5

# 4. 验证代码完整性
python3 -m py_compile data-server/app.py

# 5. 重启服务
systemctl restart data-server

# 6. 检查服务状态
systemctl status data-server

# 7. 查看日志确认启动成功
tail -f logs/server_*.log
```

### 方法2: 一键部署脚本

在服务器上创建并执行：

```bash
#!/bin/bash
# deploy.sh

echo "========================================"
echo "  开始部署前端测试平台"
echo "========================================"

cd /root/course-project

echo "[1/4] 拉取最新代码..."
git pull origin week5

echo "[2/4] 验证代码语法..."
python3 -m py_compile data-server/app.py
if [ $? -ne 0 ]; then
    echo "❌ 代码语法错误，部署中止！"
    exit 1
fi

echo "[3/4] 重启服务..."
systemctl restart data-server

echo "[4/4] 检查服务状态..."
sleep 2
systemctl is-active data-server

if [ $? -eq 0 ]; then
    echo "✅ 部署成功！"
    echo ""
    echo "访问地址:"
    echo "  - 测试页面: http://47.103.108.47:5000/test"
    echo "  - 首页: http://47.103.108.47:5000"
else
    echo "❌ 服务启动失败，请检查日志"
    journalctl -u data-server -n 50 --no-pager
fi
```

执行：
```bash
chmod +x deploy.sh
./deploy.sh
```

### 方法3: 使用Windows部署脚本

双击运行：
```
deploy_to_server.bat
```

然后在提示时输入密码：`@Dierzu999`

## 📊 部署验证清单

部署完成后，请验证以下功能：

### 1. 服务状态检查
```bash
# 检查进程是否运行
ps aux | grep python

# 检查端口监听
netstat -tlnp | grep 5000

# 检查systemd服务
systemctl status data-server
```

### 2. API健康检查
```bash
curl http://localhost:5000/api/health
```

预期响应：
```json
{
  "status": "healthy",
  "service": "Flask Data Server v3.0",
  "timestamp": "...",
  "features": ["JWT Auth", "API Key", "AES Encryption"]
}
```

### 3. 前端页面访问
在浏览器中打开：
- **测试页面**: http://47.103.108.47:5000/test
- **首页**: http://47.103.108.47:5000

应该能看到紫色渐变的测试平台界面。

### 4. 功能测试
点击"🎯 开始一键式全功能测试"按钮，验证所有12项测试通过。

## 🔍 故障排查

### 问题1: Git拉取失败

**症状**: `git pull` 报错

**解决**:
```bash
# 检查Git配置
git remote -v

# 如果remote未配置，重新添加
git remote add origin https://github.com/MOONFISH2233/software-design-project.git

# 或者使用SSH方式（需要配置SSH密钥）
git remote set-url origin git@github.com:MOONFISH2233/software-design-project.git
```

### 问题2: 服务启动失败

**症状**: `systemctl restart data-server` 失败

**解决**:
```bash
# 查看详细错误日志
journalctl -u data-server -n 100 --no-pager

# 常见原因：
# 1. 端口被占用: lsof -i:5000
# 2. 依赖缺失: pip3 install -r requirements.txt
# 3. 配置文件错误: 检查 app.py 语法
```

### 问题3: 前端页面无法访问

**症状**: 浏览器显示连接错误或404

**解决**:
```bash
# 1. 检查static目录是否存在
ls -la /root/course-project/data-server/static/

# 2. 检查test_dashboard.html是否存在
ls -la /root/course-project/data-server/static/test_dashboard.html

# 3. 检查app.py是否有路由配置
grep -n "def test_dashboard" /root/course-project/data-server/app.py

# 4. 重启服务
systemctl restart data-server
```

### 问题4: 防火墙阻止访问

**症状**: 本地可以访问，但外网无法访问

**解决**:
```bash
# 检查防火墙规则
firewall-cmd --list-all

# 添加5000端口
firewall-cmd --add-port=5000/tcp --permanent
firewall-cmd --reload

# 如果使用阿里云，还需在安全组中开放5000端口
```

## 📝 部署后检查

### 文件结构验证
```bash
cd /root/course-project/data-server
tree -L 2 -I '__pycache__|*.pyc'
```

应该看到：
```
data-server/
├── static/
│   └── test_dashboard.html      ← 新增
├── app.py                        ← 已修改
├── start_test_platform.bat       ← 新增
├── start_test_platform.sh        ← 新增
├── QUICK_TEST_START.md           ← 新增
├── FRONTEND_TEST_GUIDE.md        ← 新增
├── FRONTEND_TEST_COMPLETED.md    ← 新增
├── TEST_DEMO.md                  ← 新增
└── FILES_CHECKLIST.md            ← 新增
```

### 服务日志检查
```bash
# 实时查看日志
tail -f /root/course-project/logs/server_*.log

# 应该看到类似输出：
# Flask 数据服务器 v3.0 - 安全增强版
# * Running on all addresses (0.0.0.0)
# * Running on http://0.0.0.0:5000
```

## 🎯 访问测试平台

部署成功后，可以通过以下方式访问：

### 从服务器本地访问
```
http://localhost:5000/test
```

### 从外网访问
```
http://47.103.108.47:5000/test
```

### 默认账户
- 用户名: `admin`
- 密码: `admin123`

## 📞 技术支持

如遇到问题：
1. 查看服务日志: `journalctl -u data-server -f`
2. 检查应用日志: `tail -f /root/course-project/logs/server_*.log`
3. 验证代码语法: `python3 -m py_compile data-server/app.py`
4. 参考文档: `FRONTEND_TEST_GUIDE.md`

---

**提示**: 部署完成后，建议立即访问测试页面并运行一键式全功能测试，确保所有功能正常！🚀
