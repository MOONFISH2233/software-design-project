"""
数据生成模拟器 - MQ 版本（带重传机制）
功能：
1. 生成传感器数据并发布到消息队列
2. 失败数据自动加入重试队列
3. 定期重传失败数据
4. 支持 Redis 和 RabbitMQ 两种后端
"""

import threading
import time
import random
import csv
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import sys
import os

# 添加父目录到路径，以便导入 mq_utils
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mq_utils import create_mq

# ================= 配置区 =================
class Config:
    """配置类"""
    # MQ 配置
    MQ_TYPE = 'redis'  
    MQ_HOST = '47.103.108.47'
    MQ_PORT = 6379
    MQ_DB = 0
    
    # 流名称
    RAW_DATA_STREAM = 'sensor:raw'
    RETRY_QUEUE = 'retry'
    
    # 文件配置
    CSV_FILE_NAME = "mirror_sensor_data.csv"
    TXT_FILE_NAME = "mirror_sensor_log.txt"
    
    # 重传配置
    MAX_RETRY_COUNT = 3  # 最大重试次数
    RETRY_INTERVAL = 30  # 重试间隔（秒）
    TIMEOUT_SECONDS = 10  # 超时时间（秒）
    
    # 采样间隔
    SKIN_SENSOR_INTERVAL = 2  # 皮肤传感器采样间隔（秒）
    ENV_SENSOR_INTERVAL = 3   # 环境传感器采样间隔（秒）


# ================= 全局变量 =================
stop_event = threading.Event()
file_lock = threading.Lock()
mq_client = None
retry_queue = []  # 本地重试队列
retry_lock = threading.Lock()


# ================= 初始化文件 =================
def init_files():
    """初始化本地文件"""
    # 初始化 CSV 文件并写入表头
    with open(Config.CSV_FILE_NAME, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["时间戳", "传感器来源", "数据项 1", "数据项 2"])
    
    # 初始化 TXT 文件并写入标题头
    with open(Config.TXT_FILE_NAME, mode='w', encoding='utf-8') as file:
        file.write("=== AI 宠物美妆镜 - 传感器后台数据日志 (MQ 版本) ===\n")
    
    print("✅ 本地文件初始化完成")


# ================= 数据发布器 =================
class DataPublisher:
    """数据发布器 - 负责将数据发布到 MQ"""
    
    def __init__(self):
        self.published_count = 0
        self.failed_count = 0
        self.retry_count = 0
        self.lock = threading.Lock()
    
    def publish_with_retry(self, data: Dict[str, Any], sensor_type: str, description: str):
        """
        发布数据到 MQ，失败时加入重试队列
        :param data: 要发布的数据
        :param sensor_type: 传感器类型
        :param description: 描述信息
        """
        success = False
        
        # 尝试发布到 MQ
        try:
            message = {
                'sensor_type': sensor_type,
                'data': data,
                'description': description,
                'timestamp': datetime.now().isoformat(),
                'retry_count': 0
            }
            
            if mq_client and mq_client.connected:
                success = mq_client.publish(Config.RAW_DATA_STREAM, message)
            
            if success:
                with self.lock:
                    self.published_count += 1
                print(f"    📤 已发布到 MQ: {sensor_type} - {message['timestamp']}")
                return True
            else:
                raise Exception("MQ 发布失败")
                
        except Exception as e:
            print(f"    ⚠️  发布失败：{str(e)}")
            self._add_to_retry(data, sensor_type, description)
            with self.lock:
                self.failed_count += 1
            return False
    
    def _add_to_retry(self, data: Dict[str, Any], sensor_type: str, description: str):
        """
        将失败的数据加入重试队列
        :param data: 数据
        :param sensor_type: 传感器类型
        :param description: 描述
        """
        retry_item = {
            'data': data,
            'sensor_type': sensor_type,
            'description': description,
            'first_failed_time': datetime.now(),
            'retry_count': 0,
            'next_retry_time': datetime.now() + timedelta(seconds=Config.RETRY_INTERVAL)
        }
        
        with retry_lock:
            retry_queue.append(retry_item)
            print(f"    💾 已加入重试队列，将在 {Config.RETRY_INTERVAL} 秒后重试")
    
    def process_retry_queue(self):
        """处理重试队列"""
        current_time = datetime.now()
        items_to_remove = []
        
        with retry_lock:
            for item in retry_queue:
                # 检查是否到了重试时间
                if current_time >= item['next_retry_time']:
                    if item['retry_count'] >= Config.MAX_RETRY_COUNT:
                        # 超过最大重试次数，放弃
                        print(f"    ❌ 放弃重传：{item['sensor_type']} - 已达最大重试次数")
                        items_to_remove.append(item)
                        continue
                    
                    # 尝试重传
                    print(f"    🔄 正在重传：{item['sensor_type']} (第 {item['retry_count'] + 1} 次)")
                    success = self.publish_with_retry(
                        item['data'],
                        item['sensor_type'],
                        item['description']
                    )
                    
                    if success:
                        items_to_remove.append(item)
                        with self.lock:
                            self.retry_count += 1
                    else:
                        # 更新重试信息
                        item['retry_count'] += 1
                        item['next_retry_time'] = current_time + timedelta(seconds=Config.RETRY_INTERVAL * (item['retry_count'] + 1))
        
        # 移除已处理的项目
        with retry_lock:
            for item in items_to_remove:
                if item in retry_queue:
                    retry_queue.remove(item)
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        with self.lock:
            return {
                'published': self.published_count,
                'failed': self.failed_count,
                'retried': self.retry_count,
                'pending_retry': len(retry_queue)
            }


