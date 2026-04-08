"""
消息队列配置和工具类
支持 Redis 和 RabbitMQ 两种后端
"""

import json
import redis
import pika
from datetime import datetime
from typing import Dict, Any, Optional, Callable
import threading


class RedisMQ:
    """基于 Redis Stream 的消息队列"""
    
    def __init__(self, host='localhost', port=6379, db=0, socket_timeout=5, socket_connect_timeout=5):
        """
        初始化 Redis MQ
        :param host: Redis 服务器地址
        :param port: Redis 端口
        :param db: Redis 数据库编号
        :param socket_timeout: socket 超时时间（秒）
        :param socket_connect_timeout: socket 连接超时时间（秒）
        """
        self.host = host
        self.port = port
        self.db = db
        self.socket_timeout = socket_timeout
        self.socket_connect_timeout = socket_connect_timeout
        self.redis_client = None
        self.connected = False
    
    def connect(self):
        """连接到 Redis"""
        try:
            print(f"🔄 正在连接 Redis: {self.host}:{self.port}...")
            self.redis_client = redis.Redis(
                host=self.host, 
                port=self.port, 
                db=self.db, 
                decode_responses=True,
                socket_timeout=self.socket_timeout,
                socket_connect_timeout=self.socket_connect_timeout,
                retry_on_timeout=False,  # 禁用自动重试
                health_check_interval=0  # 禁用健康检查
            )
            # 使用 ping 测试连接，设置明确的超时
            result = self.redis_client.ping()
            if result:
                self.connected = True
                print("✅ Redis 连接成功")
                return True
            else:
                print("❌ Redis ping 失败")
                self.connected = False
                return False
        except redis.exceptions.TimeoutError:
            print(f"❌ Redis 连接超时：无法在 {self.socket_connect_timeout} 秒内连接到 {self.host}:{self.port}")
            print("💡 请检查：")
            print("   1. 服务器 IP 地址是否正确")
            print("   2. 防火墙是否开放 6379 端口")
            print("   3. 阿里云安全组是否开放 6379 端口")
            print("   4. Redis 服务是否正常运行")
            self.connected = False
            return False
        except redis.exceptions.ConnectionError as e:
            print(f"❌ Redis 连接失败：{e}")
            print("💡 请检查网络连接和 Redis 服务状态")
            self.connected = False
            return False
        except Exception as e:
            print(f"❌ Redis 连接异常：{type(e).__name__}: {e}")
            print("💡 请检查网络连接和 Redis 服务状态")
            self.connected = False
            return False
    
    def publish(self, stream_name: str, message: Dict[str, Any]) -> bool:
        """
        发布消息到流
        :param stream_name: 流名称
        :param message: 消息内容（字典）
        :return: 是否成功
        """
        try:
            # 添加时间戳
            message['timestamp'] = datetime.now().isoformat()
            
            # 转换为字符串格式
            message_data = {k: str(v) for k, v in message.items()}
            
            # 添加到流
            self.redis_client.xadd(stream_name, message_data)
            return True
        except Exception as e:
            print(f"❌ 发布消息失败：{e}")
            return False
    
    def consume(self, stream_name: str, consumer_group: str, consumer_name: str, 
                callback: Callable, block_timeout: int = 1000):
        """
        消费消息（使用消费者组）
        :param stream_name: 流名称
        :param consumer_group: 消费者组名称
        :param consumer_name: 消费者名称
        :param callback: 消息处理回调函数
        :param block_timeout: 阻塞超时时间（毫秒）
        """
        try:
            # 创建消费者组（如果不存在）
            try:
                self.redis_client.xgroup_create(
                    stream_name, 
                    consumer_group, 
                    id='0', 
                    mkstream=True
                )
                print(f"✅ 创建消费者组：{consumer_group} - {stream_name}")
            except Exception:
                # 组已存在
                pass
            
            while True:
                try:
                    # 读取消息
                    messages = self.redis_client.xreadgroup(
                        groupname=consumer_group,
                        consumername=consumer_name,
                        streams={stream_name: '>'},
                        count=1,
                        block=block_timeout
                    )
                    
                    if messages:
                        for stream, msgs in messages:
                            for msg_id, msg_data in msgs:
                                try:
                                    # 调用回调函数处理消息
                                    callback(msg_data)
                                    
                                    # 确认消息已处理
                                    self.redis_client.xack(stream_name, consumer_group, msg_id)
                                except Exception as e:
                                    print(f"❌ 处理消息失败：{e}")
                                    # 不确认消息，稍后会重新投递
                    else:
                        # 没有新消息，继续等待
                        continue
                        
                except KeyboardInterrupt:
                    print("\n🛑 消费者停止")
                    break
                except Exception as e:
                    print(f"❌ 消费消息异常：{e}")
                    import time
                    time.sleep(1)  # 避免频繁重试
                    
        except Exception as e:
            print(f"❌ 消费者启动失败：{e}")
    
    def get_stream_length(self, stream_name: str) -> int:
        """获取流中消息数量"""
        try:
            return self.redis_client.xlen(stream_name)
        except:
            return 0
    
    def close(self):
        """关闭连接"""
        if self.redis_client:
            self.redis_client.close()
            self.connected = False


