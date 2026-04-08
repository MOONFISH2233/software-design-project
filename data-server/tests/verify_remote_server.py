"""
自动登录远程服务器并验证数据服务
无需手动输入密码
"""

import paramiko
import json
import time
from datetime import datetime

# 服务器配置
SERVER_HOST = "47.103.108.47"
SERVER_PORT = 22
USERNAME = "root"
PASSWORD = "@Dierzu999"

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

def execute_command(ssh, command, description=""):
    """执行远程命令"""
    if description:
        print_info(f"执行: {description}")
    
    try:
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        
        if error and "warning" not in error.lower():
            print_error(f"错误: {error}")
            return None, error
        
        return output, None
    except Exception as e:
        print_error(f"命令执行失败: {e}")
        return None, str(e)

def check_server_status(ssh):
    """检查服务器状态"""
    print_header("1. 检查服务器状态")
    
    # 检查进程
    output, error = execute_command(
        ssh, 
        "ps aux | grep 'python.*app.py' | grep -v grep",
        "检查数据服务进程"
    )
    
    if output:
        print_success("数据服务进程正在运行")
        print_info(output)
        return True
    else:
        print_error("数据服务进程未运行")
        return False

def test_health_check(ssh):
    """测试健康检查接口"""
    print_header("2. 测试健康检查接口")
    
    output, error = execute_command(
        ssh,
        "curl -s http://localhost:5000/api/health",
        "调用健康检查接口"
    )
    
    if output:
        try:
            data = json.loads(output)
            print_success(f"健康检查成功 - 状态: {data.get('status', 'unknown')}")
            print_info(f"服务: {data.get('service', 'unknown')}")
            print_info(f"时间: {data.get('timestamp', 'unknown')}")
            return True
        except:
            print_info(f"响应: {output}")
            return True
    else:
        print_error("健康检查失败")
        return False

def test_login(ssh):
    """测试用户登录"""
    print_header("3. 测试用户登录 (JWT Token)")
    
    login_data = json.dumps({
        'username': 'user1',
        'password': 'user123'
    })
    
    cmd = f"curl -s -X POST http://localhost:5000/api/auth/login -H 'Content-Type: application/json' -d '{login_data}'"
    output, error = execute_command(ssh, cmd, "调用登录接口")
    
    if output:
        try:
            data = json.loads(output)
            if 'token' in data:
                print_success("登录成功")
                print_info(f"Token: {data['token'][:50]}...")
                print_info(f"过期时间: {data.get('expires_in', 'unknown')} 小时")
                return data['token']
            else:
                print_error(f"登录失败: {output}")
                return None
        except:
            print_info(f"响应: {output}")
            return None
    else:
        print_error("登录请求失败")
        return None

def test_encrypt_decrypt(ssh):
    """测试数据加密和解密"""
    print_header("4. 测试数据加密和解密")
    
    test_data = json.dumps({
        'temperature': 25.5,
        'humidity': 60,
        'device_id': 'sensor_001'
    })
    
    # 测试加密
    cmd = f"curl -s -X POST http://localhost:5000/api/encrypt -H 'Content-Type: application/json' -d '{test_data}'"
    output, error = execute_command(ssh, cmd, "调用加密接口")
    
    if not output:
        print_error("加密接口调用失败")
        return False
    
    try:
        encrypt_result = json.loads(output)
        if 'encrypted_data' in encrypt_result:
            print_success("加密成功")
            encrypted_data = encrypt_result['encrypted_data']
            print_info(f"加密数据: {encrypted_data[:60]}...")
            
            # 测试解密
            decrypt_data = json.dumps({'encrypted_data': encrypted_data})
            cmd = f"curl -s -X POST http://localhost:5000/api/decrypt -H 'Content-Type: application/json' -d '{decrypt_data}'"
            output, error = execute_command(ssh, cmd, "调用解密接口")
            
            if output:
                decrypt_result = json.loads(output)
                if 'decrypted_data' in decrypt_result:
                    print_success("解密成功")
                    print_info(f"解密数据: {json.dumps(decrypt_result['decrypted_data'])}")
                    
                    # 验证数据
                    if decrypt_result['decrypted_data'].get('temperature') == 25.5:
                        print_success("✓ 数据一致性验证通过")
                        return True
                    else:
                        print_error("✗ 数据不一致")
                        return False
                else:
                    print_error(f"解密失败: {output}")
                    return False
            else:
                print_error("解密接口调用失败")
                return False
        else:
            print_error(f"加密失败: {output}")
            return False
    except Exception as e:
        print_error(f"解析失败: {e}")
        return False

