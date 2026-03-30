"""
数据接收模块 - 从 MQ 读取原始数据
功能：
1. 从 Redis Stream 读取传感器数据
2. 进行基本格式验证
3. 发布到验证队列
4. 支持多实例并行运行
"""

import sys
import json
from datetime import datetime
from typing import Dict, Any
import os

# 导入 MQ 工具
from mq_utils import create_mq

# ================= 配置 =================
class Config:
    """配置类"""
    # MQ 配置
    MQ_TYPE = 'redis'
    MQ_HOST = 'localhost'
    MQ_PORT = 6379
    MQ_DB = 0
    
    # 流和队列
    RAW_DATA_STREAM = 'sensor:raw'
    VALIDATED_QUEUE = 'sensor:validated'
    
    # 消费者组配置
    CONSUMER_GROUP = 'receiver_group'
    CONSUMER_NAME = f'receiver_{os.getpid()}'  # 使用进程 ID 作为唯一标识
    
    # 日志配置
    LOG_FILE = 'logs/receiver.log'


# ================= 日志处理器 =================
class SimpleLogger:
    """简单日志记录器"""
    
    def __init__(self, log_file: str):
        self.log_file = log_file
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    def info(self, message: str):
        self._write('INFO', message)
    
    def error(self, message: str):
        self._write('ERROR', message)
    
    def warning(self, message: str):
        self._write('WARNING', message)
    
    def _write(self, level: str, message: str):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] [{level}] {message}\n"
        
        # 写入文件
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_line)
        
        # 同时输出到控制台
        print(log_line.strip())


logger = SimpleLogger(Config.LOG_FILE)


# ================= 数据处理 =================
def validate_basic_format(message: Dict[str, Any]) -> bool:
    """
    验证消息的基本格式
    :param message: 消息内容
    :return: 是否有效
    """
    # 检查必要字段
    required_fields = ['sensor_type', 'data', 'timestamp']
    for field in required_fields:
        if field not in message:
            return False
    
    # 检查 sensor_type 是否有效
    valid_types = ['skin', 'environment', 'device']
    if message['sensor_type'] not in valid_types:
        return False
    
    # 检查 data 是否为字典
    if not isinstance(message['data'], dict):
        return False
    
    return True


def process_message(message: Dict[str, Any], mq_client):
    """
    处理单条消息
    :param message: 消息内容
    :param mq_client: MQ 客户端
    """
    logger.info(f"收到消息：sensor_type={message.get('sensor_type')}, time={message.get('timestamp')}")
    
    # 1. 基本格式验证
    if not validate_basic_format(message):
        logger.warning(f"消息格式无效：{json.dumps(message, ensure_ascii=False)}")
        return
    
    # 2. 添加接收时间戳
    message['received_by_receiver'] = datetime.now().isoformat()
    
    # 3. 发布到验证队列
    try:
        success = mq_client.publish(Config.VALIDATED_QUEUE, message)
        if success:
            logger.info(f"✓ 已转发到验证队列：{message['sensor_type']}")
        else:
            logger.error(f"✗ 发布到验证队列失败：{message['sensor_type']}")
    except Exception as e:
        logger.error(f"✗ 发布异常：{str(e)}")


def start_receiver():
    """启动接收模块"""
    logger.info("="*60)
    logger.info("📥 数据接收模块启动")
    logger.info(f"MQ 类型：{Config.MQ_TYPE}")
    logger.info(f"输入流：{Config.RAW_DATA_STREAM}")
    logger.info(f"输出队列：{Config.VALIDATED_QUEUE}")
    logger.info(f"消费者：{Config.CONSUMER_NAME}")
    logger.info("="*60)
    
    # 连接 MQ
    mq_client = create_mq(
        Config.MQ_TYPE,
        host=Config.MQ_HOST,
        port=Config.MQ_PORT,
        db=Config.MQ_DB
    )
    
    if not mq_client.connect():
        logger.error("MQ 连接失败，退出")
        return
    
    logger.info("✅ MQ 连接成功")
    
    # 开始消费
    try:
        mq_client.consume(
            stream_name=Config.RAW_DATA_STREAM,
            consumer_group=Config.CONSUMER_GROUP,
            consumer_name=Config.CONSUMER_NAME,
            callback=lambda msg: process_message(msg, mq_client),
            block_timeout=1000
        )
    except KeyboardInterrupt:
        logger.info("\n🛑 收到停止信号")
    except Exception as e:
        logger.error(f"消费异常：{str(e)}")
    finally:
        mq_client.close()
        logger.info("✅ 接收模块已停止")


if __name__ == '__main__':
    start_receiver()
