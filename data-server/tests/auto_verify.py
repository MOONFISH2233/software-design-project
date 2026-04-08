"""
自动验证脚本 - 测试所有第五周任务功能
自动执行，无需手动输入
"""

import requests
import time
import json
from datetime import datetime

# 服务器地址
BASE_URL = "http://localhost:5000"

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.YELLOW}ℹ {text}{Colors.END}")

def test_health_check():
    """测试 1: 健康检查"""
    print_header("测试 1: 健康检查")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print_success(f"健康检查成功 - 状态码: {response.status_code}")
            print_info(f"响应: {response.json()}")
            return True
        else:
            print_error(f"健康检查失败 - 状态码: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"健康检查异常: {e}")
        return False

def test_login():
    """测试 2: 用户登录"""
    print_header("测试 2: 用户登录 (JWT Token)")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={'username': 'user1', 'password': 'user123'},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"登录成功 - 用户: user1")
            print_info(f"Token: {data['token'][:50]}...")
            print_info(f"过期时间: {data['expires_in']} 小时")
            return data['token']
        else:
            print_error(f"登录失败 - 状态码: {response.status_code}")
            print_error(f"响应: {response.text}")
            return None
    except Exception as e:
        print_error(f"登录异常: {e}")
        return None

def test_encrypt_decrypt():
    """测试 3: 数据加密和解密"""
    print_header("测试 3: 数据加密和解密")
    
    test_data = {
        'temperature': 25.5,
        'humidity': 60,
        'device_id': 'sensor_001',
        'timestamp': datetime.now().isoformat()
    }
    
    print_info(f"原始数据: {json.dumps(test_data, ensure_ascii=False)}")
    
    try:
        # 加密
        encrypt_response = requests.post(
            f"{BASE_URL}/api/encrypt",
            json=test_data,
            timeout=5
        )
        
        if encrypt_response.status_code != 200:
            print_error(f"加密失败 - 状态码: {encrypt_response.status_code}")
            return False
        
        encrypted_data = encrypt_response.json()['encrypted_data']
        print_success(f"加密成功")
        print_info(f"加密数据: {encrypted_data[:80]}...")
        
        # 解密
        decrypt_response = requests.post(
            f"{BASE_URL}/api/decrypt",
            json={'encrypted_data': encrypted_data},
            timeout=5
        )
        
        if decrypt_response.status_code == 200:
            decrypted = decrypt_response.json()['decrypted_data']
            print_success(f"解密成功")
            print_info(f"解密数据: {json.dumps(decrypted, ensure_ascii=False)}")
            
            # 验证数据一致性
            if decrypted['temperature'] == test_data['temperature']:
                print_success("✓ 数据一致性验证通过")
                return True
            else:
                print_error("✗ 数据一致性验证失败")
                return False
        else:
            print_error(f"解密失败 - 状态码: {decrypt_response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"加密/解密异常: {e}")
        return False

def test_secure_receive(token):
    """测试 4: 安全数据接收 (JWT 认证)"""
    print_header("测试 4: 安全数据接收 (JWT Token 认证)")
    
    if not token:
        print_error("Token 为空，跳过测试")
        return False
    
    test_data = {
        'temperature': 26.5,
        'humidity': 65,
        'device_id': 'sensor_002',
        'timestamp': datetime.now().isoformat()
    }
    
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/receive/secure",
            json=test_data,
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"安全数据接收成功")
            print_info(f"文件名: {data['filename']}")
            print_info(f"请求 ID: {data['request_id']}")
            print_info(f"耗时: {data['elapsed_ms']}ms")
            return True
        else:
            print_error(f"安全数据接收失败 - 状态码: {response.status_code}")
            print_error(f"响应: {response.text}")
            return False
    except Exception as e:
        print_error(f"安全数据接收异常: {e}")
        return False

