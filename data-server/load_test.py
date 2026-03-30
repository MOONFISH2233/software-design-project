"""
压力测试脚本 - 测试 Flask 应用的高并发性能
用于验证异步日志系统的性能表现
"""

import requests
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from statistics import mean, median, percentile
import json


class LoadTester:
    """压力测试器"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.results = []
        self.success_count = 0
        self.failure_count = 0
        self.lock = threading.Lock()
    
    def send_request(self, request_id):
        """发送单个请求"""
        start_time = time.time()
        
        try:
            # 测试数据接收接口
            payload = {
                'test_id': request_id,
                'data': f'Test data {request_id}' * 10,
                'timestamp': time.time()
            }
            
            response = requests.post(
                f'{self.base_url}/api/receive',
                json=payload,
                timeout=10
            )
            
            end_time = time.time()
            duration = (end_time - start_time) * 1000  # 转换为毫秒
            
            with self.lock:
                if response.status_code == 200:
                    self.success_count += 1
                else:
                    self.failure_count += 1
                
                self.results.append({
                    'request_id': request_id,
                    'status_code': response.status_code,
                    'duration_ms': duration,
                    'success': response.status_code == 200
                })
            
            return {
                'success': response.status_code == 200,
                'duration_ms': duration
            }
        
        except Exception as e:
            end_time = time.time()
            duration = (end_time - start_time) * 1000
            
            with self.lock:
                self.failure_count += 1
                self.results.append({
                    'request_id': request_id,
                    'status_code': 0,
                    'duration_ms': duration,
                    'success': False,
                    'error': str(e)
                })
            
            return {
                'success': False,
                'duration_ms': duration,
                'error': str(e)
            }
    
    def run_test(self, total_requests=1000, concurrent_users=50):
        """
        运行压力测试
        
        :param total_requests: 总请求数
        :param concurrent_users: 并发用户数（线程数）
        """
        print(f"\n{'='*60}")
        print(f"开始压力测试")
        print(f"{'='*60}")
        print(f"目标地址：{self.base_url}")
        print(f"总请求数：{total_requests}")
        print(f"并发用户数：{concurrent_users}")
        print(f"{'='*60}\n")
        
        start_time = time.time()
        
        # 使用线程池执行并发请求
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(self.send_request, i) for i in range(total_requests)]
            
            # 显示进度
            completed = 0
            for future in as_completed(futures):
                completed += 1
                if completed % 100 == 0:
                    print(f"进度：{completed}/{total_requests} ({completed/total_requests*100:.1f}%)")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 分析结果
        self.analyze_results(total_time)
    
    def analyze_results(self, total_time):
        """分析测试结果"""
        print(f"\n{'='*60}")
        print(f"测试结果分析")
        print(f"{'='*60}")
        
        # 基础统计
        success_rate = (self.success_count / len(self.results)) * 100 if self.results else 0
        qps = len(self.results) / total_time
        
        print(f"\n📊 基础指标:")
        print(f"  总请求数：{len(self.results)}")
        print(f"  成功请求：{self.success_count}")
        print(f"  失败请求：{self.failure_count}")
        print(f"  成功率：{success_rate:.2f}%")
        print(f"  总耗时：{total_time:.2f} 秒")
        print(f"  QPS: {qps:.2f} 请求/秒")
        
        # 响应时间统计
        durations = [r['duration_ms'] for r in self.results if r['success']]
        
        if durations:
            avg_duration = mean(durations)
            median_duration = median(durations)
            min_duration = min(durations)
            max_duration = max(durations)
            p95_duration = percentile(durations, 95) if hasattr(__builtins__, 'percentile') else sorted(durations)[int(len(durations)*0.95)]
            p99_duration = percentile(durations, 99) if hasattr(__builtins__, 'percentile') else sorted(durations)[int(len(durations)*0.99)]
            
            print(f"\n⏱️ 响应时间统计 (毫秒):")
            print(f"  平均值：{avg_duration:.2f} ms")
            print(f"  中位数：{median_duration:.2f} ms")
            print(f"  最小值：{min_duration:.2f} ms")
            print(f"  最大值：{max_duration:.2f} ms")
            print(f"  P95: {p95_duration:.2f} ms")
            print(f"  P99: {p99_duration:.2f} ms")
            
            # 性能评估
            print(f"\n🎯 性能评估:")
            if avg_duration < 50:
                print(f"  ✅ 平均响应时间优秀 (<50ms)")
            elif avg_duration < 100:
                print(f"  ✅ 平均响应时间良好 (<100ms)")
            elif avg_duration < 200:
                print(f"  ⚠️ 平均响应时间一般 (<200ms)")
            else:
                print(f"  ❌ 平均响应时间较差 (>200ms)")
            
            if p95_duration < 200:
                print(f"  ✅ P95 延迟优秀 (<200ms)")
            elif p95_duration < 500:
                print(f"  ✅ P95 延迟良好 (<500ms)")
            else:
                print(f"  ⚠️ P95 延迟需要优化 (>500ms)")
        
        # 慢请求分析
        slow_requests = [r for r in self.results if r['duration_ms'] > 100]
        if slow_requests:
            print(f"\n🐢 慢请求分析 (>100ms):")
            print(f"  慢请求数量：{len(slow_requests)}")
            print(f"  占比：{len(slow_requests)/len(self.results)*100:.2f}%")
        
        # 错误分析
        errors = [r for r in self.results if not r['success']]
        if errors:
            print(f"\n❌ 错误分析:")
            print(f"  错误数量：{len(errors)}")
            error_types = {}
            for error in errors:
                error_type = error.get('error', f"HTTP {error['status_code']}")
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            for error_type, count in error_types.items():
                print(f"  - {error_type}: {count} 次")
        
        print(f"\n{'='*60}\n")
        
        # 生成报告
        self.generate_report(total_time, qps, avg_duration if durations else 0, success_rate)
    
    def generate_report(self, total_time, qps, avg_duration, success_rate):
        """生成测试报告并保存到文件"""
        report = {
            'test_info': {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'base_url': self.base_url,
                'total_requests': len(self.results),
                'concurrent_users': 50,
                'total_time_seconds': round(total_time, 2)
            },
            'metrics': {
                'qps': round(qps, 2),
                'success_rate_percent': round(success_rate, 2),
                'avg_response_time_ms': round(avg_duration, 2),
                'success_count': self.success_count,
                'failure_count': self.failure_count
            },
            'version': '2.0.0'
        }
        
        # 保存报告
        report_filename = f'load_test_report_{time.strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📄 测试报告已保存到：{report_filename}")


def test_health_endpoint():
    """测试健康检查接口（轻量级）"""
    print("\n测试健康检查接口...")
    tester = LoadTester()
    tester.run_test(total_requests=500, concurrent_users=30)


def test_receive_endpoint():
    """测试数据接收接口（重量级）"""
    print("\n测试数据接收接口...")
    tester = LoadTester()
    tester.run_test(total_requests=1000, concurrent_users=50)


if __name__ == '__main__':
    print("Flask 应用压力测试工具 v1.0")
    print("="*60)
    
    # 选择测试模式
    print("\n请选择测试模式:")
    print("1. 轻量级测试（健康检查接口，500 请求/30 并发）")
    print("2. 标准测试（数据接收接口，1000 请求/50 并发）")
    print("3. 自定义测试")
    
    choice = input("\n请输入选项 (1/2/3): ").strip()
    
    if choice == '1':
        test_health_endpoint()
    elif choice == '2':
        test_receive_endpoint()
    elif choice == '3':
        total = int(input("总请求数 (默认 1000): ") or "1000")
        concurrent = int(input("并发用户数 (默认 50): ") or "50")
        tester = LoadTester()
        tester.run_test(total_requests=total, concurrent_users=concurrent)
    else:
        print("无效选项，使用默认测试")
        test_receive_endpoint()
