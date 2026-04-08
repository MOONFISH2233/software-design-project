"""
MQ 架构系统一键启动脚本
功能：同时启动所有 MQ 模块

使用方法：
    python start_all_modules.py                          # 默认连接远程服务器
    python start_all_modules.py --host 47.103.108.47     # 指定MQ地址
    python start_all_modules.py --host localhost         # 连接本地MQ
    python start_all_modules.py --no-simulator           # 只启动服务端模块
"""

import subprocess
import sys
import os
import time
import argparse
from datetime import datetime

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
    UNDERLINE = '\033[4m'


def print_banner():
    """打印横幅"""
    print(Colors.OKCYAN + "="*70)
    print(" " * 20 + "MQ 数据服务器系统启动")
    print("="*70 + Colors.ENDC)
    print(f"\n启动时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"工作目录：{os.getcwd()}\n")


def check_redis_connection(host='localhost', port=6379):
    """检查 Redis 连接"""
    print(Colors.OKBLUE + f"[1/6] 检查 Redis 连接 ({host}:{port})..." + Colors.ENDC)
    
    try:
        import redis
        r = redis.Redis(host=host, port=port, db=0, socket_connect_timeout=5)
        r.ping()
        print(Colors.OKGREEN + "      ✅ Redis 连接成功" + Colors.ENDC)
        return True
    except Exception as e:
        print(Colors.FAIL + f"      ❌ Redis 连接失败：{e}" + Colors.ENDC)
        print(Colors.WARNING + "      提示：请先启动 Redis 服务" + Colors.ENDC)
        print(Colors.WARNING + "      Docker 启动：docker run -d -p 6379:6379 redis:latest" + Colors.ENDC)
        return False


def start_module(module_name, process_list, env_vars=None):
    """启动单个模块"""
    try:
        env = os.environ.copy()
        if env_vars:
            env.update(env_vars)
        cmd = [sys.executable, module_name]
        process = subprocess.Popen(cmd, env=env)
        process_list.append((module_name, process))
        print(Colors.OKGREEN + f"      ✅ {module_name} 已启动 (PID: {process.pid})" + Colors.ENDC)
        return True
    except Exception as e:
        print(Colors.FAIL + f"      ❌ {module_name} 启动失败：{e}" + Colors.ENDC)
        return False


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='MQ架构系统一键启动')
    parser.add_argument('--host', default='47.103.108.47',
                        help='MQ服务器地址（默认: 47.103.108.47）')
    parser.add_argument('--port', type=int, default=6379,
                        help='MQ端口（默认: 6379）')
    parser.add_argument('--no-simulator', action='store_true',
                        help='只启动服务端模块，不启动模拟器')
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()
    
    print_banner()
    print(f"MQ服务器：{args.host}:{args.port}")
    print(f"模拟器：{'禁用' if args.no_simulator else '启用'}\n")
    
    # 检查 Redis
    if not check_redis_connection(args.host, args.port):
        print(Colors.FAIL + "\n❌ 启动失败，请先确保 Redis 服务运行" + Colors.ENDC)
        sys.exit(1)
    
    # 将MQ配置传给子进程（通过环境变量）
    env_vars = {
        'MQ_HOST': args.host,
        'MQ_PORT': str(args.port)
    }
    
    process_list = []
    
    # 启动各个服务端模块
    print(Colors.OKBLUE + "\n[2/6] 启动数据接收模块..." + Colors.ENDC)
    start_module('module_receiver.py', process_list, env_vars)
    time.sleep(0.5)
    
    print(Colors.OKBLUE + "[3/6] 启动数据验证模块..." + Colors.ENDC)
    start_module('module_validator.py', process_list, env_vars)
    time.sleep(0.5)
    
    print(Colors.OKBLUE + "[4/6] 启动数据写入模块..." + Colors.ENDC)
    start_module('module_writer.py', process_list, env_vars)
    time.sleep(0.5)
    
    print(Colors.OKBLUE + "[5/6] 启动日志记录模块..." + Colors.ENDC)
    start_module('module_logger.py', process_list, env_vars)
    time.sleep(0.5)
    
    if not args.no_simulator:
        print(Colors.OKBLUE + "[6/6] 启动模拟器客户端..." + Colors.ENDC)
        start_module('simulator_mq.py', process_list, env_vars)
        time.sleep(1)
    else:
        print(Colors.WARNING + "[6/6] 跳过模拟器（--no-simulator）" + Colors.ENDC)
    
    # 打印启动摘要
    print("\n" + Colors.OKGREEN + "="*70)
    print(" " * 25 + "系统启动完成")
    print("="*70 + Colors.ENDC)
    
    print(f"\n📊 已启动 {len(process_list)} 个模块:")
    for module_name, process in process_list:
        if process.poll() is None:  # 仍在运行
            print(f"   ✅ {module_name} (PID: {process.pid})")
        else:
            print(f"   ❌ {module_name} (已退出)")
    
    print("\n" + Colors.WARNING + "💡 提示:" + Colors.ENDC)
    print("   - 按 Ctrl+C 可以停止所有模块")
    print("   - 查看日志：tail -f logs/*.log  (Linux/Mac)")
    print("   - 查看日志：Get-Content logs\\*.log -Wait  (PowerShell)")
    print(f"   - 监控 MQ: redis-cli -h {args.host} -p {args.port}")
    print("   - 启动多个写入模块：python module_writer.py  (新开终端)")
    print()
    
    # 等待用户中断
    try:
        while True:
            time.sleep(1)
            
            # 检查是否有进程异常退出
            for module_name, process in process_list:
                if process.poll() is not None:
                    print(Colors.WARNING + f"\n⚠️  {module_name} 已退出 (PID: {process.pid})" + Colors.ENDC)
                    
    except KeyboardInterrupt:
        print("\n\n" + Colors.WARNING + "🛑 正在停止所有模块..." + Colors.ENDC)
        
        # 终止所有进程
        for module_name, process in process_list:
            if process.poll() is None:
                process.terminate()
                print(Colors.OKGREEN + f"      ✅ {module_name} 已停止" + Colors.ENDC)
        
        print(Colors.OKCYAN + "\n✅ 所有模块已安全停止\n" + Colors.ENDC)


if __name__ == '__main__':
    main()
