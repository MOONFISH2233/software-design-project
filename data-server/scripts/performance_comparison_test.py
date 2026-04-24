#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MongoDB vs 文件存储性能对比测试
功能：
1. 测试写入性能（QPS）
2. 测试查询性能（响应时间）
3. 测试并发能力
4. 生成性能对比报告
"""

import os
import sys
import json
import time
import random
import threading
from datetime import datetime, timedelta
from pymongo import MongoClient
from typing import Dict, List, Any
import statistics


class PerformanceTester:
    """性能测试器"""
    
    def __init__(self, mongo_uri='mongodb://localhost:27017/', db_name='sensor_data', file_dir='data/perf_test'):
        """初始化测试器"""
        self.mongo_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        self.db = self.mongo_client[db_name]
        self.file_dir = file_dir
        os.makedirs(file_dir, exist_ok=True)
        
        # 测试结果
        self.results = {
            'mongodb': {'write': [], 'read': []},
            'file': {'write': [], 'read': []}
        }
    
    def generate_test_data(self, count: int = 1000) -> List[Dict]:
        """生成测试数据"""
        data = []
        for i in range(count):
            record = {
                'device_id': f'TEST_DEV_{i % 10:03d}',
                'moisture': random.randint(50, 80),
                'oiliness': random.randint(20, 50),
                'temperature': round(random.uniform(35.0, 38.0), 1),
                'timestamp': (datetime.utcnow() - timedelta(seconds=random.randint(0, 3600))).isoformat(),
                'received_at': datetime.utcnow(),
                'validated': True,
                'quality_score': round(random.uniform(0.8, 1.0), 2)
            }
            data.append(record)
        return data
    
    def test_mongodb_write(self, data: List[Dict], batch_size: int = 100) -> Dict:
        """测试MongoDB写入性能"""
        print("\n📊 测试 MongoDB 写入性能...")
        
        collection = self.db['skin_sensor']
        start_time = time.time()
        total_records = 0
        
        # 分批写入
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            operations = [InsertOne(record) for record in batch]
            collection.bulk_write(operations, ordered=False)
            total_records += len(batch)
        
        elapsed = time.time() - start_time
        qps = total_records / elapsed if elapsed > 0 else 0
        
        result = {
            'total_records': total_records,
            'elapsed_seconds': round(elapsed, 3),
            'qps': round(qps, 2),
            'avg_latency_ms': round((elapsed / total_records) * 1000, 2)
        }
        
        print(f"   ✅ 写入 {total_records} 条记录")
        print(f"   ⏱️  耗时: {result['elapsed_seconds']}s")
        print(f"   🚀 QPS: {result['qps']}")
        print(f"   📈 平均延迟: {result['avg_latency_ms']}ms")
        
        return result
    
    def test_file_write(self, data: List[Dict]) -> Dict:
        """测试文件写入性能"""
        print("\n📊 测试 文件存储 写入性能...")
        
        start_time = time.time()
        total_records = 0
        
        for i, record in enumerate(data):
            filepath = os.path.join(self.file_dir, f'record_{i}.json')
            # 转换所有非JSON序列化类型
            serializable_record = {}
            for key, value in record.items():
                if isinstance(value, datetime):
                    serializable_record[key] = value.isoformat()
                elif hasattr(value, '__str__') and type(value).__name__ == 'ObjectId':
                    serializable_record[key] = str(value)
                else:
                    serializable_record[key] = value
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(serializable_record, f, ensure_ascii=False, indent=2)
            total_records += 1
        
        elapsed = time.time() - start_time
        qps = total_records / elapsed if elapsed > 0 else 0
        
        result = {
            'total_records': total_records,
            'elapsed_seconds': round(elapsed, 3),
            'qps': round(qps, 2),
            'avg_latency_ms': round((elapsed / total_records) * 1000, 2)
        }
        
        print(f"   ✅ 写入 {total_records} 条记录")
        print(f"   ⏱️  耗时: {result['elapsed_seconds']}s")
        print(f"   🚀 QPS: {result['qps']}")
        print(f"   📈 平均延迟: {result['avg_latency_ms']}ms")
        
        return result
    
    def test_mongodb_read(self, query_count: int = 100) -> Dict:
        """测试MongoDB查询性能"""
        print("\n📊 测试 MongoDB 查询性能...")
        
        collection = self.db['skin_sensor']
        latencies = []
        
        for _ in range(query_count):
            device_id = f'TEST_DEV_{random.randint(0, 9):03d}'
            start = time.time()
            result = list(collection.find({'device_id': device_id}).limit(10))
            elapsed = (time.time() - start) * 1000  # 转换为毫秒
            latencies.append(elapsed)
        
        avg_latency = statistics.mean(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
        qps = query_count / (sum(latencies) / 1000) if sum(latencies) > 0 else 0
        
        result = {
            'total_queries': query_count,
            'avg_latency_ms': round(avg_latency, 2),
            'p95_latency_ms': round(p95_latency, 2),
            'qps': round(qps, 2)
        }
        
        print(f"   ✅ 执行 {query_count} 次查询")
        print(f"   📈 平均延迟: {result['avg_latency_ms']}ms")
        print(f"   📊 P95延迟: {result['p95_latency_ms']}ms")
        print(f"   🚀 QPS: {result['qps']}")
        
        return result
    
    def test_file_read(self, query_count: int = 100) -> Dict:
        """测试文件读取性能"""
        print("\n📊 测试 文件存储 读取性能...")
        
        # 获取所有文件
        files = glob.glob(os.path.join(self.file_dir, '*.json'))
        if not files:
            print("   ⚠️  没有文件可读取")
            return {'total_queries': 0, 'avg_latency_ms': 0, 'p95_latency_ms': 0, 'qps': 0}
        
        latencies = []
        
        for _ in range(query_count):
            filepath = random.choice(files)
            start = time.time()
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                elapsed = (time.time() - start) * 1000
                latencies.append(elapsed)
            except:
                pass
        
        if latencies:
            avg_latency = statistics.mean(latencies)
            p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
            qps = len(latencies) / (sum(latencies) / 1000) if sum(latencies) > 0 else 0
        else:
            avg_latency = p95_latency = qps = 0
        
        result = {
            'total_queries': len(latencies),
            'avg_latency_ms': round(avg_latency, 2),
            'p95_latency_ms': round(p95_latency, 2),
            'qps': round(qps, 2)
        }
        
        print(f"   ✅ 执行 {len(latencies)} 次查询")
        print(f"   📈 平均延迟: {result['avg_latency_ms']}ms")
        print(f"   📊 P95延迟: {result['p95_latency_ms']}ms")
        print(f"   🚀 QPS: {result['qps']}")
        
        return result
    
    def run_full_test(self, record_count: int = 1000, query_count: int = 100):
        """运行完整性能测试"""
        print("="*70)
        print("  MongoDB vs 文件存储 性能对比测试")
        print("="*70)
        
        # 生成测试数据
        print(f"\n🔄 生成 {record_count} 条测试数据...")
        test_data = self.generate_test_data(record_count)
        print(f"   ✅ 数据生成完成")
        
        # 测试写入性能
        print("\n" + "="*70)
        print("  写入性能测试")
        print("="*70)
        
        mongodb_write_result = self.test_mongodb_write(test_data)
        file_write_result = self.test_file_write(test_data)
        
        # 测试读取性能
        print("\n" + "="*70)
        print("  读取性能测试")
        print("="*70)
        
        mongodb_read_result = self.test_mongodb_read(query_count)
        file_read_result = self.test_file_read(query_count)
        
        # 生成对比报告
        self.generate_comparison_report(
            mongodb_write_result, file_write_result,
            mongodb_read_result, file_read_result
        )
        
        # 清理测试数据
        self.cleanup_test_data()
    
    def generate_comparison_report(self, mongo_write, file_write, mongo_read, file_read):
        """生成性能对比报告"""
        print("\n" + "="*70)
        print("  性能对比报告")
        print("="*70)
        print()
        
        # 写入性能对比
        print("📝 写入性能对比:")
        print(f"   MongoDB:  QPS={mongo_write['qps']}, 延迟={mongo_write['avg_latency_ms']}ms")
        print(f"   文件存储: QPS={file_write['qps']}, 延迟={file_write['avg_latency_ms']}ms")
        
        if file_write['qps'] > 0:
            write_improvement = ((mongo_write['qps'] - file_write['qps']) / file_write['qps']) * 100
            print(f"   📈 提升: {write_improvement:+.1f}%")
        
        print()
        
        # 读取性能对比
        print("📖 读取性能对比:")
        print(f"   MongoDB:  QPS={mongo_read['qps']}, 平均延迟={mongo_read['avg_latency_ms']}ms, P95={mongo_read['p95_latency_ms']}ms")
        print(f"   文件存储: QPS={file_read['qps']}, 平均延迟={file_read['avg_latency_ms']}ms, P95={file_read['p95_latency_ms']}ms")
        
        if file_read['avg_latency_ms'] > 0:
            read_improvement = ((file_read['avg_latency_ms'] - mongo_read['avg_latency_ms']) / file_read['avg_latency_ms']) * 100
            print(f"   📈 延迟降低: {read_improvement:.1f}%")
        
        print()
        print("="*70)
        
        # 保存报告
        report = {
            'test_time': datetime.now().isoformat(),
            'mongodb_write': mongo_write,
            'file_write': file_write,
            'mongodb_read': mongo_read,
            'file_read': file_read
        }
        
        report_path = os.path.join(os.path.dirname(__file__), 'performance_comparison_report.json')
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"💾 详细报告已保存: {report_path}")
    
    def cleanup_test_data(self):
        """清理测试数据"""
        print("\n🧹 清理测试数据...")
        
        # 清理MongoDB测试数据
        self.db['skin_sensor'].delete_many({'device_id': {'$regex': '^TEST_DEV_'}})
        print("   ✅ MongoDB测试数据已清理")
        
        # 清理文件测试数据
        import shutil
        if os.path.exists(self.file_dir):
            shutil.rmtree(self.file_dir)
            print("   ✅ 文件测试数据已清理")


def main():
    """主函数"""
    # 默认配置
    record_count = 1000
    query_count = 100
    
    # 支持命令行参数
    if len(sys.argv) > 1:
        record_count = int(sys.argv[1])
    if len(sys.argv) > 2:
        query_count = int(sys.argv[2])
    
    # 执行测试
    tester = PerformanceTester()
    tester.run_full_test(record_count, query_count)


if __name__ == '__main__':
    from pymongo import InsertOne
    import glob
    main()
