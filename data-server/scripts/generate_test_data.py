#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为用户123生成测试数据
包括：设备、皮肤数据、环境数据、健康报告、通知等
"""

import sys
import os
from datetime import datetime, timedelta
import random

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, User, Device, DeviceBinding, SkinSensorData, EnvironmentSensorData, HealthReport, Notification, DailyStatistics
from app_simple import app


def generate_test_data():
    """为指定用户生成完整的测试数据"""
    
    with app.app_context():
        # 查找用户
        user = User.query.filter_by(username='123').first()
        if not user:
            print("❌ 用户 '123' 不存在")
            return
        
        print(f"✅ 找到用户: {user.username} (ID: {user.id})")
        
        # 1. 创建设备
        print("\n【步骤1】创建设备...")
        devices = []
        device_configs = [
            {'device_id': 'DEV_001', 'device_type': 'skin_sensor', 'location': '卧室'},
            {'device_id': 'DEV_002', 'device_type': 'skin_sensor', 'location': '客厅'},
            {'device_id': 'ENV_001', 'device_type': 'environment', 'location': '书房'},
        ]
        
        for config in device_configs:
            device = Device.query.filter_by(device_id=config['device_id']).first()
            if not device:
                device = Device(
                    device_id=config['device_id'],
                    device_type=config['device_type'],
                    location=config['location'],
                    status='online',
                    battery_level=random.randint(60, 95),
                    signal_strength=random.randint(-70, -40),
                    last_heartbeat=datetime.now() - timedelta(minutes=random.randint(1, 30)),
                    firmware_version='v1.0.0',
                    install_date=datetime.now().date()
                )
                db.session.add(device)
                print(f"  ✓ 创建设备: {config['device_id']} ({config['location']})")
            else:
                print(f"  • 设备已存在: {config['device_id']}")
            
            # 绑定设备到用户
            binding = DeviceBinding.query.filter_by(user_id=user.id, device_id=config['device_id']).first()
            if not binding:
                binding = DeviceBinding(
                    user_id=user.id,
                    device_id=config['device_id'],
                    bind_time=datetime.now(),
                    is_primary=(len(devices) == 0)  # 第一个设备设为主设备
                )
                db.session.add(binding)
            
            devices.append(device)
        
        db.session.commit()
        
        # 2. 生成皮肤传感器数据（过去30天，每小时1条）
        print("\n【步骤2】生成皮肤传感器数据...")
        skin_count = 0
        for device in [d for d in devices if d.device_type == 'skin_sensor']:
            device_name = f"{device.location}检测仪"
            # 过去30天，每天生成14条数据（8:00-22:00，每小时1条）
            for day_offset in range(30):
                date = datetime.now() - timedelta(days=day_offset)
                
                for hour in range(8, 22):  # 早上8点到晚上10点 (不含22点，即8-21点共14个小时)
                    minute = random.randint(0, 59)
                    sensor_time = date.replace(hour=hour, minute=minute, second=0)
                    
                    # 根据时间段调整数值（早上水分高，晚上油性高）
                    base_moisture = 65 if hour < 12 else 55
                    base_oiliness = 35 if hour < 12 else 45
                    
                    skin_data = SkinSensorData(
                        device_id=device.device_id,
                        moisture=random.randint(base_moisture - 10, base_moisture + 10),  # 水分波动
                        oiliness=random.randint(base_oiliness - 8, base_oiliness + 8),  # 油分波动
                        temperature=random.uniform(32, 36),  # 温度 32-36°C
                        sensor_time=sensor_time,
                        received_at=datetime.now(),
                        quality_score=random.uniform(75, 95),
                        client_ip='192.168.1.100',
                        request_id=f'REQ_{int(sensor_time.timestamp())}',
                        validated=True
                    )
                    db.session.add(skin_data)
                    skin_count += 1
            
            print(f"  ✓ {device_name}: 生成 {skin_count} 条数据")
        
        db.session.commit()
        print(f"  总计生成 {skin_count} 条皮肤数据")
        
        # 3. 生成环境传感器数据（过去30天，每2小时1条）
        print("\n【步骤3】生成环境传感器数据...")
        env_count = 0
        for device in [d for d in devices if d.device_type == 'environment']:
            device_name = f"{device.location}监测仪"
            for day_offset in range(30):
                date = datetime.now() - timedelta(days=day_offset)
                
                # 每2小时生成1条数据（一天12条）
                for hour in range(0, 24, 2):
                    minute = random.randint(0, 59)
                    sensor_time = date.replace(hour=hour, minute=minute, second=0)
                    
                    # 根据时间段调整温度和湿度
                    base_temp = 22 if 6 <= hour <= 18 else 18  # 白天22度，晚上18度
                    base_humidity = 45 if 6 <= hour <= 18 else 55
                    
                    env_data = EnvironmentSensorData(
                        device_id=device.device_id,
                        temperature=random.uniform(base_temp - 2, base_temp + 2),
                        humidity=random.uniform(base_humidity - 5, base_humidity + 5),
                        pm25=random.randint(15, 50),  # PM2.5: 15-50 (优良)
                        co2=random.randint(400, 800),  # CO2: 400-800 ppm
                        sensor_time=sensor_time,
                        received_at=datetime.now(),
                        quality_score=random.uniform(80, 98),
                        client_ip='192.168.1.101',
                        request_id=f'ENV_REQ_{int(sensor_time.timestamp())}',
                        validated=True
                    )
                    db.session.add(env_data)
                    env_count += 1
            
            print(f"  ✓ {device_name}: 生成 {env_count} 条数据")
        
        db.session.commit()
        print(f"  总计生成 {env_count} 条环境数据")
        
        # 4. 生成每日统计数据（Dashboard图表数据源）
        print("\n【步骤4】生成每日统计数据...")
        stats_count = 0
        for day_offset in range(30):
            stat_date = (datetime.now() - timedelta(days=day_offset)).date()
            
            # 计算当天的平均值（模拟）
            avg_moisture = random.uniform(58, 68)  # 水分 58-68%
            avg_oiliness = random.uniform(38, 48)  # 油性 38-48%
            avg_elasticity = random.uniform(72, 82)  # 弹性 72-82%
            avg_temperature = random.uniform(20, 24)  # 环境温度
            avg_humidity = random.uniform(45, 55)  # 环境湿度
            
            daily_stat = DailyStatistics(
                stat_date=stat_date,
                avg_moisture=round(avg_moisture, 2),
                avg_oiliness=round(avg_oiliness, 2),
                avg_temperature=round(avg_temperature, 2),
                avg_humidity=round(avg_humidity, 2),
                total_records=random.randint(10, 20),
                active_devices=3,
                created_at=datetime.now()
            )
            db.session.add(daily_stat)
            stats_count += 1
        
        db.session.commit()
        print(f"  ✓ 生成 {stats_count} 条每日统计数据（过去30天）")
        
        # 5. 创建健康报告
        print("\n【步骤5】创建健康报告...")
        reports = [
            {
                'title': '本周皮肤健康分析报告',
                'report_type': 'weekly',
                'summary': '本周皮肤整体状态良好，水分含量保持在正常范围。建议加强保湿护理。',
                'score': random.randint(75, 90),
                'recommendations': [
                    '保持每日补水，建议使用保湿精华',
                    '注意防晒，避免紫外线伤害',
                    '适当增加运动，促进血液循环'
                ]
            },
            {
                'title': '环境影响因素分析',
                'report_type': 'environment',
                'summary': '室内空气质量优良，温湿度适宜。PM2.5浓度在安全范围内。',
                'score': random.randint(80, 95),
                'recommendations': [
                    '继续保持室内通风',
                    '定期清洁空调滤网',
                    '可适当使用加湿器调节湿度'
                ]
            },
            {
                'title': '月度皮肤趋势报告',
                'report_type': 'monthly',
                'summary': '过去一个月皮肤状态稳步提升，水分和弹性指标均有改善。',
                'score': random.randint(70, 85),
                'recommendations': [
                    '坚持当前护肤方案',
                    '可尝试添加抗氧化产品',
                    '建议每月进行一次深层清洁'
                ]
            }
        ]
        
        for report_data in reports:
            report = HealthReport(
                user_id=user.id,
                report_type=report_data['report_type'],
                report_date=datetime.now().date() - timedelta(days=random.randint(1, 7)),
                start_date=datetime.now().date() - timedelta(days=8),
                end_date=datetime.now().date() - timedelta(days=1),
                content_json={
                    'title': report_data['title'],
                    'summary': report_data['summary'],
                    'recommendations': report_data['recommendations']
                },
                score=float(report_data['score']),
                suggestions='\n'.join(report_data['recommendations']),
                is_generated=True,
                generated_at=datetime.now() - timedelta(days=random.randint(1, 7))
            )
            db.session.add(report)
            print(f"  ✓ 创建报告: {report_data['title']}")
        
        db.session.commit()
        
        # 6. 创建通知
        print("\n【步骤6】创建通知...")
        notifications = [
            {
                'title': '设备在线提醒',
                'content': '您的卧室检测仪已重新连接，当前电量85%',
                'type': 'device',
                'is_read': False
            },
            {
                'title': '皮肤数据异常',
                'content': '检测到昨晚23:30皮肤水分含量偏低（28%），建议及时补水',
                'type': 'alert',
                'is_read': False
            },
            {
                'title': '周报生成完成',
                'content': '您的本周皮肤健康分析报告已生成，点击查看详细内容',
                'type': 'report',
                'is_read': True
            },
            {
                'title': '系统维护通知',
                'content': '系统将于今晚凌晨2:00-3:00进行例行维护，期间可能无法访问',
                'type': 'system',
                'is_read': True
            },
            {
                'title': '新设备绑定成功',
                'content': '环境监测仪已成功绑定到您的账户',
                'type': 'device',
                'is_read': True
            }
        ]
        
        for notif_data in notifications:
            notification = Notification(
                user_id=user.id,
                type=notif_data['type'],
                title=notif_data['title'],
                content=notif_data['content'],
                is_read=notif_data['is_read'],
                read_at=datetime.now() if notif_data['is_read'] else None,
                created_at=datetime.now() - timedelta(hours=random.randint(1, 48))
            )
            db.session.add(notification)
            print(f"  ✓ 创建通知: {notif_data['title']}")
        
        db.session.commit()
        
        # 7. 统计信息
        print("\n" + "="*60)
        print("📊 数据生成完成统计")
        print("="*60)
        print(f"用户: {user.username} (ID: {user.id})")
        print(f"设备数量: {len(devices)}")
        print(f"皮肤数据: {skin_count} 条")
        print(f"环境数据: {env_count} 条")
        print(f"健康报告: {len(reports)} 份")
        print(f"通知消息: {len(notifications)} 条")
        print("="*60)
        print("\n✅ 所有测试数据生成成功！")
        print("现在可以登录前端页面查看完整数据展示")


if __name__ == '__main__':
    generate_test_data()
