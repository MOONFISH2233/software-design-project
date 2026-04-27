#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MySQL 8.0 升级自动化脚本
通过SSH连接到服务器并执行MySQL版本升级
"""

import subprocess
import sys
import time


def run_ssh_command(command, password="@Dierzu999"):
    """
    通过SSH执行远程命令
    """
    ssh_cmd = f'ssh root@47.103.108.47 "{command}"'
    
    try:
        result = subprocess.run(
            ssh_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)


def check_mysql_version():
    """检查当前MySQL版本"""
    print("=" * 60)
    print("检查当前MySQL版本...")
    print("=" * 60)
    
    returncode, stdout, stderr = run_ssh_command("mysql --version")
    
    if returncode == 0:
        print(f"当前版本: {stdout.strip()}")
        return stdout.strip()
    else:
        print(f"错误: {stderr}")
        return None


def check_baota_status():
    """检查宝塔面板状态"""
    print("\n" + "=" * 60)
    print("检查宝塔面板状态...")
    print("=" * 60)
    
    returncode, stdout, stderr = run_ssh_command("bt default")
    
    if returncode == 0:
        print("宝塔面板正在运行")
        print(stdout)
        return True
    else:
        print(f"错误: {stderr}")
        return False


def backup_mysql_data():
    """备份MySQL数据"""
    print("\n" + "=" * 60)
    print("备份MySQL数据...")
    print("=" * 60)
    
    backup_cmd = """
    mkdir -p /root/mysql_backup && \
    mysqldump --all-databases > /root/mysql_backup/all_databases_$(date +%Y%m%d_%H%M%S).sql && \
    echo "备份完成" || echo "备份失败"
    """
    
    returncode, stdout, stderr = run_ssh_command(backup_cmd)
    
    if returncode == 0:
        print("✓ 数据备份成功")
        print(stdout)
        return True
    else:
        print("✗ 数据备份失败")
        print(stderr)
        return False


def upgrade_mysql_via_cli():
    """
    尝试通过命令行升级MySQL (高级方法)
    注意: 此方法有风险,建议优先使用宝塔面板
    """
    print("\n" + "=" * 60)
    print("警告: 命令行升级存在风险!")
    print("=" * 60)
    print("\n推荐做法:")
    print("1. 访问宝塔面板: https://47.103.108.47:8888/90a1c9ff")
    print("2. 用户名: f151c119")
    print("3. 密码: 196f5df06612")
    print("4. 左侧菜单 → 数据库 → MySQL管理 → 设置 → 切换版本 → 选择8.0.x")
    print("\n是否继续命令行升级? (y/n): ", end="")
    
    choice = input().strip().lower()
    if choice != 'y':
        print("已取消升级操作")
        return False
    
    print("\n开始升级流程...")
    
    # 步骤1: 停止MySQL服务
    print("\n[1/5] 停止MySQL服务...")
    run_ssh_command("systemctl stop mysqld")
    time.sleep(2)
    
    # 步骤2: 备份配置文件
    print("[2/5] 备份配置文件...")
    run_ssh_command("cp /etc/my.cnf /etc/my.cnf.backup.$(date +%Y%m%d)")
    
    # 步骤3: 卸载旧版本
    print("[3/5] 卸载MySQL 5.7...")
    run_ssh_command("yum remove -y mysql-community-server mysql-community-client")
    
    # 步骤4: 安装MySQL 8.0
    print("[4/5] 安装MySQL 8.0...")
    install_commands = """
    yum install -y https://dev.mysql.com/get/mysql80-community-release-el7-3.noarch.rpm && \
    yum-config-manager --disable mysql57-community && \
    yum-config-manager --enable mysql80-community && \
    yum install -y mysql-community-server
    """
    returncode, stdout, stderr = run_ssh_command(install_commands)
    
    if returncode != 0:
        print(f"安装失败: {stderr}")
        return False
    
    # 步骤5: 启动新版本
    print("[5/5] 启动MySQL 8.0...")
    run_ssh_command("systemctl start mysqld")
    time.sleep(5)
    
    # 验证升级
    verify_upgrade()
    
    return True


def verify_upgrade():
    """验证MySQL升级结果"""
    print("\n" + "=" * 60)
    print("验证MySQL升级结果...")
    print("=" * 60)
    
    returncode, stdout, stderr = run_ssh_command("mysql --version")
    
    if returncode == 0:
        version_info = stdout.strip()
        print(f"✓ 当前版本: {version_info}")
        
        if "8.0" in version_info:
            print("✓ MySQL已成功升级到8.0!")
            
            # 检查服务状态
            run_ssh_command("systemctl status mysqld | head -10")
            
            return True
        else:
            print("✗ MySQL版本未更新到8.0")
            return False
    else:
        print(f"✗ 无法获取MySQL版本: {stderr}")
        return False


def show_manual_guide():
    """显示手动升级指南"""
    print("\n" + "=" * 60)
    print("📋 手动升级指南 (推荐)")
    print("=" * 60)
    print("""
步骤1: 登录宝塔面板
   - 浏览器访问: https://47.103.108.47:8888/90a1c9ff
   - 用户名: f151c119
   - 密码: 196f5df06612

步骤2: 进入MySQL管理
   - 左侧菜单点击"数据库"
   - 找到"MySQL管理器"或"MySQL 5.7"
   - 点击"设置"按钮

步骤3: 切换版本
   - 在设置页面找到"切换版本"选项
   - 选择"MySQL 8.0.x" (推荐8.0.26或更高)
   - 点击"确定"开始升级

步骤4: 等待升级完成
   - 升级过程需要10-20分钟
   - 期间MySQL服务会重启
   - 请勿关闭浏览器或刷新页面

步骤5: 验证升级
   - 升级完成后,在终端执行:
     ssh root@47.103.108.47 "mysql --version"
   - 应该显示: mysql Ver 8.0.x ...

⚠️  注意事项:
   - 升级前会自动备份数据
   - 升级期间应用会短暂不可用
   - 升级后需测试应用兼容性
   - 如有问题可查看日志: /www/server/data/*.err
""")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("MySQL 8.0 升级工具")
    print("=" * 60)
    print("\n请选择操作:")
    print("1. 检查当前MySQL版本")
    print("2. 备份MySQL数据")
    print("3. 查看手动升级指南 (推荐)")
    print("4. 尝试自动升级 (高级,有风险)")
    print("5. 验证MySQL版本")
    print("0. 退出")
    print()
    
    choice = input("请输入选项 (0-5): ").strip()
    
    if choice == '1':
        check_mysql_version()
    elif choice == '2':
        backup_mysql_data()
    elif choice == '3':
        show_manual_guide()
    elif choice == '4':
        upgrade_mysql_via_cli()
    elif choice == '5':
        verify_upgrade()
    elif choice == '0':
        print("再见!")
        sys.exit(0)
    else:
        print("无效选项")
        sys.exit(1)


if __name__ == "__main__":
    main()