def test_encrypted_receive(token):
    """测试 5: 加密数据传输"""
    print_header("测试 5: 加密数据传输")
    
    if not token:
        print_error("Token 为空，跳过测试")
        return False
    
    test_data = {
        'temperature': 27.5,
        'humidity': 70,
        'device_id': 'sensor_003',
        'encrypted_test': True,
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        # 先加密数据
        encrypt_response = requests.post(
            f"{BASE_URL}/api/encrypt",
            json=test_data,
            timeout=5
        )
        
        if encrypt_response.status_code != 200:
            print_error("加密失败")
            return False
        
        encrypted_data = encrypt_response.json()['encrypted_data']
        print_info(f"数据已加密")
        
        # 发送加密数据
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.post(
            f"{BASE_URL}/api/receive/secure",
            json={'data': encrypted_data, 'encrypted': True},
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"加密数据传输成功")
            print_info(f"文件名: {data['filename']}")
            print_info(f"耗时: {data['elapsed_ms']}ms")
            return True
        else:
            print_error(f"加密数据传输失败 - 状态码: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"加密数据传输异常: {e}")
        return False

def test_apikey_receive():
    """测试 6: API Key 认证"""
    print_header("测试 6: API Key 认证数据接收")
    
    test_data = {
        'temperature': 28.5,
        'humidity': 75,
        'device_id': 'sensor_004',
        'timestamp': datetime.now().isoformat()
    }
    
    headers = {'X-API-Key': 'key_user1_001'}
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/receive/apikey",
            json=test_data,
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"API Key 认证数据接收成功")
            print_info(f"文件名: {data['filename']}")
            print_info(f"耗时: {data['elapsed_ms']}ms")
            return True
        else:
            print_error(f"API Key 认证失败 - 状态码: {response.status_code}")
            print_error(f"响应: {response.text}")
            return False
    except Exception as e:
        print_error(f"API Key 认证异常: {e}")
        return False

def test_quick_stress():
    """测试 7: 快速压力测试 (10 并发, 10 秒)"""
    print_header("测试 7: 快速压力测试 (10 并发, 10 秒)")
    
    try:
        # 使用 jmeter_test.py 进行快速测试
        import subprocess
        result = subprocess.run(
            ['python', 'jmeter_test.py', 
             '--url', BASE_URL,
             '--duration', '10',
             '--users', '10',
             '--username', 'user1',
             '--password', 'user123',
             '--type', 'encrypted'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print_success("压力测试完成")
            # 显示关键结果
            for line in result.stdout.split('\n'):
                if any(keyword in line for keyword in ['QPS', '成功率', '平均', '总请求']):
                    print_info(line.strip())
            return True
        else:
            print_error(f"压力测试失败")
            print_error(result.stderr)
            return False
    except Exception as e:
        print_error(f"压力测试异常: {e}")
        return False

def main():
    """主测试流程"""
    print(f"\n{Colors.BOLD}{'='*60}")
    print(f"  第五周任务 - 自动验证脚本")
    print(f"  开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}{Colors.END}\n")
    
    results = {}
    
    # 测试 1: 健康检查
    results['health'] = test_health_check()
    time.sleep(1)
    
    # 测试 2: 登录
    token = test_login()
    results['login'] = token is not None
    time.sleep(1)
    
    # 测试 3: 加密解密
    results['encrypt_decrypt'] = test_encrypt_decrypt()
    time.sleep(1)
    
    # 测试 4: 安全数据接收
    results['secure_receive'] = test_secure_receive(token)
    time.sleep(1)
    
    # 测试 5: 加密数据传输
    results['encrypted_receive'] = test_encrypted_receive(token)
    time.sleep(1)
    
    # 测试 6: API Key 认证
    results['apikey_receive'] = test_apikey_receive()
    time.sleep(1)
    
    # 测试 7: 快速压力测试
    results['stress_test'] = test_quick_stress()
    
    # 打印总结
    print_header("验证总结")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    for test_name, result in results.items():
        status = "✓ 通过" if result else "✗ 失败"
        color = Colors.GREEN if result else Colors.RED
        print(f"{color}{status}{Colors.END} - {test_name}")
    
    print(f"\n{Colors.BOLD}总测试结果: {passed}/{total} 通过{Colors.END}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 所有测试通过！第五周任务验证完成！{Colors.END}\n")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}⚠️  部分测试失败，请检查错误信息{Colors.END}\n")
    
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()
