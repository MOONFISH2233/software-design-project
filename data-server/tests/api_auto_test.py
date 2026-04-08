"""
API 接口自动化测试脚本
功能：逐个测试所有 API 接口，并生成测试报告
"""

import requests
import json
from datetime import datetime
import sys

class APITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.test_results = []
        self.session = requests.Session()
    
    def test_receive_data(self):
        """测试数据接收接口"""
        print("\n" + "="*60)
        print("测试 1: 数据接收接口 POST /api/receive")
        print("="*60)
        
        test_cases = [
            {
                "name": "皮肤传感器数据",
                "data": {
                    "data": {
                        "sensor_type": "skin",
                        "moisture": 65,
                        "oiliness": 35,
                        "device_id": "sensor_001"
                    },
                    "description": "皮肤传感器数据",
                    "source": "local"
                }
            },
            {
                "name": "环境传感器数据",
                "data": {
                    "data": {
                        "sensor_type": "environment",
                        "humidity": 55,
                        "light_lux": 650,
                        "temperature": 25.5,
                        "device_id": "env_sensor_001"
                    },
                    "description": "环境传感器数据",
                    "source": "local"
                }
            }
        ]
        
        for case in test_cases:
            try:
                response = self.session.post(
                    f'{self.base_url}/api/receive',
                    json=case['data'],
                    timeout=10
                )
                
                result = {
                    'test_name': f"数据接收 - {case['name']}",
                    'status_code': response.status_code,
                    'success': response.status_code == 200,
                    'response_time_ms': round(response.elapsed.total_seconds() * 1000, 2),
                    'response': response.json() if response.status_code == 200 else None
                }
                
                self._print_result(result)
                self.test_results.append(result)
                
            except Exception as e:
                result = {
                    'test_name': f"数据接收 - {case['name']}",
                    'status_code': 0,
                    'success': False,
                    'error': str(e)
                }
                self._print_result(result)
                self.test_results.append(result)
    
    def test_health_check(self):
        """测试健康检查接口"""
        print("\n" + "="*60)
        print("测试 2: 健康检查接口 GET /api/health")
        print("="*60)
        
        try:
            response = self.session.get(f'{self.base_url}/api/health', timeout=10)
            
            result = {
                'test_name': '健康检查',
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response_time_ms': round(response.elapsed.total_seconds() * 1000, 2),
                'response': response.json()
            }
            
            self._print_result(result)
            self.test_results.append(result)
            
        except Exception as e:
            result = {
                'test_name': '健康检查',
                'status_code': 0,
                'success': False,
                'error': str(e)
            }
            self._print_result(result)
            self.test_results.append(result)
    
    def test_get_logs(self):
        """测试日志查询接口"""
        print("\n" + "="*60)
        print("测试 3: 日志查询接口 GET /api/logs")
        print("="*60)
        
        try:
            response = self.session.get(f'{self.base_url}/api/logs', timeout=10)
            
            result = {
                'test_name': '日志查询',
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response_time_ms': round(response.elapsed.total_seconds() * 1000, 2),
                'response': response.json()
            }
            
            self._print_result(result)
            self.test_results.append(result)
            
        except Exception as e:
            result = {
                'test_name': '日志查询',
                'status_code': 0,
                'success': False,
                'error': str(e)
            }
            self._print_result(result)
            self.test_results.append(result)
    
    def test_get_stats(self):
        """测试统计信息接口"""
        print("\n" + "="*60)
        print("测试 4: 统计信息接口 GET /api/stats")
        print("="*60)
        
        try:
            response = self.session.get(f'{self.base_url}/api/stats', timeout=10)
            
            result = {
                'test_name': '统计信息',
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response_time_ms': round(response.elapsed.total_seconds() * 1000, 2),
                'response': response.json()
            }
            
            self._print_result(result)
            self.test_results.append(result)
            
        except Exception as e:
            result = {
                'test_name': '统计信息',
                'status_code': 0,
                'success': False,
                'error': str(e)
            }
            self._print_result(result)
            self.test_results.append(result)
    
    def _print_result(self, result):
        """打印测试结果"""
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"\n{status} | {result['test_name']}")
        
        if result.get('status_code'):
            print(f"   状态码：{result['status_code']}")
            print(f"   响应时间：{result['response_time_ms']}ms")
        
        if result.get('response'):
            print(f"   响应内容：{json.dumps(result['response'], indent=2, ensure_ascii=False)}")
        
        if result.get('error'):
            print(f"   错误信息：{result['error']}")
    
    def generate_report(self):
        """生成测试报告"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'success_rate': f"{success_rate:.2f}%",
                'test_time': datetime.now().isoformat(),
                'server_url': self.base_url
            },
            'results': self.test_results
        }
        
        # 保存报告到文件
        report_filename = f"api_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print("\n" + "="*60)
        print("📊 测试报告汇总")
        print("="*60)
        print(f"总测试数：{total_tests}")
        print(f"通过：{passed_tests} ✅")
        print(f"失败：{failed_tests} ❌")
        print(f"成功率：{success_rate:.2f}%")
        print(f"\n详细报告已保存到：{report_filename}")
        
        return report
    
    def test_skin_sensor_api(self):
        """测试皮肤传感器专用接口"""
        print("\n" + "="*60)
        print("测试 5: 皮肤传感器接口 POST /api/sensor/skin")
        print("="*60)
        
        test_cases = [
            {
                "name": "正常皮肤数据",
                "data": {"moisture": 65, "oiliness": 35, "device_id": "skin_001"},
                "expect_status": 200
            },
            {
                "name": "缺少必填字段（应返回400）",
                "data": {"device_id": "skin_001"},
                "expect_status": 400
            },
            {
                "name": "边界值测试（水分100%）",
                "data": {"moisture": 100, "oiliness": 0, "device_id": "skin_002"},
                "expect_status": 200
            }
        ]
        
        for case in test_cases:
            try:
                response = self.session.post(
                    f'{self.base_url}/api/sensor/skin',
                    json=case['data'],
                    timeout=10
                )
                success = response.status_code == case['expect_status']
                result = {
                    'test_name': f"皮肤传感器 - {case['name']}",
                    'status_code': response.status_code,
                    'success': success,
                    'response_time_ms': round(response.elapsed.total_seconds() * 1000, 2),
                    'response': response.json()
                }
            except Exception as e:
                result = {
                    'test_name': f"皮肤传感器 - {case['name']}",
                    'status_code': 0,
                    'success': False,
                    'error': str(e)
                }
            self._print_result(result)
            self.test_results.append(result)

    def test_environment_sensor_api(self):
        """测试环境传感器专用接口"""
        print("\n" + "="*60)
        print("测试 6: 环境传感器接口 POST /api/sensor/environment")
        print("="*60)
        
        test_cases = [
            {
                "name": "正常环境数据",
                "data": {"humidity": 55, "light_lux": 650, "temperature": 25.5, "device_id": "env_001"},
                "expect_status": 200
            },
            {
                "name": "缺少必填字段（应返回400）",
                "data": {"temperature": 25.0},
                "expect_status": 400
            },
            {
                "name": "边界值测试（湿度0%，光照0）",
                "data": {"humidity": 0, "light_lux": 0, "temperature": -20, "device_id": "env_002"},
                "expect_status": 200
            }
        ]
        
        for case in test_cases:
            try:
                response = self.session.post(
                    f'{self.base_url}/api/sensor/environment',
                    json=case['data'],
                    timeout=10
                )
                success = response.status_code == case['expect_status']
                result = {
                    'test_name': f"环境传感器 - {case['name']}",
                    'status_code': response.status_code,
                    'success': success,
                    'response_time_ms': round(response.elapsed.total_seconds() * 1000, 2),
                    'response': response.json()
                }
            except Exception as e:
                result = {
                    'test_name': f"环境传感器 - {case['name']}",
                    'status_code': 0,
                    'success': False,
                    'error': str(e)
                }
            self._print_result(result)
            self.test_results.append(result)

    def test_device_status_api(self):
        """测试设备状态专用接口"""
        print("\n" + "="*60)
        print("测试 7: 设备状态接口 POST /api/device/status")
        print("="*60)
        
        test_cases = [
            {
                "name": "设备在线",
                "data": {"device_id": "mirror_001", "status": "online", "battery": 85},
                "expect_status": 200
            },
            {
                "name": "设备运行中",
                "data": {"device_id": "mirror_001", "status": "running", "cpu_usage": 32},
                "expect_status": 200
            },
            {
                "name": "缺少必填字段（应返回400）",
                "data": {"battery": 50},
                "expect_status": 400
            }
        ]
        
        for case in test_cases:
            try:
                response = self.session.post(
                    f'{self.base_url}/api/device/status',
                    json=case['data'],
                    timeout=10
                )
                success = response.status_code == case['expect_status']
                result = {
                    'test_name': f"设备状态 - {case['name']}",
                    'status_code': response.status_code,
                    'success': success,
                    'response_time_ms': round(response.elapsed.total_seconds() * 1000, 2),
                    'response': response.json()
                }
            except Exception as e:
                result = {
                    'test_name': f"设备状态 - {case['name']}",
                    'status_code': 0,
                    'success': False,
                    'error': str(e)
                }
            self._print_result(result)
            self.test_results.append(result)

    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "="*60)
        print("🚀 Flask 数据服务器 API 自动化测试")
        print(f"服务器地址：{self.base_url}")
        print(f"测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # 先检查服务器是否可用
        try:
            response = self.session.get(f'{self.base_url}/api/health', timeout=5)
            if response.status_code != 200:
                print(f"⚠️  服务器返回异常状态码：{response.status_code}")
        except Exception as e:
            print(f"❌ 无法连接到服务器：{e}")
            print("请确保服务器正在运行！")
            return
        
        # 执行所有测试（含新增传感器接口）
        self.test_health_check()
        self.test_receive_data()
        self.test_get_stats()
        self.test_get_logs()
        self.test_skin_sensor_api()
        self.test_environment_sensor_api()
        self.test_device_status_api()
        
        # 生成报告
        self.generate_report()


def main():
    """主函数"""
    # 默认使用本地服务器地址
    default_url = "http://localhost:5000"
    
    # 如果有命令行参数，使用提供的 URL
    if len(sys.argv) > 1:
        server_url = sys.argv[1]
    else:
        server_url = default_url
    
    print(f"\n💡 提示：可以通过命令行参数指定服务器地址")
    print(f"   例如：python api_auto_test.py http://47.103.108.47:5000\n")
    
    tester = APITester(server_url)
    tester.run_all_tests()


if __name__ == '__main__':
    main()
