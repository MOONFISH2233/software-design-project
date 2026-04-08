# SSH 免密登录配置成功！✅

## 🎉 配置完成

SSH 密钥已生成并上传到服务器，现在可以免密登录了！

## 使用方法

### 方式一：使用简化命令（推荐）

```bash
# 使用别名登录（无需密码）
ssh -i /c/Users/MOONFISH/.ssh/id_rsa_server root@47.103.108.47
```

### 方式二：配置 SSH Config（更方便）

手动创建配置文件 `C:\Users\MOONFISH\.ssh\config`，内容如下：

```
Host server-47
    HostName 47.103.108.47
    User root
    IdentityFile ~/.ssh/id_rsa_server
    IdentitiesOnly yes
```

然后就可以这样登录：
```bash
ssh server-47
```

### 方式三：添加到 Windows 环境变量

创建批处理脚本 `ssh-server.bat`：

```batch
@echo off
ssh -i C:\Users\MOONFISH\.ssh\id_rsa_server root@47.103.108.47 %*
```

## 测试连接

```bash
# 测试免密登录
ssh -i /c/Users/MOONFISH/.ssh/id_rsa_server root@47.103.108.47 "echo 连接成功！"

# 查看服务器信息
ssh -i /c/Users/MOONFISH/.ssh/id_rsa_server root@47.103.108.47 "uname -a"

# 查看目录
ssh -i /c/Users/MOONFISH/.ssh/id_rsa_server root@47.103.108.47 "ls -la /root/data-server/"
```

## 密钥文件位置

- **私钥**: `C:\Users\MOONFISH\.ssh\id_rsa_server`
- **公钥**: `C:\Users\MOONFISH\.ssh\id_rsa_server.pub`

⚠️ **重要提示**：不要分享私钥文件！

## 如果还是提示输入密码

1. 检查权限：
```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

2. 重启 SSH 服务：
```bash
systemctl restart sshd
```

3. 重新上传公钥：
```bash
cat /c/Users/MOONFISH/.ssh/id_rsa_server.pub | ssh root@47.103.108.47 "cat >> ~/.ssh/authorized_keys"
```
