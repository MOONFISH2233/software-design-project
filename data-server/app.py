"""
Flask 数据服务器 - 支持加密和鉴权
功能：接收数据、保存到文件、记录日志、JWT 鉴权、AES 加密
版本：v3.0 - 安全增强版
"""

from flask import Flask, request, jsonify
from flask_httpauth import HTTPTokenAuth
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from functools import wraps
import jwt
import hashlib
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
import json
import logging
from logging.handlers import RotatingFileHandler
import threading
import queue
import random
import time
from typing import Dict, Any, Optional

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['JWT_EXPIRATION_HOURS'] = 24

# ==================== MySQL数据库配置 ====================
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin@localhost/sensor_project?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True
}

# 初始化数据库
db = SQLAlchemy(app)

# 初始化认证
auth = HTTPTokenAuth(scheme='Bearer')
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per minute", "1000 per hour"]
)

# 创建日志目录和文件存储目录
LOG_DIR = 'logs'
DATA_DIR = 'data'
SECURITY_DIR = 'security'
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(SECURITY_DIR, exist_ok=True)

# 将配置添加到 Flask app.config
app.config['LOG_DIR'] = LOG_DIR
app.config['DATA_DIR'] = DATA_DIR
app.config['SECURITY_DIR'] = SECURITY_DIR


# ==================== 日志处理类 ====================

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


# ==================== 日志配置 ====================

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


# ==================== 安全模块 ====================

