"""
Flask 数据服务器
功能：接收数据、保存到文件、记录日志
版本：v2.0 - 高性能并发优化版
"""

from flask import Flask, request, jsonify
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import os
import json
import threading
import queue
import time
import random
from typing import Dict, Any

app = Flask(__name__)

# 创建日志目录和文件存储目录
LOG_DIR = 'logs'
DATA_DIR = 'data'
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)


class AsyncLogHandler(logging.Handler):
    """异步日志处理器 - 使用独立线程处理日志 I/O"""
    
    def __init__(self, handler, queue_size=1000):
        super().__init__()
        self.handler = handler
        self.queue = queue.Queue(maxsize=queue_size)
        self.shutdown_flag = False
        
        # 启动后台工作线程
        self.worker_thread = threading.Thread(target=self._process_logs, daemon=True)
        self.worker_thread.start()
    
    def _process_logs(self):
        """后台线程：处理日志队列"""
        while not self.shutdown_flag:
            try:
                # 等待新日志（超时 1 秒）
                try:
                    record = self.queue.get(timeout=1.0)
                    if record is None:  # 关闭信号
                        break
                    self.handler.emit(record)
                    self.queue.task_done()
                except queue.Empty:
                    continue
            except Exception as e:
                # 防止日志处理异常导致线程退出
                print(f"AsyncLogHandler error: {e}")
    
    def emit(self, record):
        """将日志记录加入队列"""
        try:
            # 队列满时丢弃 DEBUG/INFO 级别日志（保证系统性能）
            if self.queue.full():
                if record.levelno in (logging.DEBUG, logging.INFO):
                    return  # 丢弃低优先级日志
                else:
                    # ERROR/CRITICAL 等待队列有空位
                    self.queue.put(record, block=True, timeout=0.1)
            else:
                self.queue.put(record, block=False)
        except Exception:
            self.handleError(record)
    
    def close(self):
        """关闭处理器"""
        self.shutdown_flag = True
        # 发送关闭信号
        try:
            self.queue.put(None, block=False)
        except queue.Full:
            pass
        self.worker_thread.join(timeout=2.0)
        super().close()


class SamplingFilter(logging.Filter):
    """日志采样过滤器 - 按概率记录日志"""
    
    def __init__(self, sample_rate=0.1):
        """
        :param sample_rate: 采样率 (0.0-1.0), 例如 0.1 表示 10% 的日志会被记录
        """
        super().__init__()
        self.sample_rate = sample_rate
    
    def filter(self, record):
        # INFO 和 DEBUG 级别进行采样，其他级别全部记录
        if record.levelno in (logging.DEBUG, logging.INFO):
            return random.random() < self.sample_rate
        return True  # WARNING/ERROR/CRITICAL 全部记录


