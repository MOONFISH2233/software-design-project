"""
JMeter 风格压力测试工具
支持多种认证模式：普通、JWT Token、API Key
"""

import requests
import time
import json
import threading
import argparse
import csv
from datetime import datetime


class JMETERTester:
    """压力测试器"""
    
    def __init__(self, base_url, username=None, password=None, api_key=None):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.api_key = api_key
        self.token = None
        self.results = []
        self.stop_flag = False
        
        # 如果是 JWT 认证模式，先登录获取 Token
        if username and password:
            self.login()
    
    def login(self):
        """获取 JWT Token"""
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={'username': self.username, 'password': self.password},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                print(f"✅ 登录成功，获取到 Token")
                return True
            else:
                print(f"❌ 登录失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 登录异常: {e}")
            return False
    
    def send_encrypted_data(self, sensor_data):
        """使用 JWT Token 发送加密数据"""
        headers = {'Authorization': f'Bearer {self.token}'} if self.token else {}
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/api/receive/secure",
                json=sensor_data,
                headers=headers,
                timeout=10
            )
            elapsed = time.time() - start_time
            
            return {
                'success': response.status_code == 200,
                'elapsed': elapsed,
                'status_code': response.status_code,
                'auth_method': 'jwt'
            }
        except Exception as e:
            return {'success': False, 'elapsed': 0, 'error': str(e)}
    
    def send_data_with_apikey(self, sensor_data):
        """使用 API Key 发送数据"""
        headers = {'X-API-Key': self.api_key} if self.api_key else {}
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/api/receive/apikey",
                json=sensor_data,
                headers=headers,
                timeout=10
            )
            elapsed = time.time() - start_time
            
            return {
                'success': response.status_code == 200,
                'elapsed': elapsed,
                'status_code': response.status_code,
                'auth_method': 'api_key'
            }
        except Exception as e:
            return {'success': False, 'elapsed': 0, 'error': str(e)}
    
    def send_normal_data(self, sensor_data):
        """发送普通数据（无认证）"""
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/api/receive",
                json=sensor_data,
                timeout=10
            )
            elapsed = time.time() - start_time
            
            return {
                'success': response.status_code == 200,
                'elapsed': elapsed,
                'status_code': response.status_code,
                'auth_method': 'none'
            }
        except Exception as e:
            return {'success': False, 'elapsed': 0, 'error': str(e)}
    
    def worker_task(self, worker_id, test_type='normal'):
        """工作线程任务"""
        print(f"工作线程 {worker_id} 开始测试")
        
        while not self.stop_flag:
            # 生成测试数据
            sensor_data = {
                'device_id': f'sensor_{worker_id:03d}',
                'temperature': 25.5 + worker_id * 0.1,
                'humidity': 60 + worker_id,
                'pressure': 1013 + worker_id,
                'timestamp': datetime.now().isoformat()
            }
            
            # 根据测试类型发送数据
            if test_type == 'encrypted':
                result = self.send_encrypted_data(sensor_data)
            elif test_type == 'apikey':
                result = self.send_data_with_apikey(sensor_data)
            else:
                result = self.send_normal_data(sensor_data)
            
            result['worker_id'] = worker_id
            result['timestamp'] = datetime.now().isoformat()
            self.results.append(result)
            
            # 短暂延迟，避免过快请求
            time.sleep(0.01)
    
    def run_test(self, duration=60, num_users=10, test_type='normal'):
        """运行压力测试"""
        print("\n" + "=" * 60)
        print(f"开始压力测试 - {test_type.upper()} 模式")
        print(f"持续时间：{duration}秒")
        print(f"并发用户：{num_users}")
        print("=" * 60 + "\n")
        
        # 启动工作线程
        threads = []
        for i in range(num_users):
            t = threading.Thread(target=self.worker_task, args=(i, test_type))
            t.daemon = True
            t.start()
            threads.append(t)
        
        # 等待指定时间
        print(f"测试进行中，请稍候 {duration} 秒...")
        time.sleep(duration)
        
        # 停止所有线程
        self.stop_flag = True
        
        for t in threads:
            t.join(timeout=2)
        
        # 统计结果
        self.print_results()
        
        # 保存结果到 CSV
        self.save_results_to_csv()
    
    def print_results(self):
        """打印测试结果"""
        if not self.results:
            print("❌ 没有测试结果")
            return
        
        total_requests = len(self.results)
        success_requests = sum(1 for r in self.results if r['success'])
        failed_requests = total_requests - success_requests
        success_rate = (success_requests / total_requests * 100) if total_requests > 0 else 0
        
        elapsed_times = [r['elapsed'] for r in self.results if r['elapsed'] > 0]
        
        if elapsed_times:
            avg_time = sum(elapsed_times) / len(elapsed_times)
            min_time = min(elapsed_times)
            max_time = max(elapsed_times)
            
            # 计算中位数
            sorted_times = sorted(elapsed_times)
            median_time = sorted_times[len(sorted_times) // 2]
            
            # 计算 P95
            p95_index = int(len(sorted_times) * 0.95)
            p95_time = sorted_times[p95_index] if p95_index < len(sorted_times) else max_time
        else:
            avg_time = min_time = max_time = median_time = p95_time = 0
        
        # 计算 QPS
        test_duration = max(r['elapsed'] for r in self.results) if self.results else 1
        qps = total_requests / test_duration if test_duration > 0 else 0
        
        print("\n" + "=" * 60)
        print("压力测试结果")
        print("=" * 60)
        print(f"总请求数：{total_requests}")
        print(f"成功请求：{success_requests}")
        print(f"失败请求：{failed_requests}")
        print(f"成功率：{success_rate:.2f}%")
        print(f"总耗时：{test_duration:.2f}秒")
        print(f"QPS (每秒请求数): {qps:.2f}")
        print("\n响应时间统计:")
        print(f"  平均：{avg_time*1000:.2f}ms")
        print(f"  中位数：{median_time*1000:.2f}ms")
        print(f"  最小：{min_time*1000:.2f}ms")
        print(f"  最大：{max_time*1000:.2f}ms")
        print(f"  95 百分位：{p95_time*1000:.2f}ms")
        print("=" * 60)
    
    def save_results_to_csv(self):
        """保存结果到 CSV 文件"""
        if not self.results:
            return
        
        filename = f"stress_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['worker_id', 'success', 'elapsed', 'status_code', 'auth_method', 'timestamp', 'error'])
            writer.writeheader()
            
            for result in self.results:
                writer.writerow({
                    'worker_id': result.get('worker_id'),
                    'success': result.get('success'),
                    'elapsed': result.get('elapsed'),
                    'status_code': result.get('status_code'),
                    'auth_method': result.get('auth_method'),
                    'timestamp': result.get('timestamp'),
                    'error': result.get('error', '')
                })
        
        print(f"\n测试结果已保存到：{filename}")


def main():
    parser = argparse.ArgumentParser(description='JMeter 风格压力测试工具')
    parser.add_argument('--url', default='http://localhost:5000', help='服务器地址')
    parser.add_argument('--duration', type=int, default=60, help='测试持续时间（秒）')
    parser.add_argument('--users', type=int, default=10, help='并发用户数')
    parser.add_argument('--username', help='用户名（JWT 认证模式）')
    parser.add_argument('--password', help='密码（JWT 认证模式）')
    parser.add_argument('--apikey', help='API Key（API Key 认证模式）')
    parser.add_argument('--type', choices=['normal', 'encrypted', 'apikey'], default='normal', help='测试类型')
    
    args = parser.parse_args()
    
    # 创建测试器
    tester = JMETERTester(
        base_url=args.url,
        username=args.username,
        password=args.password,
        api_key=args.apikey
    )
    
    # 运行测试
    tester.run_test(
        duration=args.duration,
        num_users=args.users,
        test_type=args.type
    )


if __name__ == '__main__':
    main()
