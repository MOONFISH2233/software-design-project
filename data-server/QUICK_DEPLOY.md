# ⚡ 快速部署命令（复制粘贴即可）

## 🎯 一键部署（在服务器上执行）

```bash
# 连接到服务器
ssh root@47.103.108.47
# 密码: @Dierzu999

# 进入项目目录并拉取代码
cd /root/course-project && git pull origin week5

# 验证代码语法
python3 -m py_compile data-server/app.py

# 重启服务
systemctl restart data-server

# 检查服务状态
systemctl status data-server

# 查看实时日志（确认启动成功）
tail -f logs/server_*.log
```

## ✅ 验证部署

在浏览器中打开：
- **测试页面**: http://47.103.108.47:5000/test
- **首页**: http://47.103.108.47:5000

点击"🎯 开始一键式全功能测试"按钮进行完整验证。

## 🔍 如果遇到问题

### 检查Git配置
```bash
cd /root/course-project
git remote -v
```

如果没有remote或需要更新：
```bash
git remote set-url origin https://github.com/MOONFISH2233/software-design-project.git
git fetch origin week5
git merge origin/week5
```

### 检查服务日志
```bash
journalctl -u data-server -n 50 --no-pager
```

### 检查端口监听
```bash
netstat -tlnp | grep 5000
```

### 手动启动测试（如果systemd有问题）
```bash
cd /root/course-project/data-server
python3 app.py
```

## 📊 预期结果

部署成功后应该看到：

1. **Git输出**:
   ```
   Updating b124191..76faec6
   Fast-forward
    ... (显示新增文件列表)
   ```

2. **服务日志**:
   ```
   Flask 数据服务器 v3.0 - 安全增强版
   * Running on all addresses (0.0.0.0)
   * Running on http://0.0.0.0:5000
   ```

3. **浏览器访问**: 看到紫色渐变的测试平台界面

---

**提示**: 所有代码已推送到GitHub，可以直接在服务器上pull获取！🚀
