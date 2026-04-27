#!/usr/bin/env python3
"""
项目文件整理脚本
用途：将 data-server 目录的文件按功能分类整理到标准目录结构中
"""

import os
import shutil
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# 文件分类规则
FILE_CATEGORIES = {
    # 文档文件 -> docs/
    'docs': [
        '*.md',
        '任务完成总结.html',
    ],
    
    # 脚本文件 -> scripts/
    'scripts': [
        '*.bat',
        '*.ps1',
        '*.sh',
        'deploy*.py',
        'upload*.ps1',
    ],
    
    # 测试文件 -> tests/
    'tests': [
        '*test*.py',
        '*verify*.py',
        '*check*.py',
        '*demo.py',
        '*_test.*',
        'acceptance_*',
        'stress_test_results_*.csv',
    ],
    
    # 配置文件 -> config/
    'config': [
        'gunicorn_config.py',
        '*.service',
        'Jenkinsfile',
        'requirements.txt',
        'postman_collection.json',
        'swagger.json',
    ],
    
    # 备份和临时文件 -> backups/
    'backups': [
        '*.save',
        'temp_*.py',
        '*_fix.py',
        'app_fix.py',
    ],
    
    # 示例文件 -> examples/
    'examples': [
        'simulator*.py',
        'cloud_to_cloud.py',
        'local_to_cloud.py',
        'multi_pc_test*.py',
        '*.csv',
        '*.txt',
    ],
}

# 特殊文件处理（保留在根目录）
ROOT_FILES = [
    'app.py',
    'README.md',
    '.gitignore',
    'security_enhanced.py',
    'module_*.py',
    'mq_utils.py',
]

def should_keep_in_root(filename):
    """判断文件是否应该保留在根目录"""
    # 核心应用文件
    core_files = ['app.py', 'security_enhanced.py']
    if filename in core_files:
        return True
    
    # 模块文件
    if filename.startswith('module_') or filename == 'mq_utils.py':
        return True
    
    # README 文件
    if filename.startswith('README'):
        return True
    
    # Git 相关文件
    if filename.startswith('.git'):
        return True
    
    return False

def move_file(src, dst_dir):
    """移动文件，如果目标已存在则跳过"""
    dst = dst_dir / src.name
    if dst.exists():
        print(f"  ⚠️  跳过 (已存在): {src.name}")
        return False
    
    try:
        shutil.move(str(src), str(dst))
        print(f"  ✅ 移动: {src.name} -> {dst_dir.name}/")
        return True
    except Exception as e:
        print(f"  ❌ 失败: {src.name} - {e}")
        return False

def organize_files():
    """执行文件整理"""
    print("=" * 70)
    print("📁 开始整理项目文件结构")
    print("=" * 70)
    print()
    
    moved_count = 0
    skipped_count = 0
    
    # 遍历所有文件和目录
    for item in PROJECT_ROOT.iterdir():
        # 跳过目录（除了我们要整理的）
        if item.is_dir():
            if item.name in ['docs', 'scripts', 'tests', 'config', 'backups', 'examples', 
                           'data', 'logs', 'security', '__pycache__', '.git']:
                continue
            print(f"⚠️  跳过目录: {item.name}/")
            continue
        
        # 跳过隐藏文件
        if item.name.startswith('.'):
            continue
        
        # 检查是否应该保留在根目录
        if should_keep_in_root(item.name):
            print(f"✓  保留: {item.name}")
            continue
        
        # 根据文件名匹配目标目录
        target_dir = None
        filename = item.name
        
        # 检查每个分类
        for category, patterns in FILE_CATEGORIES.items():
            for pattern in patterns:
                # 简单模式匹配
                if pattern.startswith('*'):
                    # 通配符匹配
                    suffix = pattern[1:]  # 去掉 *
                    if filename.endswith(suffix):
                        target_dir = PROJECT_ROOT / category
                        break
                    # 前缀匹配
                    if pattern.endswith('*'):
                        prefix = pattern[:-1]
                        if filename.startswith(prefix):
                            target_dir = PROJECT_ROOT / category
                            break
                else:
                    # 精确匹配或 glob 模式
                    from fnmatch import fnmatch
                    if fnmatch(filename, pattern):
                        target_dir = PROJECT_ROOT / category
                        break
            
            if target_dir:
                break
        
        # 移动文件
        if target_dir:
            if move_file(item, target_dir):
                moved_count += 1
            else:
                skipped_count += 1
        else:
            print(f"❓ 未分类: {item.name}")
    
    print()
    print("=" * 70)
    print(f"✅ 整理完成！")
    print(f"   - 移动文件: {moved_count} 个")
    print(f"   - 跳过文件: {skipped_count} 个")
    print("=" * 70)
    print()
    
    # 显示新的目录结构
    print("📂 新的目录结构:")
    print_directory_tree(PROJECT_ROOT, max_depth=2)

def print_directory_tree(path, prefix="", max_depth=3, current_depth=0):
    """打印目录树"""
    if current_depth > max_depth:
        return
    
    items = sorted([p for p in path.iterdir() if not p.name.startswith('.')])
    
    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        connector = "└── " if is_last else "├── "
        
        if item.is_dir():
            print(f"{prefix}{connector}📁 {item.name}/")
            extension = "    " if is_last else "│   "
            print_directory_tree(item, prefix + extension, max_depth, current_depth + 1)
        else:
            print(f"{prefix}{connector}📄 {item.name}")

if __name__ == "__main__":
    try:
        organize_files()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