class SecurityManager:
    """安全管理器 - 处理加密和鉴权"""
    
    def __init__(self):
        self.users_file = os.path.join(SECURITY_DIR, 'users.json')
        self.api_keys_file = os.path.join(SECURITY_DIR, 'api_keys.json')
        self.encryption_key_file = os.path.join(SECURITY_DIR, 'encryption.key')
        self._init_users()
        self._init_encryption()
        self._init_api_keys()
    
    def _init_users(self):
        """初始化用户系统"""
        if not os.path.exists(self.users_file):
            # 创建默认用户
            default_users = {
                'admin': {
                    'password_hash': self._hash_password('admin123'),
                    'role': 'admin',
                    'created_at': datetime.now().isoformat()
                },
                'user1': {
                    'password_hash': self._hash_password('user123'),
                    'role': 'user',
                    'created_at': datetime.now().isoformat()
                },
                'user2': {
                    'password_hash': self._hash_password('user123'),
                    'role': 'user',
                    'created_at': datetime.now().isoformat()
                },
                'user3': {
                    'password_hash': self._hash_password('user123'),
                    'role': 'user',
                    'created_at': datetime.now().isoformat()
                }
            }
            self._save_users(default_users)
            logger.info("已创建默认用户 (admin/user1/user2/user3)")
    
    def _init_encryption(self):
        """初始化加密密钥"""
        if not os.path.exists(self.encryption_key_file):
            key = Fernet.generate_key()
            with open(self.encryption_key_file, 'wb') as f:
                f.write(key)
            logger.info("已生成新的加密密钥")
        
        with open(self.encryption_key_file, 'rb') as f:
            self.key = f.read()
        self.cipher = Fernet(self.key)
    
    def _init_api_keys(self):
        """初始化 API Key"""
        if not os.path.exists(self.api_keys_file):
            api_keys = {
                'key_admin_001': {'user': 'admin', 'role': 'admin'},
                'key_user1_001': {'user': 'user1', 'role': 'user'},
                'key_user2_001': {'user': 'user2', 'role': 'user'},
                'key_user3_001': {'user': 'user3', 'role': 'user'}
            }
            with open(self.api_keys_file, 'w', encoding='utf-8') as f:
                json.dump(api_keys, f, indent=2, ensure_ascii=False)
            logger.info("已创建默认 API Keys")
    
    def _hash_password(self, password: str) -> str:
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username: str, password: str) -> Optional[str]:
        """用户认证，返回 JWT Token"""
        users = self._load_users()
        
        if username not in users:
            return None
        
        user = users[username]
        if user['password_hash'] != self._hash_password(password):
            return None
        
        # 生成 JWT Token
        token = jwt.encode({
            'username': username,
            'role': user['role'],
            'exp': datetime.now() + timedelta(hours=app.config['JWT_EXPIRATION_HOURS'])
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        # 将 bytes 解码为字符串
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        
        logger.info(f"用户 {username} 认证成功")
        return token
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """验证 JWT Token"""
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token 已过期")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Token 无效")
            return None
    
    def verify_api_key(self, api_key: str) -> Optional[Dict]:
        """验证 API Key"""
        try:
            with open(self.api_keys_file, 'r', encoding='utf-8') as f:
                api_keys = json.load(f)
            
            if api_key in api_keys:
                return api_keys[api_key]
            return None
        except Exception as e:
            logger.error(f"验证 API Key 失败：{e}")
            return None
    
    def encrypt_data(self, data: dict) -> str:
        """加密数据"""
        json_data = json.dumps(data, ensure_ascii=False)
        encrypted = self.cipher.encrypt(json_data.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_data(self, encrypted_data: str) -> dict:
        """解密数据"""
        try:
            decoded = base64.b64decode(encrypted_data)
            decrypted = self.cipher.decrypt(decoded)
            return json.loads(decrypted.decode())
        except Exception as e:
            logger.error(f"解密失败：{e}")
            raise ValueError("数据解密失败")
    
    def _load_users(self) -> dict:
        """加载用户数据"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_users(self, users: dict):
        """保存用户数据"""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
    
    def add_user(self, username: str, password: str, role: str = 'user') -> bool:
        """添加新用户"""
        users = self._load_users()
        if username in users:
            return False
        
        users[username] = {
            'password_hash': self._hash_password(password),
            'role': role,
            'created_at': datetime.now().isoformat()
        }
        self._save_users(users)
        logger.info(f"已添加用户：{username}")
        return True
    
    def generate_api_key(self, username: str) -> Optional[str]:
        """为用户生成新的 API Key"""
        users = self._load_users()
        if username not in users:
            return None
        
        api_key = f"key_{username}_{secrets.token_hex(8)}"
        try:
            with open(self.api_keys_file, 'r', encoding='utf-8') as f:
                api_keys = json.load(f)
            
            api_keys[api_key] = {'user': username, 'role': users[username]['role']}
            with open(self.api_keys_file, 'w', encoding='utf-8') as f:
                json.dump(api_keys, f, indent=2, ensure_ascii=False)
            
            logger.info(f"已为用户 {username} 生成 API Key: {api_key}")
            return api_key
        except Exception as e:
            logger.error(f"生成 API Key 失败：{e}")
            return None


# 全局安全管理器
security_manager = SecurityManager()


@auth.verify_token
def verify_token(token):
    """JWT Token 验证回调"""
    payload = security_manager.verify_token(token)
    if payload:
        return payload['username']
    return None


# ==================== 加密解密接口 ====================

@app.route('/api/encrypt', methods=['POST'])
@limiter.limit("20 per minute")
def encrypt_endpoint():
    """数据加密接口"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的 JSON 数据'}), 400
        
        encrypted = security_manager.encrypt_data(data)
        return jsonify({
            'status': 'success',
            'encrypted_data': encrypted,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"加密失败：{e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/decrypt', methods=['POST'])
@limiter.limit("20 per minute")
def decrypt_endpoint():
    """数据解密接口"""
    try:
        data = request.get_json()
        if not data or 'encrypted_data' not in data:
            return jsonify({'error': '缺少 encrypted_data 参数'}), 400
        
        decrypted = security_manager.decrypt_data(data['encrypted_data'])
        return jsonify({
            'status': 'success',
            'decrypted_data': decrypted,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"解密失败：{e}")
        return jsonify({'error': str(e)}), 500


# ==================== 认证接口 ====================

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """用户登录接口"""
    try:
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'error': '缺少用户名或密码'}), 400
        
        token = security_manager.authenticate(data['username'], data['password'])
        if token:
            return jsonify({
                'status': 'success',
                'token': token,
                'expires_in': app.config['JWT_EXPIRATION_HOURS'],
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': '用户名或密码错误'}), 401
    except Exception as e:
        logger.error(f"登录失败：{e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/apikey', methods=['POST'])
@limiter.limit("5 per minute")
def generate_api_key():
    """生成 API Key 接口"""
    try:
        # 需要 JWT Token 认证
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': '需要 JWT Token 认证'}), 401
        
        token = auth_header.split(' ')[1]
        payload = security_manager.verify_token(token)
        if not payload:
            return jsonify({'error': 'Token 无效或已过期'}), 401
        
        api_key = security_manager.generate_api_key(payload['username'])
        if api_key:
            return jsonify({
                'status': 'success',
                'api_key': api_key,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': '生成 API Key 失败'}), 500
    except Exception as e:
        logger.error(f"生成 API Key 失败：{e}")
        return jsonify({'error': str(e)}), 500


# ==================== 请求统计 ====================

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


# ==================== 健康检查接口 ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'service': 'Flask Data Server v3.0',
        'timestamp': datetime.now().isoformat(),
        'features': ['JWT Auth', 'API Key', 'AES Encryption']
    })


# ==================== 数据接收接口 ====================

@app.route('/api/receive', methods=['POST'])
def receive_data():
    """普通数据接收接口"""
    request_stats.increment()
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的 JSON 数据'}), 400
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f'data_{timestamp}.json'
        filepath = os.path.join(DATA_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"成功接收数据：{filename}")
        return jsonify({
            'status': 'success',
            'message': '数据接收成功',
            'filename': filename,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"数据接收失败：{e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/receive/secure', methods=['POST'])
@auth.login_required
@limiter.limit("50 per minute")
def receive_data_secure():
    """安全数据接收接口 (JWT 认证)"""
    request_stats.increment()
    try:
        username = auth.current_user()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '无效的 JSON 数据'}), 400
        
        # 检查是否为加密数据
        is_encrypted = data.get('encrypted', False)
        if is_encrypted:
            encrypted_data = data.get('data', '')
            try:
                data = security_manager.decrypt_data(encrypted_data)
            except Exception as e:
                return jsonify({'error': '数据解密失败'}), 400
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f'secure_{username}_{timestamp}.json'
        filepath = os.path.join(DATA_DIR, filename)
        
        save_data = {
            'metadata': {
                'username': username,
                'received_at': datetime.now().isoformat(),
                'encrypted': is_encrypted
            },
            'payload': data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"用户 {username} - 安全接收数据：{filename}")
        return jsonify({
            'status': 'success',
            'message': '数据接收成功',
            'filename': filename,
            'request_id': secrets.token_hex(8),
            'timestamp': datetime.now().isoformat(),
            'elapsed_ms': 0
        })
    except Exception as e:
        logger.error(f"安全数据接收失败：{e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/receive/apikey', methods=['POST'])
@limiter.limit("50 per minute")
def receive_data_apikey():
    """API Key 认证数据接收接口"""
    request_stats.increment()
    try:
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': '缺少 X-API-Key 请求头'}), 401
        
        key_info = security_manager.verify_api_key(api_key)
        if not key_info:
            return jsonify({'error': '无效的 API Key'}), 401
        
        username = key_info['user']
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '无效的 JSON 数据'}), 400
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f'apikey_{username}_{timestamp}.json'
        filepath = os.path.join(DATA_DIR, filename)
        
        save_data = {
            'metadata': {
                'username': username,
                'received_at': datetime.now().isoformat(),
                'api_key_auth': True
            },
            'payload': data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"用户 {username} (API Key) - 接收数据：{filename}")
        return jsonify({
            'status': 'success',
            'message': '数据接收成功',
            'filename': filename,
            'request_id': secrets.token_hex(8),
            'timestamp': datetime.now().isoformat(),
            'elapsed_ms': 0
        })
    except Exception as e:
        logger.error(f"API Key 数据接收失败：{e}")
        return jsonify({'error': str(e)}), 500


# ==================== 传感器专用接口 ====================

def save_sensor_data(data: dict, sensor_type: str) -> str:
    """保存传感器数据到独立目录"""
    sensor_dirs = {
        'skin': 'skin_sensor',
        'environment': 'environment',
        'device': 'device'
    }
    
    dir_name = sensor_dirs.get(sensor_type, 'data')
    save_dir = os.path.join(app.config['DATA_DIR'], dir_name)
    
    if not os.path.exists(save_dir):
        os.makedirs(save_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
    filename = f"data_{timestamp}.json"
    filepath = os.path.join(save_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"成功保存 {sensor_type} 数据：{filename}")
    return filename


@app.route('/api/sensor/skin', methods=['POST'])
@limiter.limit("100 per minute")
def skin_sensor():
    """皮肤传感器数据接口"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的 JSON 数据'}), 400
        
        # 验证必要字段
        required_fields = ['moisture', 'oiliness']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必要字段: {field}'}), 400
        
        # 添加元数据
        data['sensor_type'] = 'skin'
        data['timestamp'] = datetime.now().isoformat()
        
        # 保存数据
        filename = save_sensor_data(data, 'skin')
        
        return jsonify({
            'status': 'success',
            'message': '皮肤传感器数据接收成功',
            'filename': filename,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"皮肤传感器数据处理失败：{e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/sensor/environment', methods=['POST'])
@limiter.limit("100 per minute")
def environment_sensor():
    """环境传感器数据接口"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的 JSON 数据'}), 400
        
        # 验证必要字段
        required_fields = ['humidity', 'light_lux', 'temperature']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必要字段: {field}'}), 400
        
        # 添加元数据
        data['sensor_type'] = 'environment'
        data['timestamp'] = datetime.now().isoformat()
        
        # 保存数据
        filename = save_sensor_data(data, 'environment')
        
        return jsonify({
            'status': 'success',
            'message': '环境传感器数据接收成功',
            'filename': filename,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"环境传感器数据处理失败：{e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/device/status', methods=['POST'])
@limiter.limit("50 per minute")
def device_status():
    """设备状态接口"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的 JSON 数据'}), 400
        
        # 验证必要字段
        if 'device_id' not in data:
            return jsonify({'error': '缺少必要字段: device_id'}), 400
        
        # 添加元数据
        data['sensor_type'] = 'device'
        data['timestamp'] = datetime.now().isoformat()
        
        # 保存数据
        filename = save_sensor_data(data, 'device')
        
        return jsonify({
            'status': 'success',
            'message': '设备状态数据接收成功',
            'filename': filename,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"设备状态数据处理失败：{e}")
        return jsonify({'error': str(e)}), 500


# ==================== 数据统计接口 ====================

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取数据统计信息"""
    try:
        data_dir = app.config['DATA_DIR']
        stats = {
            'total_files': 0,
            'total_size': 0,
            'directories': {}
        }
        
        if os.path.exists(data_dir):
            for root, dirs, files in os.walk(data_dir):
                for file in files:
                    if file.endswith('.json'):
                        filepath = os.path.join(root, file)
                        stats['total_files'] += 1
                        stats['total_size'] += os.path.getsize(filepath)
                        
                        # 统计各目录文件数
                        dir_name = os.path.basename(root)
                        if dir_name not in stats['directories']:
                            stats['directories'][dir_name] = 0
                        stats['directories'][dir_name] += 1
        
        stats['total_size_mb'] = round(stats['total_size'] / (1024 * 1024), 2)
        
        return jsonify({
            'status': 'success',
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"获取统计信息失败：{e}")
        return jsonify({'error': str(e)}), 500


# ==================== MySQL路由注册 ====================
try:
    from routes.mysql_routes import mysql_bp
    app.register_blueprint(mysql_bp)
    print("✅ MySQL路由注册成功")
except Exception as e:
    print(f"⚠️  MySQL路由注册失败: {e}")


# ==================== 小程序路由注册 ====================
try:
    from routes.miniprogram_routes import init_app as init_miniprogram
    init_miniprogram(app)
    print("✅ 小程序路由注册成功")
except Exception as e:
    print(f"⚠️  小程序路由注册失败: {e}")


# ==================== 主程序入口 ====================

if __name__ == '__main__':
    # 打印启动信息
    print("=" * 60)
    print("Flask 数据服务器 v3.0 - 安全增强版")
    print("=" * 60)
    print(f"数据保存目录：{os.path.abspath(DATA_DIR)}")
    print(f"日志目录：{os.path.abspath(LOG_DIR)}")
    print(f"安全配置目录：{os.path.abspath(SECURITY_DIR)}")
    print("=" * 60)
    print("默认用户账户：")
    print("  - admin / admin123 (管理员)")
    print("  - user1 / user123 (普通用户)")
    print("  - user2 / user123 (普通用户)")
    print("  - user3 / user123 (普通用户)")
    print("=" * 60)
    print("API 接口：")
    print("  认证接口：/api/auth/login")
    print("  数据接收（普通）：/api/receive")
    print("  数据接收（JWT 认证）：/api/receive/secure")
    print("  数据接收（API Key）：/api/receive/apikey")
    print("  数据加密：/api/encrypt")
    print("  数据解密：/api/decrypt")
    print("  健康检查：/api/health")
    print("=" * 60)
    print("MySQL API 接口：")
    print("  设备管理：/api/mysql/devices [GET/POST/PUT/DELETE]")
    print("  皮肤数据：/api/mysql/skin-data [GET/POST]")
    print("  环境数据：/api/mysql/environment-data [GET]")
    print("  统计数据：/api/mysql/statistics [GET]")
    print("  用户管理：/api/mysql/users [GET]")
    print("=" * 60)
    
    # 启动服务器
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
