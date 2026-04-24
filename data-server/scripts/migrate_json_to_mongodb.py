#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据迁移脚本：将JSON文件导入MongoDB
功能：
1. 扫描指定目录下的所有JSON文件
2. 解析JSON数据并验证格式
3. 批量导入到MongoDB对应集合
4. 生成迁移报告
"""

import os
import sys
import json
import glob
from datetime import datetime
from pymongo import MongoClient, InsertOne
from typing import Dict, List, Any


class DataMigrator:
    """数据迁移器"""
    
    def __init__(self, mongo_uri='mongodb://localhost:27017/', db_name='sensor_data'):
        """初始化迁移器"""
        self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        self.db = self.client[db_name]
        self.stats = {
            'total_files': 0,
            'success_files': 0,
            'failed_files': 0,
            'total_records': 0,
            'skin_sensor': 0,
            'environment_sensor': 0,
            'device_status': 0,
            'errors': []
        }
        
    def detect_sensor_type(self, data: Dict) -> str:
        """根据数据内容检测传感器类型"""
        if 'moisture' in data or 'oiliness' in data:
            return 'skin_sensor'
        elif 'pm25' in data or 'co2' in data or 'humidity' in data:
            return 'environment_sensor'
        elif 'battery_level' in data or 'signal_strength' in data:
            return 'device_status'
        else:
            return 'unknown'
    
    def migrate_single_file(self, filepath: str) -> bool:
        """迁移单个JSON文件"""
        try:
            # 读取JSON文件
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 处理单条记录或数组
            if isinstance(data, list):
                records = data
            else:
                records = [data]
            
            # 按类型分组
            grouped_records = {
                'skin_sensor': [],
                'environment_sensor': [],
                'device_status': []
            }
            
            for record in records:
                sensor_type = self.detect_sensor_type(record)
                if sensor_type != 'unknown':
                    # 添加接收时间
                    if 'received_at' not in record:
                        record['received_at'] = datetime.utcnow()
                    grouped_records[sensor_type].append(record)
            
            # 批量插入到对应集合
            for collection_name, records in grouped_records.items():
                if records:
                    collection = self.db[collection_name]
                    operations = [InsertOne(record) for record in records]
                    result = collection.bulk_write(operations, ordered=False)
                    
                    count = len(records)
                    self.stats[collection_name] += count
                    self.stats['total_records'] += count
                    
                    print(f"   ✅ {collection_name}: 插入 {count} 条记录")
            
            self.stats['success_files'] += 1
            return True
            
        except Exception as e:
            self.stats['failed_files'] += 1
            error_msg = f"文件 {filepath} 迁移失败: {str(e)}"
            self.stats['errors'].append(error_msg)
            print(f"   ❌ {error_msg}")
            return False
    
    def migrate_directory(self, data_dir: str, pattern: str = '*.json'):
        """迁移整个目录的JSON文件"""
        print("="*70)
        print("  JSON数据迁移工具")
        print("="*70)
        print()
        
        # 查找所有JSON文件
        json_files = glob.glob(os.path.join(data_dir, '**', pattern), recursive=True)
        
        if not json_files:
            print(f"⚠️  在 {data_dir} 目录下未找到JSON文件")
            return
        
        self.stats['total_files'] = len(json_files)
        print(f"📁 找到 {len(json_files)} 个JSON文件")
        print(f"📂 数据目录: {data_dir}")
        print()
        
        # 逐个迁移
        for i, filepath in enumerate(json_files, 1):
            print(f"[{i}/{len(json_files)}] 处理: {os.path.basename(filepath)}")
            self.migrate_single_file(filepath)
        
        # 打印统计报告
        self.print_report()
    
    def print_report(self):
        """打印迁移报告"""
        print()
        print("="*70)
        print("  迁移完成报告")
        print("="*70)
        print()
        print(f"📊 统计信息:")
        print(f"   总文件数: {self.stats['total_files']}")
        print(f"   成功文件: {self.stats['success_files']} ✅")
        print(f"   失败文件: {self.stats['failed_files']} ❌")
        print(f"   总记录数: {self.stats['total_records']}")
        print()
        print(f"📈 各集合记录数:")
        print(f"   skin_sensor: {self.stats['skin_sensor']}")
        print(f"   environment_sensor: {self.stats['environment_sensor']}")
        print(f"   device_status: {self.stats['device_status']}")
        print()
        
        if self.stats['errors']:
            print(f"⚠️  错误列表:")
            for error in self.stats['errors'][:10]:  # 只显示前10个错误
                print(f"   - {error}")
            if len(self.stats['errors']) > 10:
                print(f"   ... 还有 {len(self.stats['errors']) - 10} 个错误")
        
        print()
        print("="*70)
        
        # 保存报告到文件
        report_path = os.path.join(os.path.dirname(__file__), 'migration_report.json')
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2, default=str)
        print(f"💾 迁移报告已保存: {report_path}")


def main():
    """主函数"""
    # 默认配置
    data_dir = '/root/course-project/week5/data-server/data-server/data'
    mongo_uri = 'mongodb://localhost:27017/'
    db_name = 'sensor_data'
    
    # 支持命令行参数
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]
    if len(sys.argv) > 2:
        mongo_uri = sys.argv[2]
    
    # 检查目录是否存在
    if not os.path.exists(data_dir):
        print(f"❌ 数据目录不存在: {data_dir}")
        sys.exit(1)
    
    # 执行迁移
    migrator = DataMigrator(mongo_uri, db_name)
    migrator.migrate_directory(data_dir)


if __name__ == '__main__':
    main()