# ================= 线程 1：模拟皮肤传感器 =================
def simulate_skin_sensor(publisher: DataPublisher):
    """皮肤传感器模拟线程"""
    while not stop_event.is_set():
        # 生成随机数据
        moisture = random.randint(40, 90)      # 水分度 40%-90%
        oiliness = random.randint(10, 60)      # 油亮度 10%-60%
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 写入本地文件（加锁）
        with file_lock:
            with open(Config.CSV_FILE_NAME, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, "皮肤传感器", f"水分度:{moisture}%", f"油亮度:{oiliness}%"])
            with open(Config.TXT_FILE_NAME, mode='a', encoding='utf-8') as file:
                file.write(f"[{timestamp}] [皮肤检测] 💧 当前水分度：{moisture}%, 当前油亮度：{oiliness}%\n")
        
        print(f"[{timestamp}] 💧 皮肤传感器已记录 -> 水分度:{moisture}% | 油亮度:{oiliness}%")
        
        # 发布到 MQ
        data = {
            "moisture": moisture,
            "oiliness": oiliness,
            "device_id": "skin_sensor_001",
            "timestamp": timestamp
        }
        publisher.publish_with_retry(data, "skin", "皮肤传感器数据")
        
        # 采样间隔（分段睡眠以便快速响应退出）
        for _ in range(int(Config.SKIN_SENSOR_INTERVAL / 0.5)):
            if stop_event.is_set():
                break
            time.sleep(0.5)


# ================= 线程 2：模拟环境传感器 =================
def simulate_env_sensor(publisher: DataPublisher):
    """环境传感器模拟线程"""
    while not stop_event.is_set():
        # 生成随机数据
        humidity = random.randint(30, 80)      # 环境湿度 30%-80%
        light_lux = random.randint(200, 1000)  # 环境光照度 200-1000 Lux
        temperature = round(random.uniform(20.0, 30.0), 1)  # 温度 20-30℃
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 写入本地文件（加锁）
        with file_lock:
            with open(Config.CSV_FILE_NAME, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, "环境传感器", f"湿度:{humidity}%", f"光照度:{light_lux}Lux"])
            with open(Config.TXT_FILE_NAME, mode='a', encoding='utf-8') as file:
                file.write(f"[{timestamp}] [环境检测] ☀️ 当前湿度：{humidity}%, 光照度:{light_lux}Lux, 温度:{temperature}℃\n")
        
        print(f"[{timestamp}] ☀️ 环境传感器已记录 -> 湿度:{humidity}% | 光照度:{light_lux}Lux | 温度:{temperature}℃")
        
        # 发布到 MQ
        data = {
            "humidity": humidity,
            "light_lux": light_lux,
            "temperature": temperature,
            "device_id": "env_sensor_001",
            "timestamp": timestamp
        }
        publisher.publish_with_retry(data, "environment", "环境传感器数据")
        
        # 采样间隔
        for _ in range(int(Config.ENV_SENSOR_INTERVAL / 0.5)):
            if stop_event.is_set():
                break
            time.sleep(0.5)


