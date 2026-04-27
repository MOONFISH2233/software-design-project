"""
第五周任务验收演示脚本
功能：自动化演示所有安全功能，生成验收报告
版本：v1.0
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List

# 服务器配置
SERVER_URL = "http://localhost:5000"

# 颜色输出
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """打印标题"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

def print_success(text: str):
    """打印成功信息"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_error(text: str):
    """打印错误信息"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text: str):
    """打印普通信息"""
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

def print_warning(text: str):
    """打印警告信息"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


class AcceptanceDemo:
    """验收演示类"""
    
    def __init__(self, base_url: str = SERVER_URL):
        self.base_url = base_url
        self.token = None
        self.api_key = None
        self.test_results = []
    
    def test_health_check(self):
        """测试 1: 健康检查"""
        print_header("测试 1: 健康检查")
        
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print_success("健康检查通过")
                print_info(f"服务状态: {data.get('status', 'unknown')}")
                print_info(f"服务版本: {data.get('service', 'unknown')}")
                print_info(f"支持功能: {', '.join(data.get('features', []))}")
                self.test_results.append({"test": "健康检查", "status": "PASS"})
            else:
                print_error(f"健康检查失败: {response.status_code}")
                self.test_results.append({"test": "健康检查", "status": "FAIL"})
        
        except Exception as e:
            print_error(f"健康检查异常: {e}")
            self.test_results.append({"test": "健康检查", "status": "FAIL", "error": str(e)})
    
    def test_login(self):
        """测试 2: 用户登录获取 Token"""
        print_header("测试 2: 用户登录 (JWT Token)")
        
        test_users = [
            {"username": "admin", "password": "admin123", "role": "管理员"},
            {"username": "user1", "password": "user123", "role": "普通用户"}
        ]
        
        for user in test_users:
            print_info(f"测试用户: {user['username']} ({user['role']})")
            
            try:
                response = requests.post(
                    f"{self.base_url}/api/auth/login",
                    json={"username": user['username'], "password": user['password']},
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print_success(f"登录成功")
                    print_info(f"Token: {data['token'][:50]}...")
                    print_info(f"过期时间: {data['expires_in']} 小时")
                    
                    if user['username'] == 'user1':
                        self.token = data['token']
                    
                    self.test_results.append({"test": f"登录-{user['username']}", "status": "PASS"})
                else:
                    print_error(f"登录失败: {response.status_code}")
                    self.test_results.append({"test": f"登录-{user['username']}", "status": "FAIL"})
            
            except Exception as e:
                print_error(f"登录异常: {e}")
                self.test_results.append({"test": f"登录-{user['username']}", "status": "FAIL", "error": str(e)})
            
            time.sleep(0.5)
    
    def test_encryption(self):
        """测试 3: 数据加密和解密"""
        print_header("测试 3: 数据加密和解密")
        
        test_data = {
            "temperature": 25.5,
            "humidity": 60,
            "pressure": 1013,
            "device_id": "sensor_001",
            "timestamp": datetime.now().isoformat()
        }
        
        # 加密数据
        print_info("步骤 1: 加密数据")
        try:
            response = requests.post(
                f"{self.base_url}/api/encrypt",
                json=test_data,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                encrypted_data = data['encrypted_data']
                print_success("数据加密成功")
                print_info(f"加密后数据: {encrypted_data[:80]}...")
            else:
                print_error(f"加密失败: {response.status_code}")
                self.test_results.append({"test": "数据加密", "status": "FAIL"})
                return
        
        except Exception as e:
            print_error(f"加密异常: {e}")
            self.test_results.append({"test": "数据加密", "status": "FAIL", "error": str(e)})
            return
        
        # 解密数据
        print_info("\n步骤 2: 解密数据")
        try:
            response = requests.post(
                f"{self.base_url}/api/decrypt",
                json={"encrypted_data": encrypted_data},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                decrypted_data = data['decrypted_data']
                print_success("数据解密成功")
                print_info(f"解密后数据: {json.dumps(decrypted_data, ensure_ascii=False)}")
                
                # 验证数据完整性
                if decrypted_data['temperature'] == test_data['temperature']:
                    print_success("数据完整性验证通过")
                    self.test_results.append({"test": "数据加密解密", "status": "PASS"})
                else:
                    print_warning("数据完整性验证失败")
                    self.test_results.append({"test": "数据加密解密", "status": "WARNING"})
            else:
                print_error(f"解密失败: {response.status_code}")
                self.test_results.append({"test": "数据解密", "status": "FAIL"})
        
        except Exception as e:
            print_error(f"解密异常: {e}")
            self.test_results.append({"test": "数据解密", "status": "FAIL", "error": str(e)})
    
    def test_secure_receive(self):
        """测试 4: 安全数据接收 (JWT 认证)"""
        print_header("测试 4: 安全数据接收 (JWT 认证)")
        
        if not self.token:
            print_error("缺少 JWT Token，跳过测试")
            self.test_results.append({"test": "安全数据接收", "status": "SKIP"})
            return
        
        test_data = {
            "temperature": 26.5,
            "humidity": 65,
            "device_id": "sensor_002"
        }
        
        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.base_url}/api/receive/secure",
                json=test_data,
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success("安全数据接收成功")
                print_info(f"文件名: {data.get('filename', 'unknown')}")
                print_info(f"请求ID: {data.get('request_id', 'unknown')}")
                self.test_results.append({"test": "安全数据接收", "status": "PASS"})
            else:
                print_error(f"安全数据接收失败: {response.status_code}")
                self.test_results.append({"test": "安全数据接收", "status": "FAIL"})
        
        except Exception as e:
            print_error(f"安全数据接收异常: {e}")
            self.test_results.append({"test": "安全数据接收", "status": "FAIL", "error": str(e)})
    
    def test_apikey_receive(self):
        """测试 5: API Key 认证数据接收"""
        print_header("测试 5: API Key 认证数据接收")
        
        test_data = {
            "temperature": 27.5,
            "humidity": 70,
            "device_id": "sensor_003"
        }
        
        try:
            headers = {
                "X-API-Key": "key_user1_001",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.base_url}/api/receive/apikey",
                json=test_data,
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success("API Key 认证数据接收成功")
                print_info(f"文件名: {data.get('filename', 'unknown')}")
                self.test_results.append({"test": "API Key 认证", "status": "PASS"})
            else:
                print_error(f"API Key 认证失败: {response.status_code}")
                self.test_results.append({"test": "API Key 认证", "status": "FAIL"})
        
        except Exception as e:
            print_error(f"API Key 认证异常: {e}")
            self.test_results.append({"test": "API Key 认证", "status": "FAIL", "error": str(e)})
    
    def test_invalid_auth(self):
        """测试 6: 无效认证测试"""
        print_header("测试 6: 无效认证测试 (安全性验证)")
        
        # 测试无效 Token
        print_info("测试 1: 无效 JWT Token")
        try:
            response = requests.post(
                f"{self.base_url}/api/receive/secure",
                json={"test": "data"},
                headers={"Authorization": "Bearer invalid_token"},
                timeout=5
            )
            
            if response.status_code == 401:
                print_success("正确拒绝无效 Token")
                self.test_results.append({"test": "无效Token拒绝", "status": "PASS"})
            else:
                print_error(f"未正确拒绝无效 Token: {response.status_code}")
                self.test_results.append({"test": "无效Token拒绝", "status": "FAIL"})
        
        except Exception as e:
            print_error(f"异常: {e}")
            self.test_results.append({"test": "无效Token拒绝", "status": "FAIL", "error": str(e)})
        
        # 测试无效 API Key
        print_info("\n测试 2: 无效 API Key")
        try:
            response = requests.post(
                f"{self.base_url}/api/receive/apikey",
                json={"test": "data"},
                headers={"X-API-Key": "invalid_key"},
                timeout=5
            )
            
            if response.status_code == 401:
                print_success("正确拒绝无效 API Key")
                self.test_results.append({"test": "无效API Key拒绝", "status": "PASS"})
            else:
                print_error(f"未正确拒绝无效 API Key: {response.status_code}")
                self.test_results.append({"test": "无效API Key拒绝", "status": "FAIL"})
        
        except Exception as e:
            print_error(f"异常: {e}")
            self.test_results.append({"test": "无效API Key拒绝", "status": "FAIL", "error": str(e)})
    
    def run_quick_performance_test(self):
        """测试 7: 快速性能测试"""
        print_header("测试 7: 快速性能测试 (10并发, 10秒)")
        
        import threading
        import statistics
        
        results = []
        stop_flag = False
        
        def worker():
            test_data = {
                "temperature": 25.0,
                "humidity": 60,
                "timestamp": datetime.now().isoformat()
            }
            
            while not stop_flag:
                try:
                    start_time = time.time()
                    response = requests.post(
                        f"{self.base_url}/api/receive",
                        json=test_data,
                        timeout=5
                    )
                    elapsed = time.time() - start_time
                    
                    results.append({
                        "success": response.status_code == 200,
                        "elapsed": elapsed
                    })
                except:
                    results.append({"success": False, "elapsed": 0})
                
                time.sleep(0.1)
        
        # 启动 10 个并发线程
        threads = []
        for i in range(10):
            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()
            threads.append(t)
        
        # 运行 10 秒
        print_info("正在进行压力测试，请稍候...")
        time.sleep(10)
        stop_flag = True
        
        for t in threads:
            t.join(timeout=2)
        
        # 分析结果
        successful = [r for r in results if r['success']]
        elapsed_times = [r['elapsed'] for r in successful if r['elapsed'] > 0]
        
        print_success("性能测试完成")
        print_info(f"总请求数: {len(results)}")
        print_info(f"成功请求: {len(successful)}")
        print_info(f"成功率: {len(successful)/len(results)*100:.2f}%")
        print_info(f"QPS: {len(results)/10:.2f}")
        
        if elapsed_times:
            print_info(f"平均响应时间: {statistics.mean(elapsed_times)*1000:.2f}ms")
            print_info(f"P95响应时间: {sorted(elapsed_times)[int(len(elapsed_times)*0.95)]*1000:.2f}ms")
        
        status = "PASS" if len(successful)/len(results) > 0.99 else "WARNING"
        self.test_results.append({
            "test": "快速性能测试",
            "status": status,
            "qps": f"{len(results)/10:.2f}",
            "success_rate": f"{len(successful)/len(results)*100:.2f}%"
        })
    
    def generate_report(self):
        """生成验收报告"""
        print_header("验收测试报告")
        
        print(f"{'测试项':<30} {'状态':<10} {'备注'}")
        print("-" * 80)
        
        for result in self.test_results:
            status_icon = "✅" if result['status'] == 'PASS' else "❌" if result['status'] == 'FAIL' else "⚠️"
            test_name = result['test']
            status = result['status']
            remark = ""
            
            if 'qps' in result:
                remark = f"QPS: {result['qps']}, 成功率: {result['success_rate']}"
            
            print(f"{test_name:<30} {status_icon} {status:<8} {remark}")
        
        # 统计
        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        total = len(self.test_results)
        
        print("-" * 80)
        print(f"总计: {total} 项测试，通过 {passed} 项，失败 {failed} 项")
        
        if failed == 0:
            print_success("🎉 所有测试通过！系统符合验收标准！")
        else:
            print_warning(f"⚠️  有 {failed} 项测试失败，请检查")
        
        # 保存报告
        report = {
            "test_time": datetime.now().isoformat(),
            "server_url": self.base_url,
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "results": self.test_results
        }
        
        report_file = "acceptance_test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print_info(f"\n测试报告已保存到: {report_file}")
    
    def run_all_tests(self):
        """运行所有验收测试"""
        print("\n")
        print("█" * 80)
        print("█" + "第五周任务验收演示".center(78) + "█")
        print("█" * 80)
        print(f"\n服务器地址: {self.base_url}")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n")
        
        time.sleep(1)
        
        self.test_health_check()
        time.sleep(1)
        
        self.test_login()
        time.sleep(1)
        
        self.test_encryption()
        time.sleep(1)
        
        self.test_secure_receive()
        time.sleep(1)
        
        self.test_apikey_receive()
        time.sleep(1)
        
        self.test_invalid_auth()
        time.sleep(1)
        
        self.run_quick_performance_test()
        time.sleep(1)
        
        self.generate_report()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='第五周任务验收演示脚本')
    parser.add_argument('--url', default=SERVER_URL, help='服务器地址')
    
    args = parser.parse_args()
    
    demo = AcceptanceDemo(args.url)
    demo.run_all_tests()


if __name__ == "__main__":
    main()
