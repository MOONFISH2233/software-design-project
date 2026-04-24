"""
数据写入模块 - 将验证后的数据写入MongoDB数据库或文件
功能：
1. 从写入队列读取数据
2. 支持MongoDB存储（主）和文件存储（备份/降级）
3. 按传感器类型分类存储
4. 支持批量写入和多实例并行运行
5. 自动故障转移（MongoDB失败时切换到文件模式）
"""

import sys
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

# 导入 MQ 工具
from mq_utils import create_mq

# 尝试导入 MongoDB 驱动
try:
    from pymongo import MongoClient, errors as mongo_errors
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False
    print("警告: pymongo 未安装，将使用文件存储模式")
    print("安装命令: pip install pymongo")

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
    STORAGE_MODE = 'mongodb'  # 可选值: 'mongodb', 'file', 'both'
    DATA_DIR = 'data'
    
    # MongoDB 配置
    MONGO_URI = 'mongodb://localhost:27017/'
    MONGO_DB_NAME = 'sensor_data'
    MONGO_POOL_SIZE = 50
    MONGO_MIN_POOL_SIZE = 10
    
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
    
    def __init__(self, data_dir: str, storage_mode: str):
        self.data_dir = data_dir
        self.storage_mode = storage_mode
        self.write_count = 0
        self.error_count = 0
        self.mongo_client = None
        self.mongo_db = None
        
        if self.storage_mode in ['mongodb', 'both']:
            self._init_mongo()
    
    def _init_mongo(self):
        try:
            self.mongo_client = MongoClient(
                Config.MONGO_URI,
                maxPoolSize=Config.MONGO_POOL_SIZE,
                minPoolSize=Config.MONGO_MIN_POOL_SIZE
            )
            self.mongo_db = self.mongo_client[Config.MONGO_DB_NAME]
            logger.info("✅ MongoDB 连接成功")
        except mongo_errors.ConnectionFailure as e:
            logger.error(f"✗ MongoDB 连接失败：{str(e)}")
            self.mongo_client = None
            self.mongo_db = None
    
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
    
    def write_data_mongo(self, message: Dict[str, Any]) -> Optional[str]:
        """
        写入数据到MongoDB
        :param message: 消息内容
        :return: 文档ID
        """
        if not self.mongo_db:
            logger.error("✗ MongoDB 连接不可用，无法写入")
            return None
        
        sensor_type = message.get('sensor_type', 'unknown')
        data = message.get('data', {})
        
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
            
            # 写入MongoDB
            result = self.mongo_db[sensor_type].insert_one(output_data)
            self.write_count += 1
            logger.info(f"✓ 数据已写入MongoDB：{result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"✗ 写入MongoDB失败：{str(e)}")
            return None
    
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
        # 尝试写入MongoDB
        if writer.storage_mode in ['mongodb', 'both']:
            mongo_id = writer.write_data_mongo(message)
            if mongo_id:
                logger.info(f"✓ 写入MongoDB成功：{mongo_id}")
                return
        
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
    writer = DataWriter(Config.DATA_DIR, Config.STORAGE_MODE)
    
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
