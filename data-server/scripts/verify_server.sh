#!/usr/bin/env bash
# 自动登录服务器并验证数据服务

# 使用 expect 自动输入密码
expect << 'EOF'
set timeout 30

# 测试健康检查
spawn ssh root@47.103.108.47 "curl -s http://localhost:5000/api/health"
expect {
    "password:" {
        send "@Dierzu999\r"
        exp_continue
    }
    eof
}

EOF
