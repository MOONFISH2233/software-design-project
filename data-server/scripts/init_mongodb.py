#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MongoDB数据库初始化脚本
功能：
1. 创建sensor_data数据库
2. 创建3个集合（skin_sensor, environment_sensor, device_status）
3. 创建索引优化查询性能
4. 插入测试数据验证
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime, timedelta
import sys


def init_mongodb():
    """初始化MongoDB数据库"""
    
    print("="*70)
    print("  MongoDB 数据库初始化")
    print("="*70)
    
    # 连接MongoDB
    try:
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        # 测试连接
        client.admin.command('ping')
        print("✅ MongoDB 连接成功")
    except Exception as e:
        print(f"❌ MongoDB 连接失败: {e}")
        print("请确保MongoDB服务已启动: systemctl start mongod")
        sys.exit(1)
    
    db = client['sensor_data']
    print(f"📊 使用数据库: sensor_data")
    print()
    
    # 1. 创建 skin_sensor 集合并添加索引
    print("1️⃣  初始化 skin_sensor 集合...")
    skin_collection = db['skin_sensor']
    
    # 删除旧索引（如果有）
    skin_collection.drop_indexes()
    
    # 创建索引
    indexes = [
        ([('device_id', ASCENDING), ('timestamp', ASCENDING)], 'idx_device_timestamp'),
        ([('received_at', DESCENDING)], 'idx_received_at'),
        ([('quality_score', DESCENDING)], 'idx_quality_score'),
        ([('validated', ASCENDING)], 'idx_validated')
    ]
    
    for keys, name in indexes:
        skin_collection.create_index(keys, name=name)
        print(f"   ✅ 创建索引: {name}")
    
    print(f"   ✅ skin_sensor 集合初始化完成\n")
    
    # 2. 创建 environment_sensor 集合并添加索引
    print("2️⃣  初始化 environment_sensor 集合...")
    env_collection = db['environment_sensor']
    
    env_collection.drop_indexes()
    
    indexes = [
        ([('device_id', ASCENDING), ('timestamp', ASCENDING)], 'idx_device_timestamp'),
        ([('location', '2dsphere')], 'idx_location'),
        ([('pm25', ASCENDING)], 'idx_pm25'),
        ([('temperature', ASCENDING)], 'idx_temperature_range')
    ]
    
    for keys, name in indexes:
        if isinstance(keys[0][1], str):  # 2dsphere索引
            env_collection.create_index(keys, name=name)
        else:
            env_collection.create_index(keys, name=name)
        print(f"   ✅ 创建索引: {name}")
    
    print(f"   ✅ environment_sensor 集合初始化完成\n")
    
    # 3. 创建 device_status 集合并添加索引
    print("3️⃣  初始化 device_status 集合...")
    status_collection = db['device_status']
    
    status_collection.drop_indexes()
    
    indexes = [
        ([('device_id', ASCENDING), ('last_heartbeat', DESCENDING)], 'idx_device_last_heartbeat'),
        ([('status', ASCENDING)], 'idx_status'),
        ([('battery_level', ASCENDING)], 'idx_battery_low')
    ]
    
    for keys, name in indexes:
        status_collection.create_index(keys, name=name)
        print(f"   ✅ 创建索引: {name}")
    
    print(f"   ✅ device_status 集合初始化完成\n")
    
    # 4. 插入测试数据
    print("4️⃣  插入测试数据...")
    
    # 皮肤传感器测试数据
    test_skin_data = {
        'device_id': 'TEST_DEV_001',
        'moisture': 65,
        'oiliness': 32,
        'temperature': 36.5,
        'timestamp': datetime.utcnow(),
        'received_at': datetime.utcnow(),
        'client_ip': '192.168.1.100',
        'request_id': 'test_req_001',
        'validated': True,
        'quality_score': 0.95
    }
    skin_collection.insert_one(test_skin_data)
    print("   ✅ 插入皮肤传感器测试数据")
    
    # 环境传感器测试数据
    test_env_data = {
        'device_id': 'TEST_DEV_002',
        'temperature': 25.3,
        'humidity': 60.5,
        'pm25': 35,
        'co2': 450,
        'light_intensity': 500.0,
        'noise_level': 45.2,
        'timestamp': datetime.utcnow(),
        'received_at': datetime.utcnow(),
        'location': {
            'type': 'Point',
            'coordinates': [116.4074, 39.9042]  # 北京坐标
        }
    }
    env_collection.insert_one(test_env_data)
    print("   ✅ 插入环境传感器测试数据")
    
    # 设备状态测试数据
    test_status_data = {
        'device_id': 'TEST_DEV_001',
        'status': 'online',
        'battery_level': 85,
        'signal_strength': -65,
        'firmware_version': 'v2.1.0',
        'last_heartbeat': datetime.utcnow(),
        'uptime': 86400,
        'memory_usage': 45.2
    }
    status_collection.insert_one(test_status_data)
    print("   ✅ 插入设备状态测试数据")
    
    print()
    
    # 5. 验证数据
    print("5️⃣  验证数据...")
    skin_count = skin_collection.count_documents({})
    env_count = env_collection.count_documents({})
    status_count = status_collection.count_documents({})
    
    print(f"   📊 skin_sensor: {skin_count} 条记录")
    print(f"   📊 environment_sensor: {env_count} 条记录")
    print(f"   📊 device_status: {status_count} 条记录")
    print()
    
    # 6. 显示索引信息
    print("6️⃣  索引信息汇总...")
    for coll_name in ['skin_sensor', 'environment_sensor', 'device_status']:
        collection = db[coll_name]
        indexes = list(collection.list_indexes())
        print(f"   {coll_name}: {len(indexes)} 个索引")
        for idx in indexes:
            if idx['name'] != '_id_':
                print(f"      - {idx['name']}: {dict(idx['key'])}")
    
    print()
    print("="*70)
    print("  ✅ MongoDB 数据库初始化完成！")
    print("="*70)
    print()
    print("💡 提示:")
    print("   - 查看数据: mongo --eval 'db.skin_sensor.find().pretty()'")
    print("   - 查看统计: mongo --eval 'db.stats()'")
    print("   - 备份数据: mongodump --db sensor_data --out /backup/")
    print()


if __name__ == '__main__':
    init_mongodb()
