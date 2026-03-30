"""
自动化压力测试 - 一键启动服务器并测试
"""

import subprocess
import time
import requests
import sys
import os


def wait_for_server(url, timeout=30):
    """等待服务器启动"""
    print(f"等待服务器启动：{url}")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{url}/api/health", timeout=2)
            if response.status_code == 200:
                print(f"✅ 服务器已就绪！")
                return True
        except:
            pass
        
        time.sleep(1)
        print(".", end="", flush=True)
    
    print("\n❌ 服务器启动超时")
    return False


def run_load_test():
    """运行完整的压力测试流程"""
    base_url = "http://localhost:5000"
    server_process = None
    
    try:
        # 检查服务器是否已在运行
        try:
            response = requests.get(f"{base_url}/api/health", timeout=2)
            if response.status_code == 200:
                print("✅ 检测到服务器已在运行\n")
                server_running = True
            else:
                server_running = False
        except:
            server_running = False
        
        # 如果服务器未运行，启动它
        if not server_running:
            print("="*60)
            print("启动 Flask 服务器...")
            print("="*60)
            
            # 启动服务器进程
            server_process = subprocess.Popen(
                [sys.executable, 'app.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # 等待服务器启动
            if not wait_for_server(base_url):
                print("\n无法启动服务器，请检查 app.py 是否有错误")
                if server_process:
                    server_process.terminate()
                return
        
        # 导入并运行压力测试
        print("\n" + "="*60)
        print("开始压力测试")
        print("="*60)
        
        from load_test import LoadTester
        
        # 测试场景 1: 健康检查接口
        print("\n\n📋 测试场景 1: 健康检查接口 (轻量级)")
        print("-"*60)
        tester = LoadTester(base_url)
        tester.run_test(total_requests=500, concurrent_users=30)
        
        time.sleep(2)
        
        # 测试场景 2: 数据接收接口
        print("\n\n📋 测试场景 2: 数据接收接口 (标准)")
        print("-"*60)
        tester = LoadTester(base_url)
        tester.run_test(total_requests=1000, concurrent_users=50)
        
        # 获取服务器统计信息
        try:
            response = requests.get(f"{base_url}/api/stats", timeout=5)
            if response.status_code == 200:
                print("\n\n" + "="*60)
                print("服务器统计信息")
                print("="*60)
                stats = response.json()
                print(f"总请求数：{stats.get('total_requests', 'N/A')}")
                print(f"版本：{stats.get('version', 'N/A')}")
                print(f"功能特性：{', '.join(stats.get('features', []))}")
        except Exception as e:
            print(f"\n无法获取统计信息：{e}")
        
        print("\n\n" + "="*60)
        print("✅ 压力测试完成！")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断测试")
    except Exception as e:
        print(f"\n❌ 测试过程中出错：{e}")
        import traceback
        traceback.print_exc()
    finally:
        # 如果是我们启动的服务器，询问是否关闭
        if server_process and not server_running:
            print("\n是否关闭 Flask 服务器？(y/n)")
            try:
                choice = input().strip().lower()
                if choice == 'y':
                    server_process.terminate()
                    print("服务器已关闭")
            except:
                server_process.terminate()


if __name__ == '__main__':
    run_load_test()
