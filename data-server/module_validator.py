"""
数据验证模块 - 验证传感器数据的合理性
功能：
1. 从验证队列读取数据
2. 验证数据是否在合理范围内
3. 过滤无效数据
4. 将有效数据发布到写入队列
5. 支持多实例并行运行
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
    
    # 队列
    VALIDATED_QUEUE = 'sensor:validated'
    WRITE_QUEUE = 'sensor:write'
    
    # 消费者组配置
    CONSUMER_GROUP = 'validator_group'
    CONSUMER_NAME = f'validator_{os.getpid()}'
    
    # 日志配置
    LOG_FILE = 'logs/validator.log'


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


# ================= 数据验证规则 =================
class ValidationRules:
    """数据验证规则"""
    
    @staticmethod
    def validate_skin_sensor(data: Dict[str, Any]) -> tuple:
        """
        验证皮肤传感器数据
        :return: (是否有效，错误信息)
        """
        moisture = data.get('moisture', 0)
        oiliness = data.get('oiliness', 0)
        
        # 水分度：0-100%
        if not (0 <= moisture <= 100):
            return False, f"水分度超出范围：{moisture}"
        
        # 油亮度：0-100%
        if not (0 <= oiliness <= 100):
            return False, f"油亮度超出范围：{oiliness}"
        
        return True, None
    
    @staticmethod
    def validate_environment(data: Dict[str, Any]) -> tuple:
        """
        验证环境传感器数据
        :return: (是否有效，错误信息)
        """
        humidity = data.get('humidity', 0)
        light_lux = data.get('light_lux', 0)
        temperature = data.get('temperature', 25.0)
        
        # 湿度：0-100%
        if not (0 <= humidity <= 100):
            return False, f"湿度超出范围：{humidity}"
        
        # 光照度：0-10000 Lux
        if not (0 <= light_lux <= 10000):
            return False, f"光照度超出范围：{light_lux}"
        
        # 温度：-20 到 60℃
        if not (-20 <= temperature <= 60):
            return False, f"温度超出范围：{temperature}"
        
        return True, None
    
    @staticmethod
    def validate_device(data: Dict[str, Any]) -> tuple:
        """
        验证设备状态数据
        :return: (是否有效，错误信息)
        """
        device_id = data.get('device_id', '')
        status = data.get('status', '')
        
        # 设备 ID 不能为空
        if not device_id:
            return False, "设备 ID 为空"
        
        # 状态必须为有效值
        valid_status = ['online', 'offline', 'running', 'error', 'standby']
        if status not in valid_status:
            return False, f"无效的设备状态：{status}"
        
        return True, None


def validate_data(message: Dict[str, Any]) -> tuple:
    """
    验证数据
    :param message: 消息内容
    :return: (是否有效，错误信息)
    """
    sensor_type = message.get('sensor_type')
    data = message.get('data', {})
    
    if sensor_type == 'skin':
        return ValidationRules.validate_skin_sensor(data)
    elif sensor_type == 'environment':
        return ValidationRules.validate_environment(data)
    elif sensor_type == 'device':
        return ValidationRules.validate_device(data)
    else:
        return False, f"未知的传感器类型：{sensor_type}"


def process_message(message: Dict[str, Any], mq_client):
    """
    处理单条消息
    :param message: 消息内容
    :param mq_client: MQ 客户端
    """
    logger.info(f"验证数据：sensor_type={message.get('sensor_type')}, time={message.get('timestamp')}")
    
    # 1. 验证数据
    is_valid, error_msg = validate_data(message)
    
    if not is_valid:
        logger.warning(f"数据验证失败：{error_msg} - {json.dumps(message.get('data'), ensure_ascii=False)}")
        # 可以选择发布到错误队列（这里简单记录）
        return
    
    # 2. 添加验证时间戳和标记
    message['validated_at'] = datetime.now().isoformat()
    message['validation_passed'] = True
    
    # 3. 发布到写入队列
    try:
        success = mq_client.publish(Config.WRITE_QUEUE, message)
        if success:
            logger.info(f"✓ 验证通过，已转发到写入队列：{message['sensor_type']}")
        else:
            logger.error(f"✗ 发布到写入队列失败：{message['sensor_type']}")
    except Exception as e:
        logger.error(f"✗ 发布异常：{str(e)}")


def start_validator():
    """启动验证模块"""
    logger.info("="*60)
    logger.info("✅ 数据验证模块启动")
    logger.info(f"MQ 类型：{Config.MQ_TYPE}")
    logger.info(f"输入队列：{Config.VALIDATED_QUEUE}")
    logger.info(f"输出队列：{Config.WRITE_QUEUE}")
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
            stream_name=Config.VALIDATED_QUEUE,
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
        logger.info("✅ 验证模块已停止")


if __name__ == '__main__':
    start_validator()