class RabbitMQ:
    """基于 RabbitMQ 的消息队列"""
    
    def __init__(self, host='localhost', port=5672, username='guest', password='guest'):
        """
        初始化 RabbitMQ
        :param host: RabbitMQ 服务器地址
        :param port: RabbitMQ 端口
        :param username: 用户名
        :param password: 密码
        """
        self.host = host
        self.port = port
        self.credentials = pika.PlainCredentials(username, password)
        self.connection = None
        self.channel = None
    
    def connect(self):
        """连接到 RabbitMQ"""
        try:
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=self.credentials
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            print("✅ RabbitMQ 连接成功")
            return True
        except Exception as e:
            print(f"❌ RabbitMQ 连接失败：{e}")
            return False
    
    def declare_queue(self, queue_name: str, durable: bool = True):
        """
        声明队列
        :param queue_name: 队列名称
        :param durable: 是否持久化
        """
        if self.channel:
            self.channel.queue_declare(queue=queue_name, durable=durable)
    
    def publish(self, queue_name: str, message: Dict[str, Any]) -> bool:
        """
        发布消息到队列
        :param queue_name: 队列名称
        :param message: 消息内容
        :return: 是否成功
        """
        try:
            # 确保队列存在
            self.declare_queue(queue_name)
            
            # 序列化消息
            body = json.dumps(message, ensure_ascii=False)
            
            # 发布消息
            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=body,
                properties=pika.BasicProperties(
                    delivery_mode=2  # 持久化
                )
            )
            return True
        except Exception as e:
            print(f"❌ 发布消息失败：{e}")
            return False
    
    def consume(self, queue_name: str, callback: Callable, auto_ack: bool = False):
        """
        消费消息
        :param queue_name: 队列名称
        :param callback: 消息处理回调函数
        :param auto_ack: 是否自动确认
        """
        try:
            # 确保队列存在
            self.declare_queue(queue_name)
            
            def on_message(ch, method, properties, body):
                try:
                    message = json.loads(body)
                    callback(message)
                    
                    if not auto_ack:
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as e:
                    print(f"❌ 处理消息失败：{e}")
                    if not auto_ack:
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            
            # 设置预取数量
            self.channel.basic_qos(prefetch_count=1)
            
            # 开始消费
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=on_message
            )
            
            print(f"✅ 开始消费队列：{queue_name}")
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            print("\n🛑 消费者停止")
            if self.connection:
                self.connection.close()
        except Exception as e:
            print(f"❌ 消费消息异常：{e}")
    
    def close(self):
        """关闭连接"""
        if self.connection and self.connection.is_open:
            self.connection.close()
            print("RabbitMQ 连接已关闭")


# 工厂函数，根据配置返回不同的 MQ 实例
def create_mq(mq_type='redis', **kwargs):
    """
    创建消息队列实例
    :param mq_type: 'redis' 或 'rabbitmq'
    :param kwargs: 连接参数
    :return: MQ 实例
    """
    if mq_type == 'redis':
        return RedisMQ(
            host=kwargs.get('host', 'localhost'),
            port=kwargs.get('port', 6379),
            db=kwargs.get('db', 0),
            socket_timeout=kwargs.get('socket_timeout', 5),
            socket_connect_timeout=kwargs.get('socket_connect_timeout', 5)
        )
    elif mq_type == 'rabbitmq':
        return RabbitMQ(
            host=kwargs.get('host', 'localhost'),
            port=kwargs.get('port', 5672),
            username=kwargs.get('username', 'guest'),
            password=kwargs.get('password', 'guest')
        )
    else:
        raise ValueError(f"不支持的消息队列类型：{mq_type}")


if __name__ == '__main__':
    # 测试示例
    print("测试 Redis MQ...")
    mq = create_mq('redis', host='localhost')
    if mq.connect():
        # 发布测试消息
        mq.publish('test_stream', {'message': 'Hello MQ', 'id': 1})
        print(f"流长度：{mq.get_stream_length('test_stream')}")
        mq.close()