def setup_high_performance_logger():
    """配置高性能日志系统"""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  # 设置为 DEBUG，通过过滤器控制实际输出
    
    # 避免重复添加 handler
    if logger.handlers:
        return logger
    
    # 创建格式化器（JSON 格式，便于日志分析系统处理）
    class JsonFormatter(logging.Formatter):
        """JSON 格式化器 - 结构化日志"""
        
        def format(self, record):
            log_data = {
                'timestamp': datetime.now().isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'thread': record.threadName,
                'message': record.getMessage(),
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno
            }
            
            # 如果有异常信息，添加到日志
            if record.exc_info:
                log_data['exception'] = self.formatException(record.exc_info)
            
            return json.dumps(log_data, ensure_ascii=False)
    
    json_formatter = JsonFormatter()
    
    # 传统格式（可选，注释掉以节省空间）
    traditional_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [Thread:%(threadName)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器（仅警告及以上级别）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(traditional_formatter)
    
    # 文件处理器 - 使用轮转
    file_handler = RotatingFileHandler(
        f'{LOG_DIR}/server_{datetime.now().strftime("%Y%m%d")}.log',
        maxBytes=50*1024*1024,  # 50MB
        backupCount=10,  # 保留 10 个备份
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(json_formatter)
    
    # 添加采样过滤器（10% 采样率）
    sampling_filter = SamplingFilter(sample_rate=0.1)
    file_handler.addFilter(sampling_filter)
    
    # 包装为异步处理器
    async_handler = AsyncLogHandler(file_handler, queue_size=1000)
    
    # 错误专用处理器（不采样，单独文件）
    error_handler = RotatingFileHandler(
        f'{LOG_DIR}/error_{datetime.now().strftime("%Y%m%d")}.log',
        maxBytes=20*1024*1024,  # 20MB
        backupCount=15,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(json_formatter)
    error_async_handler = AsyncLogHandler(error_handler, queue_size=500)
    
    # 添加处理器
    logger.addHandler(async_handler)
    logger.addHandler(error_async_handler)
    logger.addHandler(console_handler)
    
    return logger


logger = setup_high_performance_logger()


class RequestStats:
    """请求统计类（线程安全）"""
    
    def __init__(self):
        self._count = 0
        self._lock = threading.Lock()
        self._last_log_time = datetime.now()
    
    def increment(self):
        with self._lock:
            self._count += 1
            current_time = datetime.now()
            
            # 每分钟记录一次统计
            if (current_time - self._last_log_time).total_seconds() >= 60:
                logger.info(f"请求统计 - 累计处理：{self._count} 次，QPS 估算：{self._count / ((current_time - self._last_log_time).total_seconds() or 1):.2f}")
                self._last_log_time = current_time
            
            return self._count
    
    @property
    def count(self):
        with self._lock:
            return self._count


# 全局请求统计
request_stats = RequestStats()


@app.route('/api/receive', methods=['POST'])
def receive_data():
    """
    接收数据的 API 接口
    支持 JSON 格式数据
    """
    start_time = datetime.now()
    
    try:
        # 获取请求数据
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        # 生成时间戳文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f'data_{timestamp}.json'
        filepath = os.path.join(DATA_DIR, filename)
        
        # 添加接收时间戳
        data['received_at'] = datetime.now().isoformat()
        
        # 保存到文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 更新统计
        request_stats.increment()
        
        # 计算处理耗时
        process_time = (datetime.now() - start_time).total_seconds()
        
        # 详细日志（DEBUG 级别，会被采样）
        logger.debug(f"数据保存成功 - 文件：{filename}, 大小：{len(str(data))} 字节，耗时：{process_time*1000:.2f}ms")
        
        # 慢请求告警（超过 100ms 的请求单独记录）
        if process_time > 0.1:
            logger.warning(f"慢请求检测 - 耗时：{process_time*1000:.2f}ms, 文件：{filename}")
        
        return jsonify({
            'status': 'success',
            'message': '数据接收成功',
            'filename': filename,
            'timestamp': data['received_at'],
            'process_time_ms': round(process_time * 1000, 2)
        })
    
    except Exception as e:
        process_time = (datetime.now() - start_time).total_seconds()
        logger.error(f"接收数据失败 - 错误：{str(e)}, 耗时：{process_time*1000:.2f}ms", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'service': 'Flask Data Server v2.0',
        'timestamp': datetime.now().isoformat(),
        'total_requests': request_stats.count,
        'uptime': 'running'
    })


@app.route('/api/logs', methods=['GET'])
def get_logs():
    """获取最近的日志"""
    try:
        log_files = sorted(os.listdir(LOG_DIR))
        if not log_files:
            return jsonify({'logs': [], 'message': '暂无日志'})
        
        # 读取最新的日志文件
        latest_log = log_files[-1]
        with open(os.path.join(LOG_DIR, latest_log), 'r', encoding='utf-8') as f:
            lines = f.readlines()[-100:]  # 返回最后 100 行
        
        return jsonify({
            'logs': ''.join(lines),
            'file': latest_log
        })
    except Exception as e:
        logger.error(f"获取日志失败：{str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取服务器统计信息"""
    return jsonify({
        'total_requests': request_stats.count,
        'current_time': datetime.now().isoformat(),
        'version': '2.0.0',
        'features': [
            '异步日志处理',
            '日志采样（10%）',
            '结构化 JSON 日志',
            '慢请求检测',
            '线程安全统计',
            '日志轮转'
        ]
    })


# ==================== 新增专用传感器 API 接口 ====================

def save_sensor_data(sensor_type: str, data: Dict[str, Any]) -> str:
    """
    保存传感器数据到独立目录
    :param sensor_type: 传感器类型
    :param data: 数据内容
    :return: 文件名
    """
    # 为不同类型的传感器创建独立目录
    sensor_dir = os.path.join(DATA_DIR, sensor_type)
    os.makedirs(sensor_dir, exist_ok=True)
    
    # 生成带时间戳的文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    filename = f'{sensor_type}_{timestamp}.json'
    filepath = os.path.join(sensor_dir, filename)
    
    # 添加元数据
    data['received_at'] = datetime.now().isoformat()
    data['sensor_type'] = sensor_type
    
    # 保存到文件
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return filename


@app.route('/api/sensor/skin', methods=['POST'])
def receive_skin_sensor():
    """
    皮肤传感器数据接口
    接收：水分度、油亮度等数据
    保存到：data/skin_sensor/ 目录
    """
    start_time = datetime.now()
    
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        # 验证必要字段
        required_fields = ['moisture', 'oiliness']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'缺少必要字段：{field}'
                }), 400
        
        # 保存数据
        filename = save_sensor_data('skin_sensor', data)
        
        process_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"皮肤传感器数据 - 文件：{filename}, 耗时：{process_time*1000:.2f}ms")
        
        return jsonify({
            'status': 'success',
            'message': '皮肤传感器数据接收成功',
            'filename': filename,
            'sensor_type': 'skin',
            'process_time_ms': round(process_time * 1000, 2)
        })
    
    except Exception as e:
        logger.error(f"皮肤传感器数据处理失败：{str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/sensor/environment', methods=['POST'])
def receive_environment_sensor():
    """
    环境传感器数据接口
    接收：湿度、光照度、温度等数据
    保存到：data/environment/ 目录
    """
    start_time = datetime.now()
    
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        # 验证必要字段
        required_fields = ['humidity', 'light_lux']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'缺少必要字段：{field}'
                }), 400
        
        # 保存数据
        filename = save_sensor_data('environment', data)
        
        process_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"环境传感器数据 - 文件：{filename}, 耗时：{process_time*1000:.2f}ms")
        
        return jsonify({
            'status': 'success',
            'message': '环境传感器数据接收成功',
            'filename': filename,
            'sensor_type': 'environment',
            'process_time_ms': round(process_time * 1000, 2)
        })
    
    except Exception as e:
        logger.error(f"环境传感器数据处理失败：{str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/device/status', methods=['POST'])
def receive_device_status():
    """
    设备状态数据接口
    接收：设备 ID、运行状态、电量等信息
    保存到：data/device/ 目录
    """
    start_time = datetime.now()
    
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        # 验证必要字段
        required_fields = ['device_id', 'status']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'缺少必要字段：{field}'
                }), 400
        
        # 保存数据
        filename = save_sensor_data('device', data)
        
        process_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"设备状态数据 - 文件：{filename}, 耗时：{process_time*1000:.2f}ms")
        
        return jsonify({
            'status': 'success',
            'message': '设备状态数据接收成功',
            'filename': filename,
            'sensor_type': 'device',
            'process_time_ms': round(process_time * 1000, 2)
        })
    
    except Exception as e:
        logger.error(f"设备状态数据处理失败：{str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("Flask 数据服务器 v2.0 启动...")
    logger.info("高性能模式已启用：异步日志 | 采样过滤 | 结构化输出")
    logger.info("=" * 60)
    
    # 生产环境建议使用 gunicorn 等 WSGI 服务器
    # 例如：gunicorn -w 4 -b 0.0.0.0:5000 app:app
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