# ================= 线程 3：重试队列处理器 =================
def retry_processor(publisher: DataPublisher):
    """定期处理重试队列"""
    while not stop_event.is_set():
        publisher.process_retry_queue()
        
        # 每秒检查一次重试队列
        for _ in range(2):
            if stop_event.is_set():
                break
            time.sleep(0.5)


# ================= 线程 4：状态监控器 =================
def status_monitor(publisher: DataPublisher):
    """定期打印统计信息"""
    while not stop_event.is_set():
        stats = publisher.get_stats()
        print("\n" + "="*60)
        print("📊 模拟器统计信息")
        print("="*60)
        print(f"成功发布：{stats['published']} 条")
        print(f"失败：{stats['failed']} 条")
        print(f"重传成功：{stats['retried']} 条")
        print(f"等待重传：{stats['pending_retry']} 条")
        
        if mq_client:
            print(f"\nMQ 连接状态：{'✅ 已连接' if mq_client.connected else '❌ 未连接'}")
            if hasattr(mq_client, 'get_stream_length'):
                stream_len = mq_client.get_stream_length(Config.RAW_DATA_STREAM)
                print(f"MQ 流长度：{stream_len} 条消息")
        
        print("="*60 + "\n")
        
        # 每分钟统计一次
        for _ in range(120):
            if stop_event.is_set():
                break
            time.sleep(0.5)


# ================= 主程序入口 =================
def main():
    """主函数"""
    global mq_client
    
    print("\n" + "="*60)
    print("🚀 魔镜数据模拟器 v2.0 - MQ 版本（带重传机制）")
    print("="*60)
    print(f"\n📋 配置信息:")
    print(f"   MQ 类型：{Config.MQ_TYPE}")
    print(f"   MQ 地址：{Config.MQ_HOST}:{Config.MQ_PORT}")
    print(f"   数据流：{Config.RAW_DATA_STREAM}")
    print(f"   重试间隔：{Config.RETRY_INTERVAL}秒")
    print(f"   最大重试次数：{Config.MAX_RETRY_COUNT}")
    print(f"\n💡 提示：按 Ctrl+C 可以停止运行\n")
    
    # 初始化文件
    init_files()
    
    # 连接 MQ
    mq_client = create_mq(
        Config.MQ_TYPE,
        host=Config.MQ_HOST,
        port=Config.MQ_PORT,
        db=Config.MQ_DB
    )
    
    if not mq_client.connect():
        print("⚠️  MQ 连接失败，将使用本地重试队列缓存数据")
        print("   请确保 Redis/RabbitMQ 服务已启动")
    else:
        print(f"✅ MQ 连接成功 - {Config.MQ_TYPE}")
    
    # 创建发布器
    publisher = DataPublisher()
    
    # 创建线程
    threads = [
        threading.Thread(target=simulate_skin_sensor, args=(publisher,), name="SkinThread"),
        threading.Thread(target=simulate_env_sensor, args=(publisher,), name="EnvThread"),
        threading.Thread(target=retry_processor, args=(publisher,), name="RetryThread"),
        threading.Thread(target=status_monitor, args=(publisher,), name="MonitorThread")
    ]
    
    # 启动线程
    for t in threads:
        t.start()
        print(f"✅ 线程 {t.name} 已启动")
    
    print("\n🎯 所有线程已启动，开始生成数据...\n")
    
    # 等待用户中断
    try:
        while True:
            time.sleep(0.5)
            # 检查是否有线程异常退出
            if not any(t.is_alive() for t in threads[:2]):
                print("⚠️  有线程已退出")
                break
    except KeyboardInterrupt:
        print("\n\n🛑 收到中断信号，正在停止模拟器...")
        stop_event.set()
    
    # 等待线程结束
    for t in threads:
        t.join(timeout=2.0)
    
    # 关闭 MQ 连接
    if mq_client:
        mq_client.close()
    
    # 打印最终统计
    final_stats = publisher.get_stats()
    print("\n" + "="*60)
    print("📊 最终统计")
    print("="*60)
    print(f"总发布数：{final_stats['published']}")
    print(f"总失败数：{final_stats['failed']}")
    print(f"总重传数：{final_stats['retried']}")
    print(f"剩余待重试：{final_stats['pending_retry']}")
    print("="*60)
    print("\n✅ 模拟器已安全退出。\n")


if __name__ == "__main__":
    main()
