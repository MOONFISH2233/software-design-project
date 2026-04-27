# MySQL 8.0 升级完整指南

## 📋 当前状态

- **服务器IP**: 47.103.108.47
- **当前MySQL版本**: 5.7.40
- **目标MySQL版本**: 8.0.x (推荐 8.0.26+)
- **宝塔面板地址**: https://47.103.108.47:8888/90a1c9ff
- **面板用户名**: f151c119
- **面板密码**: 196f5df06612

---

## ⚠️ 重要提示

**MySQL升级会影响正在运行的应用**,请确保:
1. 已通知相关人员维护时间窗口
2. 已有数据备份(或准备备份)
3. 升级后需要测试应用兼容性

---

## 🎯 推荐方案:通过宝塔面板升级(最简单安全)

### 步骤1: 登录宝塔面板

在浏览器中打开:
```
https://47.103.108.47:8888/90a1c9ff
```

输入:
- 用户名: `f151c119`
- 密码: `196f5df06612`

### 步骤2: 进入MySQL管理

1. 左侧菜单点击 **"数据库"**
2. 找到 **"MySQL管理器"** 或显示为 **"MySQL 5.7"**
3. 点击右侧的 **"设置"** 按钮

### 步骤3: 切换版本

1. 在设置页面找到 **"切换版本"** 选项
2. 在下拉菜单中选择 **"MySQL 8.0.x"** (建议选择 8.0.26 或更高版本)
3. 点击 **"确定"** 开始升级

### 步骤4: 等待升级完成

- ⏱️ 升级过程通常需要 **10-20分钟**
- 🔄 期间MySQL服务会自动重启
- ⚠️ **请勿关闭浏览器或刷新页面**
- 📊 可以在页面上看到升级进度

### 步骤5: 验证升级

升级完成后,在本地终端执行:

```bash
ssh root@47.103.108.47 "mysql --version"
```

应该显示类似:
```
mysql  Ver 8.0.xx for Linux on x86_64 (MySQL Community Server - GPL)
```

---

## 🔧 备选方案:命令行升级(高级用户)

⚠️ **警告**: 此方法风险较高,仅建议有经验的用户使用

### 前置条件

需要先获取MySQL root密码。可以通过以下方式:

1. **查看宝塔数据库配置**:
```bash
ssh root@47.103.108.47 'cat /www/server/panel/data/default.sql | grep mysql_root'
```

2. **或者重置MySQL密码**:
```bash
ssh root@47.103.108.47 'bt 14'  # 选择修改MySQL root密码
```

### 升级步骤

```bash
# 1. 连接服务器
ssh root@47.103.108.47

# 2. 备份数据
mysqldump -u root -p --all-databases > /root/mysql_backup/full_backup.sql

# 3. 停止MySQL服务
systemctl stop mysqld

# 4. 备份配置文件
cp /etc/my.cnf /etc/my.cnf.backup

# 5. 卸载MySQL 5.7
yum remove -y mysql-community-server mysql-community-client

# 6. 安装MySQL 8.0仓库
yum install -y https://dev.mysql.com/get/mysql80-community-release-el7-3.noarch.rpm

# 7. 禁用5.7,启用8.0
yum-config-manager --disable mysql57-community
yum-config-manager --enable mysql80-community

# 8. 安装MySQL 8.0
yum install -y mysql-community-server

# 9. 启动新版本
systemctl start mysqld

# 10. 检查临时密码
grep 'temporary password' /var/log/mysqld.log

# 11. 使用临时密码登录并修改密码
mysql -u root -p
ALTER USER 'root'@'localhost' IDENTIFIED BY '你的新密码';
FLUSH PRIVILEGES;
EXIT;

# 12. 恢复数据(如果需要)
mysql -u root -p < /root/mysql_backup/full_backup.sql
```

---

## ✅ 升级后验证清单

### 1. 检查MySQL版本
```bash
ssh root@47.103.108.47 "mysql --version"
```

### 2. 检查MySQL服务状态
```bash
ssh root@47.103.108.47 "systemctl status mysqld"
```

### 3. 测试数据库连接
```bash
ssh root@47.103.108.47 "mysql -u root -p -e 'SHOW DATABASES;'"
```

### 4. 检查应用是否正常
访问你的应用API,确认能正常连接数据库:
```bash
curl http://47.103.108.47:5000/api/health
```

### 5. 查看错误日志(如有问题)
```bash
ssh root@47.103.108.47 "tail -100 /www/server/data/*.err"
```

---

## 🆘 常见问题

### Q1: 升级失败怎么办?
**A**: 
1. 查看错误日志: `/www/server/data/*.err`
2. 尝试回滚到备份版本
3. 联系宝塔官方支持

### Q2: 升级后应用无法连接数据库?
**A**:
1. 检查应用配置中的数据库密码是否需要更新
2. 检查MySQL 8.0的身份验证插件变化
3. 可能需要运行: `ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'password';`

### Q3: 升级需要多长时间?
**A**: 通常10-20分钟,取决于数据量和服务器性能

### Q4: 升级会丢失数据吗?
**A**: 正常情况下不会,但强烈建议先备份

---

## 📞 技术支持

- **宝塔官方论坛**: https://www.bt.cn/bbs/
- **MySQL 8.0官方文档**: https://dev.mysql.com/doc/refman/8.0/en/upgrading.html
- **项目Issues**: https://github.com/MOONFISH2233/software-design-project/issues

---

## 📝 升级记录

| 日期 | 操作 | 结果 | 备注 |
|------|------|------|------|
| 2026-04-24 | 计划升级MySQL 5.7 → 8.0 | 待执行 | - |

---

**最后更新**: 2026-04-24  
**文档版本**: 1.0
