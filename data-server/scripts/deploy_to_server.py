"""
自动上传代码到远程服务器并重启服务
无需手动输入密码
"""

import paramiko
import os
from datetime import datetime

# 服务器配置
SERVER_HOST = "47.103.108.47"
SERVER_PORT = 22
USERNAME = "root"
PASSWORD = "@Dierzu999"
REMOTE_PATH = "/root/course-project/app.py"
LOCAL_PATH = "app.py"

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.YELLOW}ℹ {text}{Colors.END}")

def main():
    """主上传流程"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}")
    print(f"  自动上传代码到远程服务器")
    print(f"  服务器: {SERVER_HOST}")
    print(f"  开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}{Colors.END}\n")
    
    # 检查本地文件
    if not os.path.exists(LOCAL_PATH):
        print_error(f"本地文件不存在: {LOCAL_PATH}")
        return
    
    file_size = os.path.getsize(LOCAL_PATH)
    print_info(f"本地文件: {LOCAL_PATH} ({file_size} bytes)")
    print_info(f"远程路径: {REMOTE_PATH}")
    
    # 连接服务器
    print_info(f"\n正在连接服务器 {SERVER_HOST}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(
            hostname=SERVER_HOST,
            port=SERVER_PORT,
            username=USERNAME,
            password=PASSWORD,
            timeout=10
        )
        print_success("服务器连接成功\n")
        
        # 上传文件
        print_header("上传文件")
        sftp = ssh.open_sftp()
        
        print_info(f"正在上传文件...")
        sftp.put(LOCAL_PATH, REMOTE_PATH)
        print_success(f"文件上传成功: {REMOTE_PATH}")
        
        sftp.close()
        
        # 重启服务
        print_header("重启服务")
        
        print_info("停止旧服务...")
        stdin, stdout, stderr = ssh.exec_command("pkill -f 'python3 app.py' || true")
        stdout.channel.recv_exit_status()
        print_success("旧服务已停止")
        
        print_info("启动新服务...")
        stdin, stdout, stderr = ssh.exec_command(
            "cd /root/course-project && nohup python3 app.py > /dev/null 2>&1 &",
            get_pty=True
        )
        stdout.channel.recv_exit_status()
        print_success("新服务已启动")
        
        # 等待服务启动
        print_info("等待服务启动 (5秒)...")
        import time
        time.sleep(5)
        
        # 验证服务
        print_header("验证服务")
        
        stdin, stdout, stderr = ssh.exec_command(
            "curl -s http://localhost:5000/api/health"
        )
        output = stdout.read().decode('utf-8').strip()
        
        if output and 'healthy' in output:
            print_success("服务验证成功！")
            print_info(f"健康检查: {output}")
        else:
            print_error("服务验证失败")
            print_info(f"响应: {output}")
        
        # 关闭连接
        ssh.close()
        
        print(f"\n{Colors.GREEN}{Colors.BOLD}{'='*60}")
        print(f"  🎉 代码上传和服务重启完成！")
        print(f"{'='*60}{Colors.END}\n")
        
    except paramiko.AuthenticationException:
        print_error("认证失败：用户名或密码错误")
    except paramiko.SSHException as e:
        print_error(f"SSH 连接失败: {e}")
    except Exception as e:
        print_error(f"操作异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
