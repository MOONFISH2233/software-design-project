#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时数据监控脚本
功能：持续监控并显示新上传的传感器数据
"""

import os
import sys
import json
import time
from datetime import datetime


def monitor_data_realtime(data_dir='data', interval=2):
    """实时监控数据目录"""
    
    print("="*70)
    print("  实时数据监控器")
    print("="*70)
    print(f"📁 监控目录: {data_dir}")
    print(f"⏱️  刷新间隔: {interval}秒")
    print(f"📊 按 Ctrl+C 停止\n")
    
    # 记录已处理的文件
    processed_files = set()
    
    try:
        while True:
            # 获取所有JSON文件，按修改时间排序
            if not os.path.exists(data_dir):
                print(f"❌ 目录不存在: {data_dir}")
                break
            
            json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
            
            if not json_files:
                print("⏳ 等待数据...", end='\r')
                time.sleep(interval)
                continue
            
            # 按文件名排序（文件名包含时间戳）
            json_files.sort(reverse=True)
            
            # 显示最新的5个文件
            new_count = 0
            for filename in json_files[:5]:
                if filename not in processed_files:
                    filepath = os.path.join(data_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # 格式化输出
                        timestamp = data.get('timestamp', 'N/A')
                        device_id = data.get('device_id', 'N/A')
                        sensor_type = data.get('sensor_type', 'N/A')
                        
                        if sensor_type == 'skin':
                            moisture = data['data'].get('moisture', 'N/A')
                            oiliness = data['data'].get('oiliness', 'N/A')
                            temp = data['data'].get('temperature', 'N/A')
                            
                            print(f"\n✅ [{datetime.now().strftime('%H:%M:%S')}] 新数据")
                            print(f"   🆔 设备: {device_id}")
                            print(f"   💧 水分: {moisture}% | 🛢️ 油分: {oiliness}% | 🌡️ 温度: {temp}°C")
                            print(f"   ⏰ 时间: {timestamp}")
                        else:
                            print(f"\n✅ [{datetime.now().strftime('%H:%M:%S')}] 新数据 - {sensor_type}")
                            print(f"   🆔 设备: {device_id}")
                            print(f"   📦 数据: {json.dumps(data.get('data', {}), ensure_ascii=False)}")
                        
                        processed_files.add(filename)
                        new_count += 1
                        
                    except Exception as e:
                        print(f"❌ 读取失败 {filename}: {e}")
            
            if new_count == 0:
                total = len(json_files)
                print(f"⏳ 已有 {total} 条数据，等待新数据...", end='\r')
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print(f"\n\n⏹️  监控已停止")
        print(f"📊 共监控到 {len(processed_files)} 条新数据")


if __name__ == '__main__':
    data_dir = sys.argv[1] if len(sys.argv) > 1 else 'data'
    interval = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    monitor_data_realtime(data_dir, interval)
