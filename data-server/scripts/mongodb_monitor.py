#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MongoDB性能监控脚本
功能：
1. 监控数据库连接数
2. 监控内存使用
3. 监控慢查询
4. 监控磁盘使用
5. 生成监控报告并告警
"""

import sys
import json
from datetime import datetime
from pymongo import MongoClient


class MongoDBMonitor:
    """MongoDB监控器"""
    
    def __init__(self, mongo_uri='mongodb://localhost:27017/'):
        """初始化监控器"""
        self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        self.admin_db = self.client.admin
        self.alerts = []
        
    def check_connections(self):
        """检查连接数"""
        try:
            server_status = self.admin_db.command('serverStatus')
            connections = server_status['connections']
            
            current = connections['current']
            available = connections['available']
            total = current + available
            
            usage_percent = (current / total) * 100 if total > 0 else 0
            
            result = {
                'current': current,
                'available': available,
                'total': total,
                'usage_percent': round(usage_percent, 2)
            }
            
            # 告警：连接数使用超过80%
            if usage_percent > 80:
                self.alerts.append(f"⚠️  连接数使用率过高: {usage_percent}%")
            
            return result
        except Exception as e:
            return {'error': str(e)}
    
    def check_memory(self):
        """检查内存使用"""
        try:
            server_status = self.admin_db.command('serverStatus')
            mem = server_status['mem']
            
            result = {
                'resident_mb': mem.get('resident', 0),
                'virtual_mb': mem.get('virtual', 0),
                'mapped_mb': mem.get('mapped', 0)
            }
            
            # 告警：常驻内存超过2GB
            if result['resident_mb'] > 2048:
                self.alerts.append(f"⚠️  内存使用过高: {result['resident_mb']}MB")
            
            return result
        except Exception as e:
            return {'error': str(e)}
    
    def check_disk(self):
        """检查磁盘使用"""
        try:
            db_stats = self.client['sensor_data'].command('dbStats')
            
            data_size_mb = db_stats['dataSize'] / (1024 * 1024)
            storage_size_mb = db_stats['storageSize'] / (1024 * 1024)
            index_size_mb = db_stats['indexSize'] / (1024 * 1024)
            
            result = {
                'data_size_mb': round(data_size_mb, 2),
                'storage_size_mb': round(storage_size_mb, 2),
                'index_size_mb': round(index_size_mb, 2),
                'collections': db_stats['collections'],
                'objects': db_stats['objects']
            }
            
            # 告警：数据量超过10GB
            if data_size_mb > 10240:
                self.alerts.append(f"⚠️  数据量过大: {data_size_mb/1024:.2f}GB")
            
            return result
        except Exception as e:
            return {'error': str(e)}
    
    def check_slow_queries(self, threshold_ms=100):
        """检查慢查询"""
        try:
            # 获取最近1小时的慢查询
            oplog = self.admin_db['system.profile']
            
            slow_queries = list(oplog.find({
                'millis': {'$gt': threshold_ms},
                'ts': {'$gt': datetime.utcnow()}
            }).sort('ts', -1).limit(10))
            
            result = {
                'count': len(slow_queries),
                'threshold_ms': threshold_ms,
                'queries': []
            }
            
            for query in slow_queries:
                result['queries'].append({
                    'operation': query.get('op', ''),
                    'namespace': query.get('ns', ''),
                    'duration_ms': query.get('millis', 0),
                    'timestamp': query.get('ts', '')
                })
            
            # 告警：存在慢查询
            if slow_queries:
                self.alerts.append(f"⚠️  发现 {len(slow_queries)} 个慢查询（>{threshold_ms}ms）")
            
            return result
        except Exception as e:
            return {'error': str(e), 'note': '需要启用profiling'}
    
    def check_replication(self):
        """检查复制状态（如果是副本集）"""
        try:
            repl_status = self.admin_db.command('replSetGetStatus')
            
            result = {
                'status': repl_status.get('myState', 'unknown'),
                'members': len(repl_status.get('members', []))
            }
            
            return result
        except Exception as e:
            return {'status': 'standalone', 'note': '非副本集模式'}
    
    def generate_report(self):
        """生成监控报告"""
        print("="*70)
        print("  MongoDB 性能监控报告")
        print("="*70)
        print(f"📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 连接数
        print("🔗 连接数:")
        connections = self.check_connections()
        if 'error' not in connections:
            print(f"   当前连接: {connections['current']}")
            print(f"   可用连接: {connections['available']}")
            print(f"   使用率: {connections['usage_percent']}%")
        else:
            print(f"   ❌ 错误: {connections['error']}")
        print()
        
        # 内存使用
        print("💾 内存使用:")
        memory = self.check_memory()
        if 'error' not in memory:
            print(f"   常驻内存: {memory['resident_mb']}MB")
            print(f"   虚拟内存: {memory['virtual_mb']}MB")
        else:
            print(f"   ❌ 错误: {memory['error']}")
        print()
        
        # 磁盘使用
        print("💿 磁盘使用:")
        disk = self.check_disk()
        if 'error' not in disk:
            print(f"   数据大小: {disk['data_size_mb']}MB")
            print(f"   存储大小: {disk['storage_size_mb']}MB")
            print(f"   索引大小: {disk['index_size_mb']}MB")
            print(f"   集合数量: {disk['collections']}")
            print(f"   文档数量: {disk['objects']}")
        else:
            print(f"   ❌ 错误: {disk['error']}")
        print()
        
        # 慢查询
        print("🐢 慢查询:")
        slow_queries = self.check_slow_queries()
        if 'error' not in slow_queries:
            print(f"   慢查询数量: {slow_queries['count']}")
            if slow_queries['queries']:
                for query in slow_queries['queries'][:5]:
                    print(f"   - {query['operation']} {query['namespace']}: {query['duration_ms']}ms")
        else:
            print(f"   ⚠️  {slow_queries.get('note', slow_queries['error'])}")
        print()
        
        # 复制状态
        print("🔄 复制状态:")
        replication = self.check_replication()
        print(f"   状态: {replication['status']}")
        if 'members' in replication:
            print(f"   成员数量: {replication['members']}")
        print()
        
        # 告警信息
        if self.alerts:
            print("="*70)
            print("  ⚠️  告警信息")
            print("="*70)
            for alert in self.alerts:
                print(f"   {alert}")
            print()
        else:
            print("✅ 所有指标正常")
            print()
        
        print("="*70)
        
        # 保存报告
        report = {
            'timestamp': datetime.now().isoformat(),
            'connections': connections,
            'memory': memory,
            'disk': disk,
            'slow_queries': slow_queries,
            'replication': replication,
            'alerts': self.alerts
        }
        
        report_path = '/var/log/mongodb_monitor_report.json'
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            print(f"💾 监控报告已保存: {report_path}")
        except:
            pass


def main():
    """主函数"""
    monitor = MongoDBMonitor()
    monitor.generate_report()


if __name__ == '__main__':
    main()