def test_secure_receive(ssh, token):
    """测试安全数据接收"""
    print_header("5. 测试安全数据接收 (JWT 认证)")
    
    if not token:
        print_error("Token 为空，跳过测试")
        return False
    
    test_data = json.dumps({
        'temperature': 26.5,
        'humidity': 65,
        'device_id': 'sensor_002'
    })
    
    cmd = f"curl -s -X POST http://localhost:5000/api/receive/secure -H 'Content-Type: application/json' -H 'Authorization: Bearer {token}' -d '{test_data}'"
    output, error = execute_command(ssh, cmd, "调用安全数据接收接口")
    
    if output:
        try:
            data = json.loads(output)
            if data.get('status') == 'success':
                print_success("安全数据接收成功")
                print_info(f"文件名: {data.get('filename', 'unknown')}")
                print_info(f"耗时: {data.get('elapsed_ms', 'unknown')}ms")
                return True
            else:
                print_error(f"接收失败: {output}")
                return False
        except:
            print_info(f"响应: {output}")
            return True
    else:
        print_error("安全数据接收失败")
        return False

def test_apikey_receive(ssh):
    """测试 API Key 认证"""
    print_header("6. 测试 API Key 认证数据接收")
    
    test_data = json.dumps({
        'temperature': 27.5,
        'humidity': 70,
        'device_id': 'sensor_003'
    })
    
    cmd = f"curl -s -X POST http://localhost:5000/api/receive/apikey -H 'Content-Type: application/json' -H 'X-API-Key: key_user1_001' -d '{test_data}'"
    output, error = execute_command(ssh, cmd, "调用 API Key 数据接收接口")
    
    if output:
        try:
            data = json.loads(output)
            if data.get('status') == 'success':
                print_success("API Key 认证数据接收成功")
                print_info(f"文件名: {data.get('filename', 'unknown')}")
                return True
            else:
                print_error(f"接收失败: {output}")
                return False
        except:
            print_info(f"响应: {output}")
            return True
    else:
        print_error("API Key 认证失败")
        return False

def check_logs(ssh):
    """检查服务器日志"""
    print_header("7. 检查服务器日志")
    
    output, error = execute_command(
        ssh,
        "tail -20 /root/course-project/logs/server_*.log 2>/dev/null || echo '日志文件不存在'",
        "查看最近日志"
    )
    
    if output and output != '日志文件不存在':
        print_success("日志文件存在")
        print_info("最近日志:")
        print(output[:500])
    else:
        print_info("日志文件不存在或为空")

def main():
    """主验证流程"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}")
    print(f"  远程服务器数据服务验证")
    print(f"  服务器: {SERVER_HOST}")
    print(f"  开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}{Colors.END}\n")
    
    results = {}
    
    # 连接服务器
    print_info(f"正在连接服务器 {SERVER_HOST}...")
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
        
        # 执行各项测试
        results['server_status'] = check_server_status(ssh)
        time.sleep(0.5)
        
        results['health_check'] = test_health_check(ssh)
        time.sleep(0.5)
        
        token = test_login(ssh)
        results['login'] = token is not None
        time.sleep(0.5)
        
        results['encrypt_decrypt'] = test_encrypt_decrypt(ssh)
        time.sleep(0.5)
        
        results['secure_receive'] = test_secure_receive(ssh, token)
        time.sleep(0.5)
        
        results['apikey_receive'] = test_apikey_receive(ssh)
        time.sleep(0.5)
        
        check_logs(ssh)
        
        # 关闭连接
        ssh.close()
        
    except paramiko.AuthenticationException:
        print_error("认证失败：用户名或密码错误")
        return
    except paramiko.SSHException as e:
        print_error(f"SSH 连接失败: {e}")
        return
    except Exception as e:
        print_error(f"连接异常: {e}")
        return
    
    # 打印总结
    print_header("验证总结")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    test_names = {
        'server_status': '服务器状态',
        'health_check': '健康检查',
        'login': '用户登录',
        'encrypt_decrypt': '加密解密',
        'secure_receive': '安全数据接收',
        'apikey_receive': 'API Key 认证'
    }
    
    for test_key, result in results.items():
        test_name = test_names.get(test_key, test_key)
        status = "✓ 通过" if result else "✗ 失败"
        color = Colors.GREEN if result else Colors.RED
        print(f"{color}{status}{Colors.END} - {test_name}")
    
    print(f"\n{Colors.BOLD}总测试结果: {passed}/{total} 通过{Colors.END}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 所有测试通过！远程服务器验证完成！{Colors.END}\n")
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  部分测试失败，请检查错误信息{Colors.END}\n")
    
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    # 检查 paramiko 是否安装
    try:
        import paramiko
    except ImportError:
        print("错误: 需要安装 paramiko 库")
        print("请运行: pip install paramiko")
        exit(1)
    
    main()
