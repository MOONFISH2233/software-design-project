"""
数据写入模块 - 将验证后的数据写入文件
功能：
1. 从写入队列读取数据
2. 按传感器类型分类写入不同目录
3. 支持批量写入和文件轮转
4. 支持多实例并行运行
"""

import sys
import json
import os
from datetime import datetime
from typing import Dict, Any

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
    
    # 队列
    WRITE_QUEUE = 'sensor:write'
    
    # 消费者组配置
    CONSUMER_GROUP = 'writer_group'
    CONSUMER_NAME = f'writer_{os.getpid()}'
    
    # 数据存储配置
    DATA_DIR = 'data'
    
    # 日志配置
    LOG_FILE = 'logs/writer.log'


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
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_line)
        
        print(log_line.strip())


logger = SimpleLogger(Config.LOG_FILE)


# ================= 数据写入器 =================
class DataWriter:
    """数据写入器"""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.write_count = 0
        self.error_count = 0
    
    def get_sensor_directory(self, sensor_type: str) -> str:
        """
        获取传感器对应的目录
        :param sensor_type: 传感器类型
        :return: 目录路径
        """
        dir_map = {
            'skin': 'skin_sensor',
            'environment': 'environment',
            'device': 'device'
        }
        
        subdir = dir_map.get(sensor_type, sensor_type)
        full_path = os.path.join(self.data_dir, subdir)
        
        # 确保目录存在
        os.makedirs(full_path, exist_ok=True)
        
        return full_path
    
    def write_data(self, message: Dict[str, Any]) -> str:
        """
        写入数据到文件
        :param message: 消息内容
        :return: 文件名
        """
        sensor_type = message.get('sensor_type', 'unknown')
        data = message.get('data', {})
        
        # 获取目录
        directory = self.get_sensor_directory(sensor_type)
        
        # 生成文件名（使用时间戳 + 进程 ID 避免冲突）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f"{sensor_type}_{timestamp}_{os.getpid()}.json"
        filepath = os.path.join(directory, filename)
        
        try:
            # 添加元数据
            output_data = {
                **data,
                'metadata': {
                    'sensor_type': sensor_type,
                    'original_timestamp': message.get('timestamp'),
                    'received_at': message.get('received_at'),
                    'validated_at': message.get('validated_at'),
                    'written_at': datetime.now().isoformat(),
                    'worker_pid': os.getpid()
                }
            }
            
            # 写入文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            self.write_count += 1
            logger.info(f"✓ 数据已写入：{filepath}")
            return filename
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"✗ 写入失败：{str(e)}")
            raise
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        return {
            'write_count': self.write_count,
            'error_count': self.error_count
        }


def process_message(message: Dict[str, Any], writer: DataWriter):
    """
    处理单条消息
    :param message: 消息内容
    :param writer: 数据写入器
    """
    sensor_type = message.get('sensor_type')
    logger.info(f"写入数据：sensor_type={sensor_type}, time={message.get('timestamp')}")
    
    try:
        # 写入文件
        filename = writer.write_data(message)
        logger.info(f"✓ 写入成功：{filename}")
        
    except Exception as e:
        logger.error(f"✗ 写入异常：{str(e)}")
        # 可以选择重新发布到错误队列


def start_writer():
    """启动写入模块"""
    logger.info("="*60)
    logger.info("💾 数据写入模块启动")
    logger.info(f"MQ 类型：{Config.MQ_TYPE}")
    logger.info(f"输入队列：{Config.WRITE_QUEUE}")
    logger.info(f"数据目录：{Config.DATA_DIR}")
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
    
    # 创建数据写入器
    writer = DataWriter(Config.DATA_DIR)
    
    # 开始消费
    try:
        mq_client.consume(
            stream_name=Config.WRITE_QUEUE,
            consumer_group=Config.CONSUMER_GROUP,
            consumer_name=Config.CONSUMER_NAME,
            callback=lambda msg: process_message(msg, writer),
            block_timeout=1000
        )
    except KeyboardInterrupt:
        logger.info("\n🛑 收到停止信号")
    except Exception as e:
        logger.error(f"消费异常：{str(e)}")
    finally:
        # 打印统计
        stats = writer.get_stats()
        logger.info(f"📊 写入统计 - 成功：{stats['write_count']}, 失败：{stats['error_count']}")
        
        mq_client.close()
        logger.info("✅ 写入模块已停止")


if __name__ == '__main__':
    start_writer()
