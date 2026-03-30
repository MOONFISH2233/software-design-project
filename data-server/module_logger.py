"""
日志记录模块 - 记录系统运行日志
功能：
1. 从日志队列读取所有消息
2. 记录到日志文件
3. 支持异常告警
4. 性能统计和监控
5. 支持多实例并行运行
"""

import sys
import json
import os
from datetime import datetime
from typing import Dict, Any
from collections import defaultdict

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
    
    # 队列（监听所有消息）
    LOG_QUEUE = 'sensor:logs'
    
    # 消费者组配置
    CONSUMER_GROUP = 'logger_group'
    CONSUMER_NAME = f'logger_{os.getpid()}'
    
    # 日志配置
    LOG_DIR = 'logs'
    SYSTEM_LOG_FILE = 'logs/system.log'
    ALERT_LOG_FILE = 'logs/alerts.log'
    STATS_INTERVAL = 60  # 统计间隔（秒）


# ================= 日志处理器 =================
class SystemLogger:
    """系统日志记录器"""
    
    def __init__(self):
        self.log_dir = Config.LOG_DIR
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 统计信息
        self.message_count = defaultdict(int)
        self.error_count = 0
        self.warning_count = 0
        self.start_time = datetime.now()
        self.last_stats_time = self.start_time
    
    def log_message(self, message: Dict[str, Any], category: str = 'info'):
        """
        记录消息
        :param message: 消息内容
        :param category: 类别 (info/error/warning/performance)
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 更新统计
        self.message_count[category] += 1
        if category == 'error':
            self.error_count += 1
        elif category == 'warning':
            self.warning_count += 1
        
        # 格式化日志
        log_entry = {
            'timestamp': timestamp,
            'category': category,
            'message': message
        }
        
        # 写入系统日志
        log_line = f"[{timestamp}] [{category.upper()}] {json.dumps(message, ensure_ascii=False)}\n"
        
        with open(Config.SYSTEM_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_line)
        
        # 如果是错误或警告，同时输出到控制台和告警日志
        if category in ['error', 'warning']:
            print(log_line.strip())
            
            with open(Config.ALERT_LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(log_line)
    
    def log_performance(self, metrics: Dict[str, Any]):
        """记录性能指标"""
        self.log_message(metrics, 'performance')
    
    def print_stats(self):
        """打印统计信息"""
        current_time = datetime.now()
        uptime = (current_time - self.start_time).total_seconds()
        
        print("\n" + "="*60)
        print("📊 日志模块统计")
        print("="*60)
        print(f"运行时长：{uptime:.0f} 秒")
        print(f"总消息数：{sum(self.message_count.values())}")
        print(f"  - INFO: {self.message_count['info']}")
        print(f"  - WARNING: {self.message_count['warning']}")
        print(f"  - ERROR: {self.message_count['error']}")
        print(f"  - PERFORMANCE: {self.message_count['performance']}")
        print(f"\n错误率：{(self.error_count / sum(self.message_count.values()) * 100) if sum(self.message_count.values()) > 0 else 0:.2f}%")
        print("="*60 + "\n")
    
    def should_print_stats(self) -> bool:
        """检查是否应该打印统计（每隔一段时间）"""
        current_time = datetime.now()
        if (current_time - self.last_stats_time).total_seconds() >= Config.STATS_INTERVAL:
            self.last_stats_time = current_time
            return True
        return False


# ================= 全局日志器 =================
system_logger = SystemLogger()


def process_message(message: Dict[str, Any]):
    """
    处理日志消息
    :param message: 消息内容
    """
    # 从消息中提取日志信息
    log_data = message.get('log_data', {})
    level = message.get('level', 'info')
    
    # 记录日志
    system_logger.log_message(log_data, level)
    
    # 检查是否需要告警
    if level == 'error':
        # 可以添加告警逻辑，如发送邮件、短信等
        pass


def start_logger():
    """启动日志模块"""
    print("="*60)
    print("📝 日志记录模块启动")
    print(f"MQ 类型：{Config.MQ_TYPE}")
    print(f"输入队列：{Config.LOG_QUEUE}")
    print(f"消费者：{Config.CONSUMER_NAME}")
    print(f"系统日志：{Config.SYSTEM_LOG_FILE}")
    print(f"告警日志：{Config.ALERT_LOG_FILE}")
    print("="*60)
    
    # 连接 MQ
    mq_client = create_mq(
        Config.MQ_TYPE,
        host=Config.MQ_HOST,
        port=Config.MQ_PORT,
        db=Config.MQ_DB
    )
    
    if not mq_client.connect():
        print("MQ 连接失败，退出")
        return
    
    print("✅ MQ 连接成功")
    
    # 开始消费
    try:
        mq_client.consume(
            stream_name=Config.LOG_QUEUE,
            consumer_group=Config.CONSUMER_GROUP,
            consumer_name=Config.CONSUMER_NAME,
            callback=lambda msg: process_message(msg),
            block_timeout=1000
        )
    except KeyboardInterrupt:
        print("\n🛑 收到停止信号")
    except Exception as e:
        print(f"消费异常：{str(e)}")
    finally:
        # 打印最终统计
        system_logger.print_stats()
        
        mq_client.close()
        print("✅ 日志模块已停止")


if __name__ == '__main__':
    start_logger()
