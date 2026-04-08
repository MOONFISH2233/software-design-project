"""
多机分布式压力测试脚本
功能：支持从配置文件读取测试参数，在多台电脑上同时运行压力测试
版本：v2.0 - 增强版
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, List

# 测试配置
SERVER_URL = "http://localhost:5000"
TEST_DURATION = 120  # 测试持续时间（秒）
CONCURRENT_USERS = 10  # 每台电脑的并发用户数

# 三台电脑的测试配置
MACHINE_CONFIGS = [
    {
        "machine_id": 1,
        "ip": "192.168.1.101",  # 修改为实际IP
        "username": "user1",
        "password": "user123",
        "concurrent_users": 10
    },
    {
        "machine_id": 2,
        "ip": "192.168.1.102",  # 修改为实际IP
        "username": "user2",
        "password": "user123",
        "concurrent_users": 10
    },
    {
        "machine_id": 3,
        "ip": "192.168.1.103",  # 修改为实际IP
        "username": "user3",
        "password": "user123",
        "concurrent_users": 10
    }
]


def generate_test_config():
    """生成测试配置文件"""
    config = {
        "server_url": SERVER_URL,
        "test_duration": TEST_DURATION,
        "machines": MACHINE_CONFIGS,
        "created_at": datetime.now().isoformat()
    }
    
    with open("multi_pc_test_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("✅ 已生成测试配置文件：multi_pc_test_config.json")
    return config


def print_test_instructions(config: Dict):
    """打印测试说明"""
    print("\n" + "=" * 80)
    print("多机分布式压力测试说明")
    print("=" * 80)
    print(f"\n服务器地址：{config['server_url']}")
    print(f"测试持续时间：{config['test_duration']}秒")
    print(f"参与电脑数量：{len(config['machines'])}台")
    print(f"总并发用户数：{sum(m['concurrent_users'] for m in config['machines'])}")
    
    print("\n" + "-" * 80)
    print("各电脑测试配置：")
    print("-" * 80)
    
    for machine in config['machines']:
        print(f"\n电脑 {machine['machine_id']}:")
        print(f"  IP地址：{machine['ip']}")
        print(f"  用户名：{machine['username']}")
        print(f"  并发数：{machine['concurrent_users']}")
        print(f"  测试命令：")
        print(f"    python jmeter_test.py \\")
        print(f"      --url {config['server_url']} \\")
        print(f"      --duration {config['test_duration']} \\")
        print(f"      --users {machine['concurrent_users']} \\")
        print(f"      --username {machine['username']} \\")
        print(f"      --password {machine['password']} \\")
        print(f"      --type encrypted")
    
    print("\n" + "=" * 80)
    print("执行步骤：")
    print("=" * 80)
    print("1. 确保服务器已启动：python app.py")
    print("2. 在三台电脑上安装依赖：pip install requests")
    print("3. 将 jmeter_test.py 复制到三台电脑")
    print("4. 在三台电脑上同时执行上述测试命令")
    print("5. 等待测试完成，查看结果")
    print("=" * 80 + "\n")


def generate_batch_script():
    """生成批量执行脚本（Windows）"""
    script_content = """@echo off
echo ==========================================
echo 多机压力测试 - 批量执行脚本
echo ==========================================
echo.

echo [1/3] 在电脑1上启动测试...
start "测试电脑1" cmd /k "python jmeter_test.py --url %SERVER_URL% --duration %DURATION% --users 10 --username user1 --password user123 --type encrypted"
timeout /t 2 >nul

echo [2/3] 在电脑2上启动测试...
start "测试电脑2" cmd /k "python jmeter_test.py --url %SERVER_URL% --duration %DURATION% --users 10 --username user2 --password user123 --type encrypted"
timeout /t 2 >nul

echo [3/3] 在电脑3上启动测试...
start "测试电脑3" cmd /k "python jmeter_test.py --url %SERVER_URL% --duration %DURATION% --users 10 --username user3 --password user123 --type encrypted"

echo.
echo 所有测试已启动！
echo 请等待测试完成...
echo.
pause
"""
    
    with open("run_multi_pc_test.bat", "w", encoding="utf-8") as f:
        f.write(script_content)
    
    print("✅ 已生成批量执行脚本：run_multi_pc_test.bat")


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("多机分布式压力测试配置生成器")
    print("=" * 80 + "\n")
    
    # 生成配置文件
    config = generate_test_config()
    
    # 打印测试说明
    print_test_instructions(config)
    
    # 生成批量执行脚本
    generate_batch_script()
    
    print("\n📝 提示：")
    print("  - 请修改 multi_pc_test_config.json 中的IP地址为实际地址")
    print("  - 确保三台电脑在同一局域网内")
    print("  - 确保服务器防火墙允许5000端口访问")
    print("  - 测试完成后查看 stress_test_results.csv 文件\n")


if __name__ == "__main__":
    main()
