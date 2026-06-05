"""
小程序相关API路由
实现用户管理、设备管理、数据查询、健康报告、社区功能等接口
"""

from flask import Blueprint, request, jsonify
from models import db, User, Device, SkinSensorData, EnvironmentSensorData, DailyStatistics
from datetime import datetime, timedelta
from functools import wraps
import jwt
import logging
import json
import hashlib
import re
import uuid
import os
from sqlalchemy import func, case, or_
from werkzeug.security import generate_password_hash, check_password_hash

# 创建蓝图
miniprogram_bp = Blueprint('miniprogram', __name__, url_prefix='/api/miniprogram')

# 配置日志
logger = logging.getLogger(__name__)

# JWT密钥（应从配置文件读取）
JWT_SECRET_KEY = 'your-secret-key-change-in-production'


def hash_password(password):
    return generate_password_hash(str(password or ''))


def is_hashed_password(value):
    text = str(value or '')
    return text.startswith(('pbkdf2:', 'scrypt:', 'argon2:'))


def verify_password(stored_hash, password):
    stored = str(stored_hash or '')
    if is_hashed_password(stored):
        try:
            return check_password_hash(stored, str(password or ''))
        except Exception:
            return False
    return stored == str(password or '')


def stable_number(*parts):
    key = '|'.join(str(part) for part in parts)
    digest = hashlib.sha256(key.encode('utf-8')).hexdigest()
    return int(digest[:16], 16)


def stable_float(key, low, high, digits=1):
    span = high - low
    value = low + (stable_number(key) % 1000000) / 999999 * span
    return round(value, digits)


def stable_int(key, low, high):
    return int(low + stable_number(key) % (high - low + 1))


def stable_phone(username):
    return f"188{stable_int('account-phone:' + str(username), 10000000, 99999999)}"


def average_numeric(values, digits=1):
    values = [safe_float(value, None) for value in values if value is not None]
    values = [value for value in values if value is not None]
    if not values:
        return None
    return round(sum(values) / len(values), digits)


# =====================================================
# 认证装饰器
# =====================================================
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # 从请求头获取token
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'success': False, 'message': '缺少认证token'}), 401
        
        try:
            # 解码token
            data = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'success': False, 'message': '用户不存在'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': '无效的Token'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated


# =====================================================
# 认证相关接口（兼容小程序调用路径）
# =====================================================
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def auth_login():
    """用户登录（兼容 /api/auth/login 路径）"""
    # 直接调用 miniprogram_bp 的登录逻辑
    from flask import request as flask_request
    return login()


# =====================================================
# 简短路径兼容层（供小程序直接调用）
# =====================================================
short_path_bp = Blueprint('short_paths', __name__)

@short_path_bp.route('/device/list', methods=['GET'])
@token_required
def short_device_list(current_user):
    """设备列表（兼容小程序 /device/list 调用）"""
    # 转发到 miniprogram_bp 的处理函数
    return get_device_list(current_user)

@short_path_bp.route('/data/skin', methods=['GET'])
@token_required
def short_skin_data(current_user):
    """皮肤数据（兼容小程序 /data/skin 调用）"""
    return get_skin_data(current_user)

@short_path_bp.route('/data/environment', methods=['GET'])
@token_required
def short_environment_data(current_user):
    """环境数据（兼容小程序 /data/environment 调用）"""
    return get_environment_data(current_user)

@short_path_bp.route('/data/statistics', methods=['GET'])
@token_required
def short_statistics(current_user):
    """统计数据（兼容小程序 /data/statistics 调用）"""
    return get_statistics(current_user)

@short_path_bp.route('/notification/list', methods=['GET'])
@token_required
def short_notification_list(current_user):
    """通知列表（兼容小程序 /notification/list 调用）"""
    return get_notification_list(current_user)


# =====================================================
# 用户管理接口
# =====================================================

@miniprogram_bp.route('/user/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['username', 'password', 'phone']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'缺少必填字段: {field}'}), 400
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'success': False, 'message': '用户名已存在'}), 409
        
        # 检查手机号是否已存在
        if User.query.filter_by(phone=data['phone']).first():
            return jsonify({'success': False, 'message': '手机号已注册'}), 409
        
        # 创建新用户
        new_user = User(
            username=data['username'],
            password_hash=hash_password(data['password']),
            phone=data['phone'],
            nickname=data.get('nickname', data['username']),
            email=data.get('email'),
            role='user',
            status='active'
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        logger.info(f"用户注册成功: {data['username']}")
        
        return jsonify({
            'success': True,
            'message': '注册成功',
            'user_id': new_user.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"用户注册失败: {str(e)}")
        return jsonify({'success': False, 'message': f'注册失败: {str(e)}'}), 500


@miniprogram_bp.route('/user/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        ensure_admin_account()
        data = request.get_json()
        
        if 'username' not in data or 'password' not in data:
            return jsonify({'success': False, 'message': '缺少用户名或密码'}), 400
        
        # 查找用户
        user = User.query.filter_by(username=data['username']).first()
        
        if not user:
            return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
        
        # 验证密码（实际应使用bcrypt.check_password_hash）
        if not verify_password(user.password_hash, data['password']):
            return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
        
        if user.status != 'active':
            return jsonify({'success': False, 'message': '账户已被禁用'}), 403
        
        # 生成JWT token
        token_bytes = jwt.encode({
            'user_id': user.id,
            'username': user.username,
            'exp': datetime.utcnow() + timedelta(days=7)
        }, JWT_SECRET_KEY, algorithm='HS256')
        
        # PyJWT 2.x返回bytes，需要解码为str
        if isinstance(token_bytes, bytes):
            token = token_bytes.decode('utf-8')
        else:
            token = token_bytes
        
        # 更新最后登录时间
        if not is_hashed_password(user.password_hash):
            user.password_hash = hash_password(data['password'])
        user.last_login = datetime.now()
        db.session.commit()
        
        logger.info(f"用户登录成功: {user.username}")
        
        return jsonify({
            'success': True,
            'message': '登录成功',
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'nickname': user.nickname,
                'avatar_url': user.avatar_url,
                'role': user.role,
                'permissions': user_permissions(user)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"用户登录失败: {str(e)}")
        return jsonify({'success': False, 'message': f'登录失败: {str(e)}'}), 500


@miniprogram_bp.route('/user/profile', methods=['GET'])
@token_required
def get_user_profile(current_user):
    """获取用户信息"""
    try:
        return jsonify({
            'success': True,
            'user': current_user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"获取用户信息失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@miniprogram_bp.route('/user/profile', methods=['PUT'])
@token_required
def update_user_profile(current_user):
    """更新用户信息"""
    try:
        data = request.get_json()
        
        # 允许更新的字段
        updatable_fields = ['nickname', 'email', 'avatar_url']
        
        for field in updatable_fields:
            if field in data:
                setattr(current_user, field, data[field])
        
        db.session.commit()
        
        logger.info(f"用户信息更新成功: {current_user.username}")
        
        return jsonify({
            'success': True,
            'message': '更新成功',
            'user': current_user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新用户信息失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


# =====================================================
# 设备管理接口
# =====================================================

DEVICE_ID_PATTERN = re.compile(r'^[A-Za-z0-9_-]{3,20}$')


def normalize_device_payload(data):
    """Clean user input for device creation/binding."""
    data = data or {}
    device_id = str(data.get('device_id', '')).strip().upper()
    device_type = str(data.get('device_type') or data.get('type') or '').strip().lower()
    if device_type in ('env', 'environment_sensor', '环境'):
        device_type = 'environment'
    elif device_type in ('skin_sensor', 'mirror', '皮肤'):
        device_type = 'skin'
    elif device_id.startswith('ENV'):
        device_type = 'environment'
    elif not device_type:
        device_type = 'skin'

    return {
        'device_id': device_id,
        'device_type': device_type,
        'firmware_version': str(data.get('firmware_version') or 'v1.0.0').strip()[:20],
        'location': str(data.get('location') or '演示区域').strip()[:100],
        'is_primary': bool(data.get('is_primary', False)),
    }


def seed_device_data(device):
    """Insert one fresh row so a newly added device has data immediately."""
    now = datetime.now().replace(microsecond=0)
    request_id = 'seed-{}'.format(uuid.uuid4().hex[:16])
    province = province_from_location(getattr(device, 'location', None))
    values = demo_values_for_province(province) if province else None

    if device.device_type == 'environment' or device.device_id.startswith('ENV'):
        row = EnvironmentSensorData(
            device_id=device.device_id,
            temperature=values['environment_temperature'] if values else stable_float(f"{device.device_id}:env-temp", 23.0, 28.5),
            humidity=values['humidity'] if values else stable_float(f"{device.device_id}:humidity", 42.0, 68.0),
            pm25=values['pm25'] if values else stable_int(f"{device.device_id}:pm25", 8, 38),
            co2=values['co2'] if values else stable_int(f"{device.device_id}:co2", 480, 880),
            location=device.location,
            sensor_time=now,
            received_at=now,
            client_ip='web-admin',
            request_id=request_id,
            validated=True,
            quality_score=0.96,
            created_at=now
        )
    else:
        row = SkinSensorData(
            device_id=device.device_id,
            moisture=values['moisture'] if values else stable_int(f"{device.device_id}:moisture", 38, 62),
            oiliness=values['oiliness'] if values else stable_int(f"{device.device_id}:oiliness", 28, 58),
            temperature=values['skin_temperature'] if values else stable_float(f"{device.device_id}:skin-temp", 32.0, 34.5),
            sensor_time=now,
            received_at=now,
            client_ip='web-admin',
            request_id=request_id,
            validated=True,
            quality_score=0.96,
            created_at=now
        )

    db.session.add(row)


def user_has_active_device(current_user, device_id):
    from models import DeviceBinding
    return DeviceBinding.query.filter_by(
        user_id=current_user.id,
        device_id=device_id,
        status='active'
    ).first()

@miniprogram_bp.route('/device/bind', methods=['POST'])
@token_required
def bind_device(current_user):
    """绑定设备；设备不存在时自动创建，方便 Web 管理台演示添加设备。"""
    try:
        payload = normalize_device_payload(request.get_json())
        device_id = payload['device_id']

        if not device_id:
            return jsonify({'success': False, 'message': '缺少设备ID'}), 400
        if not DEVICE_ID_PATTERN.match(device_id):
            return jsonify({'success': False, 'message': '设备ID只能包含字母、数字、下划线或横线，长度3-20位'}), 400

        now = datetime.now()
        device = Device.query.filter_by(device_id=device_id).first()
        if not device:
            device = Device(
                device_id=device_id,
                device_type=payload['device_type'],
                firmware_version=payload['firmware_version'],
                install_date=now.date(),
                location=payload['location'],
                status='online',
                battery_level=stable_int(f"{device_id}:battery", 82, 99),
                signal_strength=stable_int(f"{device_id}:signal", -62, -38),
                last_heartbeat=now,
                created_at=now,
                updated_at=now
            )
            db.session.add(device)
            seed_device_data(device)
        else:
            device.device_type = payload['device_type'] or device.device_type
            device.firmware_version = payload['firmware_version'] or device.firmware_version
            device.location = payload['location'] or device.location
            device.status = 'online'
            device.last_heartbeat = now
            device.updated_at = now

        from models import DeviceBinding
        existing_binding = DeviceBinding.query.filter_by(
            user_id=current_user.id,
            device_id=device_id
        ).first()

        if existing_binding:
            if existing_binding.status == 'active':
                return jsonify({'success': False, 'message': '设备已绑定'}), 409
            existing_binding.status = 'active'
            existing_binding.unbind_time = None
            existing_binding.bind_time = now
            existing_binding.is_primary = payload['is_primary']
        else:
            new_binding = DeviceBinding(
                user_id=current_user.id,
                device_id=device_id,
                bind_time=now,
                is_primary=payload['is_primary'],
                status='active'
            )
            db.session.add(new_binding)

        db.session.commit()

        logger.info(f"设备绑定成功: 用户{current_user.username}, 设备{device_id}")

        return jsonify({
            'success': True,
            'message': '设备添加成功',
            'device': device.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"设备绑定失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@miniprogram_bp.route('/device/create', methods=['POST'])
@token_required
def create_device(current_user):
    """Web 管理台添加设备，复用绑定逻辑。"""
    return bind_device.__wrapped__(current_user)


@miniprogram_bp.route('/device/list', methods=['GET'])
@token_required
def get_device_list(current_user):
    """获取用户绑定的设备列表"""
    try:
        from models import DeviceBinding
        
        bindings = DeviceBinding.query.filter_by(
            user_id=current_user.id,
            status='active'
        ).all()
        
        devices = []
        for binding in bindings:
            device = Device.query.filter_by(device_id=binding.device_id).first()
            if device:
                device_dict = device.to_dict()
                device_dict['is_primary'] = binding.is_primary
                device_dict['bind_time'] = binding.bind_time.isoformat() if binding.bind_time else None
                devices.append(device_dict)
        
        return jsonify({
            'success': True,
            'devices': devices,
            'total': len(devices)
        }), 200
        
    except Exception as e:
        logger.error(f"获取设备列表失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@miniprogram_bp.route('/device/status/<device_id>', methods=['GET'])
@token_required
def get_device_status(current_user, device_id):
    """查询设备状态"""
    try:
        if not user_has_active_device(current_user, device_id):
            return jsonify({'success': False, 'message': '设备未绑定'}), 403

        device = Device.query.filter_by(device_id=device_id).first()

        if not device:
            return jsonify({'success': False, 'message': '设备不存在'}), 404

        return jsonify({
            'success': True,
            'device': device.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"查询设备状态失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@miniprogram_bp.route('/device/<device_id>', methods=['DELETE'])
@token_required
def delete_device_binding(current_user, device_id):
    """从当前账号解绑设备；保留设备和历史数据。"""
    try:
        from models import DeviceBinding
        binding = DeviceBinding.query.filter_by(
            user_id=current_user.id,
            device_id=device_id,
            status='active'
        ).first()

        if not binding:
            return jsonify({'success': False, 'message': '设备未绑定或已删除'}), 404

        now = datetime.now()
        binding.status = 'unbound'
        binding.unbind_time = now

        active_count = DeviceBinding.query.filter_by(
            device_id=device_id,
            status='active'
        ).count()
        if active_count == 0:
            device = Device.query.filter_by(device_id=device_id).first()
            if device:
                device.status = 'offline'
                device.updated_at = now

        db.session.commit()

        logger.info(f"设备解绑成功: 用户{current_user.username}, 设备{device_id}")

        return jsonify({
            'success': True,
            'message': '设备已从我的设备中删除'
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"删除设备失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


# =====================================================
# 数据查询接口
# =====================================================

@miniprogram_bp.route('/data/skin', methods=['GET'])
@token_required
def get_skin_data(current_user):
    """查询皮肤数据"""
    try:
        # 获取查询参数
        device_id = request.args.get('device_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 构建查询
        query = SkinSensorData.query
        query = query.filter(SkinSensorData.sensor_time <= datetime.now())

        if device_id:
            query = query.filter_by(device_id=device_id)
        
        if start_date:
            query = query.filter(SkinSensorData.sensor_time >= datetime.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(SkinSensorData.sensor_time <= datetime.fromisoformat(end_date))
        
        # 按时间倒序排列
        query = query.order_by(SkinSensorData.sensor_time.desc())
        
        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        data_list = [item.to_dict() for item in pagination.items]
        
        return jsonify({
            'success': True,
            'data': data_list,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        logger.error(f"查询皮肤数据失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@miniprogram_bp.route('/data/environment', methods=['GET'])
@token_required
def get_environment_data(current_user):
    """查询环境数据"""
    try:
        # 获取查询参数
        device_id = request.args.get('device_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 构建查询
        query = EnvironmentSensorData.query
        query = query.filter(EnvironmentSensorData.sensor_time <= datetime.now())

        if device_id:
            query = query.filter_by(device_id=device_id)
        
        if start_date:
            query = query.filter(EnvironmentSensorData.sensor_time >= datetime.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(EnvironmentSensorData.sensor_time <= datetime.fromisoformat(end_date))
        
        # 按时间倒序排列
        query = query.order_by(EnvironmentSensorData.sensor_time.desc())
        
        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        data_list = [item.to_dict() for item in pagination.items]
        
        return jsonify({
            'success': True,
            'data': data_list,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        logger.error(f"查询环境数据失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@miniprogram_bp.route('/data/statistics', methods=['GET'])
@token_required
def get_statistics(current_user):
    """??????????????????? Web ?????????????"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        days = request.args.get('days', type=int)

        def parse_dt(value, end_of_day=False):
            if not value:
                return None
            clean = value.strip().replace('Z', '').replace('T', ' ')
            if '+' in clean:
                clean = clean.split('+', 1)[0]
            if '.' in clean:
                clean = clean.split('.', 1)[0]
            for fmt, candidate in [('%Y-%m-%d %H:%M:%S', clean[:19]), ('%Y-%m-%d', clean[:10])]:
                try:
                    parsed = datetime.strptime(candidate, fmt)
                    if fmt == '%Y-%m-%d' and end_of_day:
                        parsed = parsed.replace(hour=23, minute=59, second=59, microsecond=999999)
                    return parsed
                except ValueError:
                    pass
            raise ValueError('???????')

        now = datetime.now()
        start_dt = parse_dt(start_date)
        end_dt = parse_dt(end_date, end_of_day=True)
        if days and not start_dt:
            safe_days = max(1, min(days, 365))
            start_dt = (now - timedelta(days=safe_days - 1)).replace(hour=0, minute=0, second=0, microsecond=0)

        stats = {}

        def key_of(value):
            return value.isoformat() if hasattr(value, 'isoformat') else str(value)

        def rv(value):
            return round(float(value), 2) if value is not None else None

        skin_date = func.date(SkinSensorData.sensor_time)
        skin_query = db.session.query(
            skin_date.label('stat_date'),
            func.count(SkinSensorData.id).label('records'),
            func.count(func.distinct(SkinSensorData.device_id)).label('devices'),
            func.avg(SkinSensorData.moisture).label('avg_moisture'),
            func.avg(SkinSensorData.oiliness).label('avg_oiliness'),
            func.avg(SkinSensorData.temperature).label('avg_skin_temperature')
        )
        if start_dt:
            skin_query = skin_query.filter(SkinSensorData.sensor_time >= start_dt)
        if end_dt:
            skin_query = skin_query.filter(SkinSensorData.sensor_time <= end_dt)

        for row in skin_query.group_by(skin_date).all():
            key = key_of(row.stat_date)
            stats[key] = {
                'stat_date': key,
                'total_records': int(row.records or 0),
                'active_devices': int(row.devices or 0),
                'avg_moisture': rv(row.avg_moisture),
                'avg_oiliness': rv(row.avg_oiliness),
                'avg_temperature': rv(row.avg_skin_temperature),
                'avg_skin_temperature': rv(row.avg_skin_temperature),
                'avg_environment_temperature': None,
                'avg_humidity': None,
                'avg_pm25': None,
                'avg_co2': None,
                'calculated_at': now.isoformat(),
                'created_at': now.isoformat()
            }

        env_date = func.date(EnvironmentSensorData.sensor_time)
        env_query = db.session.query(
            env_date.label('stat_date'),
            func.count(EnvironmentSensorData.id).label('records'),
            func.count(func.distinct(EnvironmentSensorData.device_id)).label('devices'),
            func.avg(EnvironmentSensorData.temperature).label('avg_environment_temperature'),
            func.avg(EnvironmentSensorData.humidity).label('avg_humidity'),
            func.avg(EnvironmentSensorData.pm25).label('avg_pm25'),
            func.avg(EnvironmentSensorData.co2).label('avg_co2')
        )
        if start_dt:
            env_query = env_query.filter(EnvironmentSensorData.sensor_time >= start_dt)
        if end_dt:
            env_query = env_query.filter(EnvironmentSensorData.sensor_time <= end_dt)

        for row in env_query.group_by(env_date).all():
            key = key_of(row.stat_date)
            item = stats.setdefault(key, {
                'stat_date': key,
                'total_records': 0,
                'active_devices': 0,
                'avg_moisture': None,
                'avg_oiliness': None,
                'avg_temperature': None,
                'avg_skin_temperature': None,
                'avg_environment_temperature': None,
                'avg_humidity': None,
                'avg_pm25': None,
                'avg_co2': None,
                'calculated_at': now.isoformat(),
                'created_at': now.isoformat()
            })
            item['total_records'] += int(row.records or 0)
            item['active_devices'] += int(row.devices or 0)
            item['avg_environment_temperature'] = rv(row.avg_environment_temperature)
            if item.get('avg_temperature') is None:
                item['avg_temperature'] = item['avg_environment_temperature']
            item['avg_humidity'] = rv(row.avg_humidity)
            item['avg_pm25'] = rv(row.avg_pm25)
            item['avg_co2'] = rv(row.avg_co2)

        statistics = sorted(stats.values(), key=lambda item: item['stat_date'], reverse=True)

        return jsonify({
            'success': True,
            'statistics': statistics,
            'total': len(statistics)
        }), 200

    except Exception as e:
        logger.error("????????: %s", str(e), exc_info=True)
        try:
            db.session.rollback()
        except Exception:
            pass
        return jsonify({'success': False, 'message': str(e)}), 500



# =====================================================

@miniprogram_bp.route('/report/list', methods=['GET'])
@token_required
def get_report_list(current_user):
    """获取报告列表"""
    try:
        from models import HealthReport
        
        report_type = request.args.get('type')  # daily/weekly/monthly/yearly
        
        query = HealthReport.query.filter_by(user_id=current_user.id)
        
        if report_type:
            query = query.filter_by(report_type=report_type)
        
        # 按日期倒序排列
        query = query.order_by(HealthReport.report_date.desc())
        
        reports = [item.to_dict() for item in query.all()]
        
        return jsonify({
            'success': True,
            'reports': reports,
            'total': len(reports)
        }), 200
        
    except Exception as e:
        logger.error(f"获取报告列表失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@miniprogram_bp.route('/report/detail/<int:report_id>', methods=['GET'])
@token_required
def get_report_detail(current_user, report_id):
    """获取报告详情"""
    try:
        from models import HealthReport
        
        report = HealthReport.query.get(report_id)
        
        if not report:
            return jsonify({'success': False, 'message': '报告不存在'}), 404
        
        if report.user_id != current_user.id:
            return jsonify({'success': False, 'message': '无权访问此报告'}), 403
        
        return jsonify({
            'success': True,
            'report': report.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"获取报告详情失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


# =====================================================
# 消息通知接口
# =====================================================

@miniprogram_bp.route('/notification/list', methods=['GET'])
@token_required
def get_notification_list(current_user):
    """获取通知列表"""
    try:
        from models import Notification
        
        notification_type = request.args.get('type')
        is_read = request.args.get('is_read', type=bool)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = Notification.query.filter_by(user_id=current_user.id)
        
        if notification_type:
            query = query.filter_by(type=notification_type)
        
        if is_read is not None:
            query = query.filter_by(is_read=is_read)
        
        # 按创建时间倒序排列
        query = query.order_by(Notification.created_at.desc())
        
        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        notifications = [item.to_dict() for item in pagination.items]
        
        return jsonify({
            'success': True,
            'notifications': notifications,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        logger.error(f"获取通知列表失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@miniprogram_bp.route('/notification/read/<int:notification_id>', methods=['PUT'])
@token_required
def mark_notification_read(current_user, notification_id):
    """标记通知为已读"""
    try:
        from models import Notification
        
        notification = Notification.query.get(notification_id)
        
        if not notification:
            return jsonify({'success': False, 'message': '通知不存在'}), 404
        
        if notification.user_id != current_user.id:
            return jsonify({'success': False, 'message': '无权操作此通知'}), 403
        
        notification.is_read = True
        notification.read_at = datetime.now()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '已标记为已读'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"标记通知已读失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


# =====================================================
# 积分等级系统接口
# =====================================================

@miniprogram_bp.route('/points/info', methods=['GET'])
@token_required
def get_points_info(current_user):
    """获取用户积分信息"""
    try:
        from models import UserPoints
        
        points = UserPoints.query.filter_by(user_id=current_user.id).first()
        
        if not points:
            # 创建默认积分记录
            points = UserPoints(
                user_id=current_user.id,
                total_points=0,
                available_points=0,
                used_points=0,
                expired_points=0,
                level='bronze'
            )
            db.session.add(points)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'points': points.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"获取积分信息失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@miniprogram_bp.route('/points/history', methods=['GET'])
@token_required
def get_points_history(current_user):
    """获取积分历史记录"""
    try:
        from models import PointsHistory
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = PointsHistory.query.filter_by(user_id=current_user.id)
        query = query.order_by(PointsHistory.created_at.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        history = [item.to_dict() for item in pagination.items]
        
        return jsonify({
            'success': True,
            'history': history,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        logger.error(f"获取积分历史失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


# =====================================================
# 社区互动接口
# =====================================================

@miniprogram_bp.route('/community/posts', methods=['GET'])
@token_required
def get_community_posts(current_user):
    """获取社区帖子列表"""
    try:
        from models import CommunityPost
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category = request.args.get('category')  # experience/question/tips
        
        query = CommunityPost.query
        
        if category:
            query = query.filter_by(category=category)
        
        query = query.order_by(CommunityPost.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        posts = []
        for post in pagination.items:
            post_dict = post.to_dict()
            # 添加作者信息
            author = User.query.get(post.user_id)
            if author:
                post_dict['author'] = {
                    'username': author.username,
                    'nickname': author.nickname,
                    'avatar_url': author.avatar_url
                }
            posts.append(post_dict)
        
        return jsonify({
            'success': True,
            'posts': posts,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        logger.error(f"获取帖子列表失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@miniprogram_bp.route('/community/posts', methods=['POST'])
@token_required
def create_post(current_user):
    """发布帖子"""
    try:
        from models import CommunityPost
        
        data = request.get_json()
        
        required_fields = ['title', 'content', 'category']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'缺少必填字段: {field}'}), 400
        
        post = CommunityPost(
            user_id=current_user.id,
            title=data['title'],
            content=data['content'],
            category=data['category'],
            tags=data.get('tags', [])
        )
        
        db.session.add(post)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '发布成功',
            'post_id': post.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"发布帖子失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@miniprogram_bp.route('/community/posts/<int:post_id>/comments', methods=['GET'])
@token_required
def get_post_comments(current_user, post_id):
    """获取帖子评论"""
    try:
        from models import PostComment
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = PostComment.query.filter_by(post_id=post_id)
        query = query.order_by(PostComment.created_at.asc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        comments = [item.to_dict() for item in pagination.items]
        
        return jsonify({
            'success': True,
            'comments': comments,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        logger.error(f"获取评论失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@miniprogram_bp.route('/community/posts/<int:post_id>/comments', methods=['POST'])
@token_required
def create_comment(current_user, post_id):
    """发表评论"""
    try:
        from models import PostComment
        
        data = request.get_json()
        
        if 'content' not in data:
            return jsonify({'success': False, 'message': '评论内容不能为空'}), 400
        
        comment = PostComment(
            post_id=post_id,
            user_id=current_user.id,
            content=data['content'],
            parent_comment_id=data.get('parent_comment_id')
        )
        
        db.session.add(comment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '评论成功',
            'comment_id': comment.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"发表评论失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


# =====================================================
# 护肤记录接口
# =====================================================

@miniprogram_bp.route('/skincare/records', methods=['GET'])
@token_required
def get_skincare_records(current_user):
    """获取护肤记录"""
    try:
        from models import UserSkincareRecord
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = UserSkincareRecord.query.filter_by(user_id=current_user.id)
        
        if start_date:
            query = query.filter(UserSkincareRecord.usage_time >= datetime.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(UserSkincareRecord.usage_time <= datetime.fromisoformat(end_date))
        
        query = query.order_by(UserSkincareRecord.usage_time.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        records = [item.to_dict() for item in pagination.items]
        
        return jsonify({
            'success': True,
            'records': records,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        logger.error(f"获取护肤记录失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@miniprogram_bp.route('/skincare/records', methods=['POST'])
@token_required
def create_skincare_record(current_user):
    """添加护肤记录"""
    try:
        from models import UserSkincareRecord
        
        data = request.get_json()
        
        required_fields = ['product_name', 'usage_time']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'缺少必填字段: {field}'}), 400
        
        record = UserSkincareRecord(
            user_id=current_user.id,
            product_id=data.get('product_id'),
            product_name=data['product_name'],
            usage_time=datetime.fromisoformat(data['usage_time']),
            usage_amount=data.get('usage_amount'),
            skin_feel=data.get('skin_feel'),
            effect_rating=data.get('effect_rating'),
            notes=data.get('notes')
        )
        
        db.session.add(record)
        
        # 增加积分
        from models import UserPoints
        points = UserPoints.query.filter_by(user_id=current_user.id).first()
        if points:
            points.total_points += 10
            points.available_points += 10
            db.session.add(points)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '记录成功，获得10积分',
            'record_id': record.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"添加护肤记录失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


# =====================================================
# 产品数据库接口
# =====================================================

@miniprogram_bp.route('/products', methods=['GET'])
@token_required
def get_products(current_user):
    """获取产品列表"""
    try:
        from models import SkincareProduct
        
        category = request.args.get('category')
        brand = request.args.get('brand')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = SkincareProduct.query
        
        if category:
            query = query.filter_by(category=category)
        
        if brand:
            query = query.filter_by(brand=brand)
        
        query = query.order_by(SkincareProduct.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        products = [item.to_dict() for item in pagination.items]
        
        return jsonify({
            'success': True,
            'products': products,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        logger.error(f"获取产品列表失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@miniprogram_bp.route('/products/recommend', methods=['GET'])
@token_required
def get_recommended_products(current_user):
    """个性化产品推荐"""
    try:
        from models import SkincareProduct, UserProfile
        
        # 获取用户肤质档案
        profile = UserProfile.query.filter_by(user_id=current_user.id).first()
        
        # 根据肤质推荐产品
        query = SkincareProduct.query
        
        if profile and profile.skin_type:
            # 简单推荐逻辑：根据肤质类型筛选
            query = query.filter(
                SkincareProduct.suitable_skin_types.contains(profile.skin_type)
            )
        
        query = query.order_by(SkincareProduct.rating.desc()).limit(10)
        products = [item.to_dict() for item in query.all()]
        
        return jsonify({
            'success': True,
            'recommended_products': products,
            'based_on': profile.skin_type if profile else 'general'
        }), 200
        
    except Exception as e:
        logger.error(f"获取推荐产品失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


# =====================================================
# Web 运营监控接口
# =====================================================

@miniprogram_bp.route('/monitor/overview', methods=['GET'])
@token_required
def get_monitor_overview(current_user):
    """全站运营监控聚合数据，供 Web 管理站使用。"""
    try:
        from models import (
            DeviceBinding, HealthReport, Notification, UserPoints,
            PointsHistory, CommunityPost, PostComment, UserSkincareRecord,
            SkincareProduct
        )

        def safe_value(fn, default=0):
            try:
                return fn()
            except Exception as err:
                db.session.rollback()
                logger.warning(f"监控聚合跳过不可用数据项: {err}")
                return default

        days = request.args.get('days', 7, type=int)
        safe_days = max(1, min(days or 7, 90))
        now = datetime.now()
        start_dt = now - timedelta(days=safe_days - 1)
        start_date = start_dt.date()

        total_users = db.session.query(func.count(User.id)).scalar() or 0
        active_users = db.session.query(func.count(User.id)).filter(User.status == 'active').scalar() or 0
        new_users = db.session.query(func.count(User.id)).filter(User.created_at >= start_dt).scalar() or 0
        total_devices = db.session.query(func.count(Device.id)).scalar() or 0
        online_devices = db.session.query(func.count(Device.id)).filter(Device.status == 'online').scalar() or 0
        skin_devices = db.session.query(func.count(Device.id)).filter(Device.device_type != 'environment').scalar() or 0
        env_devices = db.session.query(func.count(Device.id)).filter(Device.device_type == 'environment').scalar() or 0
        active_bindings = db.session.query(func.count(DeviceBinding.id)).filter(DeviceBinding.status == 'active').scalar() or 0
        unbound_devices = db.session.query(func.count(DeviceBinding.id)).filter(DeviceBinding.status == 'unbound').scalar() or 0

        skin_records = db.session.query(func.count(SkinSensorData.id)).filter(SkinSensorData.sensor_time >= start_dt).scalar() or 0
        env_records = db.session.query(func.count(EnvironmentSensorData.id)).filter(EnvironmentSensorData.sensor_time >= start_dt).scalar() or 0
        total_records = skin_records + env_records

        latest_skin = SkinSensorData.query.order_by(SkinSensorData.sensor_time.desc()).first()
        latest_env = EnvironmentSensorData.query.order_by(EnvironmentSensorData.sensor_time.desc()).first()

        skin_avg = db.session.query(
            func.avg(SkinSensorData.moisture),
            func.avg(SkinSensorData.oiliness),
            func.avg(SkinSensorData.temperature),
            func.avg(SkinSensorData.quality_score)
        ).filter(SkinSensorData.sensor_time >= start_dt).first()
        env_avg = db.session.query(
            func.avg(EnvironmentSensorData.temperature),
            func.avg(EnvironmentSensorData.humidity),
            func.avg(EnvironmentSensorData.pm25),
            func.avg(EnvironmentSensorData.co2),
            func.avg(EnvironmentSensorData.quality_score)
        ).filter(EnvironmentSensorData.sensor_time >= start_dt).first()

        report_total = db.session.query(func.count(HealthReport.id)).scalar() or 0
        reports_generated = db.session.query(func.count(HealthReport.id)).filter(HealthReport.is_generated == True).scalar() or 0
        reports_recent = db.session.query(func.count(HealthReport.id)).filter(HealthReport.created_at >= start_dt).scalar() or 0
        avg_report_score = db.session.query(func.avg(HealthReport.score)).filter(HealthReport.score.isnot(None)).scalar()

        unread_notifications = db.session.query(func.count(Notification.id)).filter(Notification.is_read == False).scalar() or 0
        notification_total = db.session.query(func.count(Notification.id)).scalar() or 0
        community_posts = safe_value(lambda: db.session.query(func.count(CommunityPost.id)).scalar() or 0)
        community_comments = safe_value(lambda: db.session.query(func.count(PostComment.id)).scalar() or 0)
        skincare_records = safe_value(lambda: db.session.query(func.count(UserSkincareRecord.id)).scalar() or 0)
        products = safe_value(lambda: db.session.query(func.count(SkincareProduct.id)).filter(SkincareProduct.status == 'active').scalar() or 0)
        points_total = safe_value(lambda: db.session.query(func.coalesce(func.sum(UserPoints.total_points), 0)).scalar() or 0)
        points_events = safe_value(lambda: db.session.query(func.count(PointsHistory.id)).filter(PointsHistory.created_at >= start_dt).scalar() or 0)

        daily_rows = []
        for offset in range(safe_days):
            day = start_date + timedelta(days=offset)
            day_start = datetime.combine(day, datetime.min.time())
            day_end = day_start + timedelta(days=1)
            skin_count = db.session.query(func.count(SkinSensorData.id)).filter(
                SkinSensorData.sensor_time >= day_start,
                SkinSensorData.sensor_time < day_end
            ).scalar() or 0
            env_count = db.session.query(func.count(EnvironmentSensorData.id)).filter(
                EnvironmentSensorData.sensor_time >= day_start,
                EnvironmentSensorData.sensor_time < day_end
            ).scalar() or 0
            user_count = db.session.query(func.count(User.id)).filter(
                User.created_at >= day_start,
                User.created_at < day_end
            ).scalar() or 0
            report_count = db.session.query(func.count(HealthReport.id)).filter(
                HealthReport.created_at >= day_start,
                HealthReport.created_at < day_end
            ).scalar() or 0
            daily_rows.append({
                'date': day.isoformat(),
                'skin_records': skin_count,
                'environment_records': env_count,
                'total_records': skin_count + env_count,
                'new_users': user_count,
                'reports': report_count
            })

        device_rows = Device.query.order_by(Device.last_heartbeat.desc()).limit(50).all()
        devices = []
        device_user_relations = []
        for device in device_rows:
            item = device.to_dict()
            binding_count = db.session.query(func.count(DeviceBinding.id)).filter(
                DeviceBinding.device_id == device.device_id,
                DeviceBinding.status == 'active'
            ).scalar() or 0
            skin_count = db.session.query(func.count(SkinSensorData.id)).filter(
                SkinSensorData.device_id == device.device_id
            ).scalar() or 0
            env_count = db.session.query(func.count(EnvironmentSensorData.id)).filter(
                EnvironmentSensorData.device_id == device.device_id
            ).scalar() or 0
            binding_rows = DeviceBinding.query.filter_by(
                device_id=device.device_id,
                status='active'
            ).order_by(DeviceBinding.bind_time.desc()).limit(10).all()
            bound_users = []
            for binding in binding_rows:
                user = User.query.get(binding.user_id)
                bound_users.append({
                    'binding_id': binding.id,
                    'user_id': binding.user_id,
                    'username': user.username if user else None,
                    'nickname': user.nickname if user else None,
                    'status': user.status if user else None,
                    'is_primary': binding.is_primary,
                    'bind_time': binding.bind_time.isoformat() if binding.bind_time else None
                })
            item['active_bindings'] = binding_count
            item['record_count'] = skin_count + env_count
            item['bound_users'] = bound_users
            devices.append(item)
            device_user_relations.append({
                'device_id': device.device_id,
                'device_type': device.device_type,
                'device_status': device.status,
                'location': device.location,
                'active_bindings': binding_count,
                'record_count': skin_count + env_count,
                'users': bound_users
            })

        latest_events = []
        for row in SkinSensorData.query.order_by(SkinSensorData.sensor_time.desc()).limit(5).all():
            latest_events.append({
                'type': 'skin',
                'title': '皮肤检测数据',
                'device_id': row.device_id,
                'value': f"水分 {row.moisture}% / 油脂 {row.oiliness}%",
                'time': row.sensor_time.isoformat() if row.sensor_time else None
            })
        for row in EnvironmentSensorData.query.order_by(EnvironmentSensorData.sensor_time.desc()).limit(5).all():
            latest_events.append({
                'type': 'environment',
                'title': '环境传感数据',
                'device_id': row.device_id,
                'value': f"温度 {row.temperature}℃ / 湿度 {row.humidity}%",
                'time': row.sensor_time.isoformat() if row.sensor_time else None
            })
        latest_events = sorted(latest_events, key=lambda item: item.get('time') or '', reverse=True)[:8]

        user_rows = User.query.order_by(User.created_at.desc()).limit(8).all()
        users = []
        for user in user_rows:
            users.append({
                'id': user.id,
                'username': user.username,
                'nickname': user.nickname,
                'status': user.status,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'device_count': db.session.query(func.count(DeviceBinding.id)).filter(
                    DeviceBinding.user_id == user.id,
                    DeviceBinding.status == 'active'
                ).scalar() or 0,
                'report_count': db.session.query(func.count(HealthReport.id)).filter(
                    HealthReport.user_id == user.id
                ).scalar() or 0,
                'skincare_count': safe_value(lambda user_id=user.id: db.session.query(func.count(UserSkincareRecord.id)).filter(
                    UserSkincareRecord.user_id == user.id
                ).scalar() or 0)
            })

        report_rows = safe_value(lambda: HealthReport.query.order_by(HealthReport.created_at.desc()).limit(8).all(), [])
        reports = [row.to_dict() for row in report_rows]

        notification_rows = safe_value(lambda: Notification.query.order_by(Notification.created_at.desc()).limit(8).all(), [])
        notifications = [row.to_dict() for row in notification_rows]

        return jsonify({
            'success': True,
            'generated_at': now.isoformat(),
            'range_days': safe_days,
            'summary': {
                'users': total_users,
                'active_users': active_users,
                'new_users': new_users,
                'devices': total_devices,
                'online_devices': online_devices,
                'offline_devices': max(total_devices - online_devices, 0),
                'skin_devices': skin_devices,
                'environment_devices': env_devices,
                'active_bindings': active_bindings,
                'unbound_devices': unbound_devices,
                'records': total_records,
                'skin_records': skin_records,
                'environment_records': env_records,
                'reports': report_total,
                'reports_generated': reports_generated,
                'reports_recent': reports_recent,
                'avg_report_score': round(float(avg_report_score or 0), 1),
                'unread_notifications': unread_notifications,
                'notifications': notification_total,
                'community_posts': community_posts,
                'community_comments': community_comments,
                'skincare_records': skincare_records,
                'products': products,
                'points_total': int(points_total),
                'points_events': points_events
            },
            'averages': {
                'moisture': round(float(skin_avg[0] or 0), 1),
                'oiliness': round(float(skin_avg[1] or 0), 1),
                'skin_temperature': round(float(skin_avg[2] or 0), 1),
                'skin_quality': round(float(skin_avg[3] or 0), 2),
                'environment_temperature': round(float(env_avg[0] or 0), 1),
                'humidity': round(float(env_avg[1] or 0), 1),
                'pm25': round(float(env_avg[2] or 0), 1),
                'co2': round(float(env_avg[3] or 0), 1),
                'environment_quality': round(float(env_avg[4] or 0), 2)
            },
            'latest': {
                'skin': latest_skin.to_dict() if latest_skin else None,
                'environment': latest_env.to_dict() if latest_env else None
            },
            'daily': daily_rows,
            'devices': devices,
            'device_user_relations': device_user_relations,
            'events': latest_events,
            'users': users,
            'reports': reports,
            'notifications': notifications
        }), 200

    except Exception as e:
        logger.error(f"获取运营监控数据失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@miniprogram_bp.route('/monitor/device/<device_id>', methods=['GET'])
@token_required
def get_monitor_device(current_user, device_id):
    """全站设备详情，不按当前用户绑定过滤。"""
    try:
        from models import DeviceBinding

        device = Device.query.filter_by(device_id=device_id).first()
        if not device:
            return jsonify({'success': False, 'message': '设备不存在'}), 404

        is_environment = (device.device_type == 'environment') or device.device_id.upper().startswith('ENV')
        if is_environment:
            rows = EnvironmentSensorData.query.filter_by(device_id=device_id).order_by(
                EnvironmentSensorData.sensor_time.desc()
            ).limit(12).all()
        else:
            rows = SkinSensorData.query.filter_by(device_id=device_id).order_by(
                SkinSensorData.sensor_time.desc()
            ).limit(12).all()

        active_bindings = DeviceBinding.query.filter_by(device_id=device_id, status='active').count()
        total_bindings = DeviceBinding.query.filter_by(device_id=device_id).count()
        binding_rows = DeviceBinding.query.filter_by(device_id=device_id).order_by(
            DeviceBinding.bind_time.desc()
        ).limit(20).all()
        bound_users = []
        for binding in binding_rows:
            user = User.query.get(binding.user_id)
            bound_users.append({
                'binding_id': binding.id,
                'user_id': binding.user_id,
                'username': user.username if user else None,
                'nickname': user.nickname if user else None,
                'user_status': user.status if user else None,
                'binding_status': binding.status,
                'is_primary': binding.is_primary,
                'bind_time': binding.bind_time.isoformat() if binding.bind_time else None,
                'unbind_time': binding.unbind_time.isoformat() if binding.unbind_time else None
            })

        return jsonify({
            'success': True,
            'device': device.to_dict(),
            'active_bindings': active_bindings,
            'total_bindings': total_bindings,
            'bound_users': bound_users,
            'data_type': 'environment' if is_environment else 'skin',
            'data': [row.to_dict() for row in rows]
        }), 200

    except Exception as e:
        logger.error(f"获取全站设备详情失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@miniprogram_bp.route('/monitor/device/<device_id>', methods=['DELETE'])
@token_required
def delete_monitor_device(current_user, device_id):
    """全站设备下线并解除所有活跃绑定，保留历史检测数据。"""
    try:
        from models import DeviceBinding

        device = Device.query.filter_by(device_id=device_id).first()
        if not device:
            return jsonify({'success': False, 'message': '设备不存在'}), 404

        now = datetime.now()
        active_bindings = DeviceBinding.query.filter_by(device_id=device_id, status='active').all()
        for binding in active_bindings:
            binding.status = 'unbound'
            binding.unbind_time = now

        device.status = 'offline'
        device.updated_at = now
        db.session.commit()

        logger.info(f"监控站设备下线: 操作用户{current_user.username}, 设备{device_id}")

        return jsonify({
            'success': True,
            'message': '设备已下线，历史检测数据已保留',
            'affected_bindings': len(active_bindings)
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"全站删除设备失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


# =====================================================
# 注册蓝图
# =====================================================
@miniprogram_bp.route('/monitor/db-locations', methods=['GET'])
@token_required
def get_monitor_db_locations(current_user):
    """从数据库 devices 表读取真实设备位置分布（独立接口，供前端地域地图使用）"""
    try:
        all_devices = Device.query.filter(Device.location.isnot(None)).filter(Device.location != '').all()
        location_buckets = {}
        skipped_garbage = 0
        for dev in all_devices:
            loc = (dev.location or '').strip()
            if not loc or loc in ('??', '?????'):
                skipped_garbage += 1
                continue
            parts = loc.split('-')
            prov = parts[0].strip() if parts else loc
            if not prov:
                continue
            bucket = location_buckets.setdefault(prov, {
                'devices': 0, 'skin': 0, 'env': 0,
                'device_ids': [], 'samples': set()
            })
            bucket['devices'] += 1
            bucket['device_ids'].append(dev.device_id)
            if dev.device_type == 'environment':
                bucket['env'] += 1
            else:
                bucket['skin'] += 1
            bucket['samples'].add(loc)
        provinces_list = []
        for prov_name, data in location_buckets.items():
            provinces_list.append({
                'province': prov_name,
                'db_device_count': data['devices'],
                'db_skin_devices': data['skin'],
                'db_env_devices': data['env'],
                'device_ids': data['device_ids'][:30],
                'location_samples': list(data['samples'])[:5],
            })
        provinces_list.sort(key=lambda x: x['db_device_count'], reverse=True)
        return jsonify({
            'success': True,
            'source': 'database',
            'generated_at': datetime.now().isoformat(),
            'total_provinces': len(provinces_list),
            'total_db_devices': len(all_devices),
            'skipped_garbage': skipped_garbage,
            'provinces': provinces_list
        }), 200
    except Exception as e:
        logger.error(f"读取数据库设备位置失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


# =====================================================
# Role dashboard APIs for the web operation console
# =====================================================

ROLE_PROVINCES = [
    {'name': '北京', 'city': '北京市', 'x': 640, 'y': 245, 'base_humidity': 42, 'region': '华北'},
    {'name': '天津', 'city': '天津市', 'x': 665, 'y': 275, 'base_humidity': 47, 'region': '华北'},
    {'name': '河北', 'city': '石家庄市', 'x': 598, 'y': 310, 'base_humidity': 45, 'region': '华北'},
    {'name': '山西', 'city': '太原市', 'x': 555, 'y': 325, 'base_humidity': 42, 'region': '华北'},
    {'name': '内蒙古', 'city': '呼和浩特市', 'x': 515, 'y': 235, 'base_humidity': 35, 'region': '华北'},
    {'name': '辽宁', 'city': '沈阳市', 'x': 675, 'y': 215, 'base_humidity': 45, 'region': '东北'},
    {'name': '吉林', 'city': '长春市', 'x': 700, 'y': 165, 'base_humidity': 42, 'region': '东北'},
    {'name': '黑龙江', 'city': '哈尔滨市', 'x': 705, 'y': 115, 'base_humidity': 40, 'region': '东北'},
    {'name': '上海', 'city': '上海市', 'x': 725, 'y': 438, 'base_humidity': 67, 'region': '华东'},
    {'name': '江苏', 'city': '南京市', 'x': 688, 'y': 414, 'base_humidity': 62, 'region': '华东'},
    {'name': '浙江', 'city': '杭州市', 'x': 700, 'y': 486, 'base_humidity': 70, 'region': '华东'},
    {'name': '安徽', 'city': '合肥市', 'x': 650, 'y': 435, 'base_humidity': 61, 'region': '华东'},
    {'name': '福建', 'city': '福州市', 'x': 690, 'y': 548, 'base_humidity': 72, 'region': '华东'},
    {'name': '江西', 'city': '南昌市', 'x': 632, 'y': 522, 'base_humidity': 68, 'region': '华东'},
    {'name': '山东', 'city': '济南市', 'x': 650, 'y': 344, 'base_humidity': 50, 'region': '华东'},
    {'name': '河南', 'city': '郑州市', 'x': 585, 'y': 392, 'base_humidity': 48, 'region': '华中'},
    {'name': '湖北', 'city': '武汉市', 'x': 582, 'y': 468, 'base_humidity': 63, 'region': '华中'},
    {'name': '湖南', 'city': '长沙市', 'x': 570, 'y': 530, 'base_humidity': 66, 'region': '华中'},
    {'name': '广东', 'city': '广州市', 'x': 615, 'y': 628, 'base_humidity': 73, 'region': '华南'},
    {'name': '广西', 'city': '南宁市', 'x': 530, 'y': 625, 'base_humidity': 75, 'region': '华南'},
    {'name': '海南', 'city': '海口市', 'x': 585, 'y': 715, 'base_humidity': 78, 'region': '华南'},
    {'name': '重庆', 'city': '重庆市', 'x': 505, 'y': 505, 'base_humidity': 67, 'region': '西南'},
    {'name': '四川', 'city': '成都市', 'x': 445, 'y': 482, 'base_humidity': 58, 'region': '西南'},
    {'name': '贵州', 'city': '贵阳市', 'x': 505, 'y': 575, 'base_humidity': 70, 'region': '西南'},
    {'name': '云南', 'city': '昆明市', 'x': 425, 'y': 635, 'base_humidity': 69, 'region': '西南'},
    {'name': '西藏', 'city': '拉萨市', 'x': 320, 'y': 505, 'base_humidity': 36, 'region': '西南'},
    {'name': '陕西', 'city': '西安市', 'x': 505, 'y': 395, 'base_humidity': 44, 'region': '西北'},
    {'name': '甘肃', 'city': '兰州市', 'x': 420, 'y': 365, 'base_humidity': 38, 'region': '西北'},
    {'name': '青海', 'city': '西宁市', 'x': 365, 'y': 385, 'base_humidity': 35, 'region': '西北'},
    {'name': '宁夏', 'city': '银川市', 'x': 465, 'y': 330, 'base_humidity': 37, 'region': '西北'},
    {'name': '新疆', 'city': '乌鲁木齐市', 'x': 190, 'y': 245, 'base_humidity': 32, 'region': '西北'},
    {'name': '台湾', 'city': '台北市', 'x': 758, 'y': 585, 'base_humidity': 76, 'region': '华东'},
    {'name': '香港', 'city': '香港特别行政区', 'x': 653, 'y': 658, 'base_humidity': 77, 'region': '华南'},
    {'name': '澳门', 'city': '澳门特别行政区', 'x': 625, 'y': 670, 'base_humidity': 76, 'region': '华南'},
]

DEMO_SAMPLE_WINDOW_SECONDS = 24
ROLE_DEMO_DATASET_CACHE = {'ready_until': None, 'state': None}
LEADER_DECISION_STORE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'leader_decisions.json'
)

PERMISSION_DEFINITIONS = [
    {'key': 'leader.overview.read', 'label': '领导端-全国总览', 'group': 'leader', 'level': 'read'},
    {'key': 'leader.map.read', 'label': '领导端-地域地图', 'group': 'leader', 'level': 'read'},
    {'key': 'leader.abnormal.read', 'label': '领导端-异常省份', 'group': 'leader', 'level': 'read'},
    {'key': 'leader.age.read', 'label': '领导端-年龄画像', 'group': 'leader', 'level': 'read'},
    {'key': 'leader.trend.read', 'label': '领导端-全站趋势', 'group': 'leader', 'level': 'read'},
    {'key': 'leader.advice.read', 'label': '领导端-决策建议', 'group': 'leader', 'level': 'read'},
    {'key': 'leader.decision.edit', 'label': '领导端-新增决策', 'group': 'leader', 'level': 'edit'},
    {'key': 'support.search.read', 'label': '客服端-搜索工作台', 'group': 'support', 'level': 'read'},
    {'key': 'support.users.read', 'label': '客服端-用户详情', 'group': 'support', 'level': 'read'},
    {'key': 'support.devices.read', 'label': '客服端-设备监视', 'group': 'support', 'level': 'read'},
    {'key': 'support.stream.read', 'label': '客服端-实时数据流', 'group': 'support', 'level': 'read'},
    {'key': 'support.bind.read', 'label': '客服端-绑定管理查看', 'group': 'support', 'level': 'read'},
    {'key': 'support.bind.edit', 'label': '客服端-绑定/解绑设备', 'group': 'support', 'level': 'edit'},
    {'key': 'admin.accounts.read', 'label': '管理端-查看账号', 'group': 'admin', 'level': 'read'},
    {'key': 'admin.accounts.edit', 'label': '管理端-创建和配置账号', 'group': 'admin', 'level': 'edit'},
]
PERMISSION_KEYS = [item['key'] for item in PERMISSION_DEFINITIONS]
PERMISSION_INDEX = {key: str(index) for index, key in enumerate(PERMISSION_KEYS)}

LEADER_READ_PERMISSIONS = {
    'leader.overview.read', 'leader.map.read', 'leader.abnormal.read',
    'leader.age.read', 'leader.trend.read', 'leader.advice.read'
}
SUPPORT_READ_PERMISSIONS = {
    'support.search.read', 'support.users.read', 'support.devices.read',
    'support.stream.read', 'support.bind.read'
}
ADMIN_PERMISSIONS = {item['key'] for item in PERMISSION_DEFINITIONS}
DEFAULT_ROLE_PERMISSIONS = {
    'leader': sorted(LEADER_READ_PERMISSIONS | {'leader.decision.edit'}),
    'support': sorted(SUPPORT_READ_PERMISSIONS | {'leader.advice.read', 'support.bind.edit'}),
    'admin': sorted(ADMIN_PERMISSIONS),
}

AGE_SEGMENTS = [
    ('18-25', 18, 25),
    ('26-35', 26, 35),
    ('36-45', 36, 45),
    ('46+', 46, 90),
]


def dashboard_role_allowed(current_user, roles):
    role = (current_user.role or '').lower()
    username = (current_user.username or '').lower()
    allowed = set(roles) | {'admin'}
    if role in allowed:
        return True
    if username == 'leader' and 'leader' in roles:
        return True
    if username == 'support' and 'support' in roles:
        return True
    return False


def require_dashboard_role(current_user, roles):
    if not dashboard_role_allowed(current_user, roles):
        return jsonify({'success': False, 'message': '当前账号无权访问该角色后台'}), 403
    return None


def normalize_permissions(permissions):
    valid = {item['key'] for item in PERMISSION_DEFINITIONS}
    result = []
    for item in permissions or []:
        key = str(item or '').strip()
        if key in valid and key not in result:
            result.append(key)
    return result


def has_read_permission(permissions):
    return any(str(item).endswith('.read') for item in permissions or [])


def user_permissions(user):
    role = (getattr(user, 'role', '') or '').lower()
    if role == 'admin':
        return sorted(ADMIN_PERMISSIONS)

    raw = getattr(user, 'email', None)
    if raw and str(raw).startswith('perm:'):
        try:
            body = str(raw)[5:].strip()
            if body.startswith('{') or body.startswith('['):
                payload = json.loads(body)
                permissions = normalize_permissions(payload.get('permissions') if isinstance(payload, dict) else payload)
            else:
                permissions = normalize_permissions(
                    PERMISSION_KEYS[int(code)]
                    for code in body.split(',')
                    if code.strip().isdigit() and int(code) < len(PERMISSION_KEYS)
                )
            if permissions:
                return permissions
        except Exception:
            pass
    return DEFAULT_ROLE_PERMISSIONS.get(role, [])


def set_user_permissions(user, permissions):
    codes = [PERMISSION_INDEX[key] for key in normalize_permissions(permissions)]
    user.email = 'perm:' + ','.join(codes)


def has_permission(user, permission):
    return permission in user_permissions(user)


def require_permission(current_user, permission):
    if not has_permission(current_user, permission):
        return jsonify({'success': False, 'message': '当前账号没有该操作权限'}), 403
    return None


def ensure_admin_account():
    now = datetime.now()
    admin = User.query.filter(User.role == 'admin').order_by(User.created_at.asc()).first()
    if not admin:
        bootstrap_username = os.environ.get('ROLE_DASHBOARD_ADMIN_USER')
        bootstrap_password = os.environ.get('ROLE_DASHBOARD_ADMIN_PASSWORD')
        if not bootstrap_username or not bootstrap_password:
            return None
        admin = User(
            username=bootstrap_username,
            password_hash=hash_password(bootstrap_password),
            phone='18800000000',
            nickname='超级管理员',
            role='admin',
            status='active',
            created_at=now,
            updated_at=now
        )
        db.session.add(admin)
    admin.role = 'admin'
    admin.status = 'active'
    admin.nickname = admin.nickname or '超级管理员'
    set_user_permissions(admin, ADMIN_PERMISSIONS)
    db.session.commit()
    return admin



def account_payload(user):
    return {
        'id': user.id,
        'username': user.username,
        'nickname': user.nickname,
        'role': user.role,
        'status': user.status,
        'permissions': user_permissions(user),
        'created_at': row_to_iso(user.created_at),
        'last_login': row_to_iso(user.last_login)
    }


def safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value, default=0):
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def province_catalog():
    return {item['name']: item for item in ROLE_PROVINCES}


def clamp(value, low, high):
    return max(low, min(high, value))


def current_demo_scenario(now=None):
    now = now or datetime.now()
    return {
        'bucket': 'database-threshold-v1',
        'generated_at': now.replace(microsecond=0).isoformat(),
        'abnormal_provinces': set()
    }


def province_from_location(location):
    text = str(location or '').strip()
    if not text:
        return None
    catalog = province_catalog()
    first = re.split(r'[-\s/]', text, maxsplit=1)[0]
    if first in catalog:
        return first
    for info in sorted(ROLE_PROVINCES, key=lambda item: len(item['name']), reverse=True):
        if text.startswith(info['name']):
            return info['name']
    return None


def demo_values_for_province(province, scenario=None):
    catalog = province_catalog()
    info = catalog.get(province) or ROLE_PROVINCES[0]
    key = f"province-default:{info['name']}"
    humidity = clamp(info.get('base_humidity', 55) + stable_float(f"{key}:humidity-offset", -4.5, 4.5), 28.0, 84.0)
    moisture = expected_moisture_for_humidity(humidity) + stable_float(f"{key}:moisture-offset", -2.0, 3.2)

    return {
        'humidity': round(clamp(humidity, 25.0, 86.0), 1),
        'moisture': int(round(clamp(moisture, 28.0, 66.0))),
        'oiliness': int(round(clamp(38 + stable_float(f"{key}:oiliness-offset", -8, 10), 20, 68))),
        'skin_temperature': round(clamp(32.4 + stable_float(f"{key}:skin-temp-offset", -0.7, 1.2), 30.8, 35.0), 1),
        'environment_temperature': round(clamp(24.5 + stable_float(f"{key}:env-temp-offset", -4.0, 5.0), 18.0, 33.0), 1),
        'pm25': stable_int(f"{key}:pm25", 8, 52),
        'co2': stable_int(f"{key}:co2", 420, 980),
        'quality_score': stable_float(f"{key}:quality", 0.93, 0.99, 2)
    }


def load_leader_decisions():
    try:
        if not os.path.exists(LEADER_DECISION_STORE):
            return []
        with open(LEADER_DECISION_STORE, 'r', encoding='utf-8') as handle:
            rows = json.load(handle)
        if not isinstance(rows, list):
            return []
        return rows[:80]
    except Exception as err:
        logger.warning(f"load leader decisions failed: {err}")
        return []


def save_leader_decisions(rows):
    directory = os.path.dirname(LEADER_DECISION_STORE)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    with open(LEADER_DECISION_STORE, 'w', encoding='utf-8') as handle:
        json.dump(rows[:80], handle, ensure_ascii=False, indent=2)


def ensure_demo_binding(user, device_id, is_primary=False, now=None):
    from models import DeviceBinding

    now = now or datetime.now()
    for binding in DeviceBinding.query.filter_by(device_id=device_id, status='active').all():
        if binding.user_id != user.id:
            binding.status = 'unbound'
            binding.unbind_time = now
    binding = DeviceBinding.query.filter_by(user_id=user.id, device_id=device_id).first()
    if binding:
        binding.status = 'active'
        binding.unbind_time = None
        binding.is_primary = bool(is_primary)
        binding.bind_time = binding.bind_time or now
        return binding
    binding = DeviceBinding(
        user_id=user.id,
        device_id=device_id,
        bind_time=now,
        is_primary=bool(is_primary),
        status='active',
        notes='role-dashboard-demo'
    )
    db.session.add(binding)
    return binding


def upsert_demo_device(device_id, device_type, info, slot, now):
    device = Device.query.filter_by(device_id=device_id).first()
    if not device:
        device = Device(
            device_id=device_id,
            device_type=device_type,
            firmware_version='v2.3.0',
            install_date=now.date(),
            location=f"{info['name']}-{info['city']}-演示点位{slot}",
            status='online',
            battery_level=88,
            signal_strength=-48,
            last_heartbeat=now,
            created_at=now,
            updated_at=now
        )
        db.session.add(device)
    else:
        device.device_type = device_type
        device.firmware_version = device.firmware_version or 'v2.3.0'
        device.location = f"{info['name']}-{info['city']}-演示点位{slot}"
        device.status = 'online'
        device.battery_level = device.battery_level or 88
        device.signal_strength = device.signal_strength or -48
        device.last_heartbeat = now
        device.updated_at = now
    return device


def ensure_role_demo_dataset(scenario=None):
    from models import DeviceBinding, UserProfile

    scenario = scenario or current_demo_scenario()
    now = datetime.now().replace(microsecond=0)
    if ROLE_DEMO_DATASET_CACHE.get('ready_until') and ROLE_DEMO_DATASET_CACHE['ready_until'] > now:
        cached = dict(ROLE_DEMO_DATASET_CACHE.get('state') or {})
        cached['scenario'] = scenario
        return cached

    created_or_updated = 0
    demo_usernames = [f"demo_p{index:02d}_{slot}" for index in range(1, len(ROLE_PROVINCES) + 1) for slot in (1, 2)]
    demo_device_ids = []
    for index in range(1, len(ROLE_PROVINCES) + 1):
        demo_device_ids.extend([f"SKP{index:02d}1", f"ENV{index:02d}1", f"SKP{index:02d}2"])

    users_by_name = {user.username: user for user in User.query.filter(User.username.in_(demo_usernames)).all()}
    devices_by_id = {device.device_id: device for device in Device.query.filter(Device.device_id.in_(demo_device_ids)).all()}
    profiles_by_user = {}
    if users_by_name:
        profiles_by_user = {
            profile.user_id: profile
            for profile in UserProfile.query.filter(UserProfile.user_id.in_([user.id for user in users_by_name.values()])).all()
        }
    bindings_by_key = {
        (binding.user_id, binding.device_id): binding
        for binding in DeviceBinding.query.filter(DeviceBinding.device_id.in_(demo_device_ids)).all()
    }

    for index, info in enumerate(ROLE_PROVINCES, start=1):
        for slot in (1, 2):
            username = f"demo_p{index:02d}_{slot}"
            user = users_by_name.get(username)
            if not user:
                user = User(
                    username=username,
                    password_hash=hash_password(uuid.uuid4().hex),
                    phone=f"188{index:02d}{slot:06d}",
                    nickname=f"{info['name']}监测用户{slot}",
                    email=f"{username}@dierzunb666.cn",
                    role='user',
                    status='active',
                    created_at=now,
                    updated_at=now
                )
                db.session.add(user)
                db.session.flush()
                users_by_name[username] = user
                created_or_updated += 1
            else:
                user.role = 'user'
                user.status = 'active'
                user.nickname = user.nickname or f"{info['name']}监测用户{slot}"
                user.updated_at = now

            profile = profiles_by_user.get(user.id)
            goals = {
                'province': info['name'],
                'city': info['city'],
                'region': info['region'],
                'usage_frequency': round(3.5 + ((index + slot) % 6) * 0.8, 1),
                'member_level': ['普通', '银卡', '金卡', '重点跟进'][(index + slot) % 4],
                'demo_source': 'role-dashboard'
            }
            if not profile:
                profile = UserProfile(
                    user_id=user.id,
                    skin_type=['混合性', '干性', '油性', '敏感性'][(index + slot) % 4],
                    skincare_goals=goals,
                    age=19 + ((index * 3 + slot * 5) % 35),
                    gender='女' if (index + slot) % 3 else '男',
                    register_date=now,
                    last_update=now
                )
                db.session.add(profile)
                profiles_by_user[user.id] = profile
            else:
                profile.skincare_goals = goals
                profile.age = profile.age or (19 + ((index * 3 + slot * 5) % 35))
                profile.gender = profile.gender or ('女' if (index + slot) % 3 else '男')
                profile.skin_type = profile.skin_type or ['混合性', '干性', '油性', '敏感性'][(index + slot) % 4]
                profile.last_update = now

            skin_device_id = f"SKP{index:02d}{slot}"
            skin_device = devices_by_id.get(skin_device_id) or upsert_demo_device(skin_device_id, 'skin', info, slot, now)
            devices_by_id[skin_device_id] = skin_device
            binding = bindings_by_key.get((user.id, skin_device_id))
            if binding:
                binding.status = 'active'
                binding.unbind_time = None
                binding.is_primary = True
                binding.bind_time = binding.bind_time or now
            else:
                bindings_by_key[(user.id, skin_device_id)] = ensure_demo_binding(user, skin_device_id, is_primary=True, now=now)

            if slot == 1:
                env_device_id = f"ENV{index:02d}1"
                env_device = devices_by_id.get(env_device_id) or upsert_demo_device(env_device_id, 'environment', info, slot, now)
                devices_by_id[env_device_id] = env_device
                binding = bindings_by_key.get((user.id, env_device_id))
                if binding:
                    binding.status = 'active'
                    binding.unbind_time = None
                    binding.is_primary = False
                    binding.bind_time = binding.bind_time or now
                else:
                    bindings_by_key[(user.id, env_device_id)] = ensure_demo_binding(user, env_device_id, is_primary=False, now=now)

    db.session.commit()
    state = {
        'users': len(ROLE_PROVINCES) * 2,
        'devices': len(demo_device_ids),
        'created_or_updated': created_or_updated,
        'scenario': scenario
    }
    ROLE_DEMO_DATASET_CACHE['ready_until'] = now + timedelta(minutes=10)
    ROLE_DEMO_DATASET_CACHE['state'] = dict(state)
    return state


def parse_profile_meta(profile, user=None):
    goals = {}
    if profile and profile.skincare_goals:
        if isinstance(profile.skincare_goals, dict):
            goals = profile.skincare_goals
        elif isinstance(profile.skincare_goals, str):
            try:
                parsed = json.loads(profile.skincare_goals)
                goals = parsed if isinstance(parsed, dict) else {}
            except Exception:
                goals = {}

    catalog = province_catalog()
    fallback = ROLE_PROVINCES[(safe_int(getattr(user, 'id', 1), 1) - 1) % len(ROLE_PROVINCES)]
    province = str(goals.get('province') or goals.get('region') or fallback['name'])
    if province not in catalog:
        province = fallback['name']
    province_info = catalog[province]
    return {
        'province': province,
        'city': goals.get('city') or province_info['city'],
        'region': province_info['region'],
        'age': safe_int(getattr(profile, 'age', None), 28 + (safe_int(getattr(user, 'id', 1), 1) % 26)),
        'gender': getattr(profile, 'gender', None) or goals.get('gender') or ('女' if safe_int(getattr(user, 'id', 1), 1) % 3 else '男'),
        'skin_type': getattr(profile, 'skin_type', None) or goals.get('skin_type') or '混合性',
        'usage_frequency': safe_float(goals.get('usage_frequency'), 4.0 + (safe_int(getattr(user, 'id', 1), 1) % 5)),
        'member_level': goals.get('member_level') or ['普通', '银卡', '金卡', '重点跟进'][safe_int(getattr(user, 'id', 1), 1) % 4],
    }


def row_to_iso(value):
    return value.isoformat() if value else None


def is_environment_device(device):
    device_type = str(getattr(device, 'device_type', '') or '').lower()
    device_id = str(getattr(device, 'device_id', '') or '').upper()
    return device_type == 'environment' or device_id.startswith('ENV') or device_id.startswith('RENV')


def latest_device_rows(device, limit=16):
    if not device:
        return [], 'skin'
    cutoff = datetime.now()
    if is_environment_device(device):
        rows = EnvironmentSensorData.query.filter_by(device_id=device.device_id).filter(
            EnvironmentSensorData.sensor_time <= cutoff
        ).order_by(
            EnvironmentSensorData.sensor_time.desc()
        ).limit(limit).all()
        return [row.to_dict() for row in rows], 'environment'
    rows = SkinSensorData.query.filter_by(device_id=device.device_id).filter(
        SkinSensorData.sensor_time <= cutoff
    ).order_by(
        SkinSensorData.sensor_time.desc()
    ).limit(limit).all()
    return [row.to_dict() for row in rows], 'skin'


def append_live_sample(device, now=None, force=False, scenario=None):
    if not device:
        return None
    now = now or datetime.now().replace(microsecond=0)
    latest = None
    if is_environment_device(device):
        latest = EnvironmentSensorData.query.filter_by(device_id=device.device_id).order_by(
            EnvironmentSensorData.sensor_time.desc()
        ).first()
    else:
        latest = SkinSensorData.query.filter_by(device_id=device.device_id).order_by(
            SkinSensorData.sensor_time.desc()
        ).first()
    if not force and latest and latest.sensor_time and (now - latest.sensor_time).total_seconds() < 18:
        device.last_heartbeat = now
        device.updated_at = now
        return None

    province = province_from_location(getattr(device, 'location', None))
    demo_values = demo_values_for_province(province) if province else None
    request_id = 'live-{}-{}'.format(device.device_id, now.strftime('%Y%m%d%H%M%S'))
    device.status = 'online'
    device.last_heartbeat = now
    device.updated_at = now
    if device.battery_level is None:
        device.battery_level = stable_int(f"{device.device_id}:battery-live", 66, 99)
    if device.signal_strength is None:
        device.signal_strength = stable_int(f"{device.device_id}:signal-live", -70, -38)

    if is_environment_device(device):
        base = province_catalog().get(province, {}).get('base_humidity', 58)
        row = EnvironmentSensorData(
            device_id=device.device_id,
            temperature=demo_values['environment_temperature'] if demo_values else stable_float(f"{device.device_id}:live-env-temp", 21.0, 30.0),
            humidity=demo_values['humidity'] if demo_values else round(max(25, min(86, base + stable_float(f"{device.device_id}:live-humidity-offset", -7, 7))), 1),
            pm25=demo_values['pm25'] if demo_values else stable_int(f"{device.device_id}:live-pm25", 8, 52),
            co2=demo_values['co2'] if demo_values else stable_int(f"{device.device_id}:live-co2", 430, 980),
            location=device.location,
            sensor_time=now,
            received_at=now,
            client_ip='role-dashboard',
            request_id=request_id,
            validated=True,
            quality_score=demo_values['quality_score'] if demo_values else stable_float(f"{device.device_id}:live-quality", 0.92, 0.99, 2),
            created_at=now
        )
    else:
        row = SkinSensorData(
            device_id=device.device_id,
            moisture=demo_values['moisture'] if demo_values else stable_int(f"{device.device_id}:live-moisture", 35, 63),
            oiliness=demo_values['oiliness'] if demo_values else stable_int(f"{device.device_id}:live-oiliness", 26, 62),
            temperature=demo_values['skin_temperature'] if demo_values else stable_float(f"{device.device_id}:live-skin-temp", 31.5, 35.3),
            sensor_time=now,
            received_at=now,
            client_ip='role-dashboard',
            request_id=request_id,
            validated=True,
            quality_score=demo_values['quality_score'] if demo_values else stable_float(f"{device.device_id}:live-quality", 0.92, 0.99, 2),
            created_at=now
        )
    db.session.add(row)
    return row


def touch_live_stream(limit=12, force=True, scenario=None):
    try:
        devices = Device.query.filter(Device.status == 'online').order_by(Device.last_heartbeat.asc()).limit(limit).all()
        now = datetime.now().replace(microsecond=0)
        for device in devices:
            append_live_sample(device, now=now, force=force, scenario=scenario)
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        logger.warning(f"role dashboard live stream skipped: {err}")


def avg_skin_for_devices(device_ids, start_dt=None):
    if not device_ids:
        return None
    rows = []
    for device_id in device_ids:
        row = SkinSensorData.query.filter_by(device_id=device_id).order_by(
            SkinSensorData.sensor_time.desc(),
            SkinSensorData.id.desc()
        ).first()
        if row:
            rows.append(row)
    if not rows:
        return None
    return (
        average_numeric([row.moisture for row in rows]),
        average_numeric([row.oiliness for row in rows]),
        average_numeric([row.temperature for row in rows]),
        len(rows)
    )


def avg_env_for_devices(device_ids, start_dt=None):
    if not device_ids:
        return None
    rows = []
    for device_id in device_ids:
        row = EnvironmentSensorData.query.filter_by(device_id=device_id).order_by(
            EnvironmentSensorData.sensor_time.desc(),
            EnvironmentSensorData.id.desc()
        ).first()
        if row:
            rows.append(row)
    if not rows:
        return None
    return (
        average_numeric([row.humidity for row in rows]),
        average_numeric([row.temperature for row in rows]),
        average_numeric([row.pm25 for row in rows]),
        average_numeric([row.co2 for row in rows]),
        len(rows)
    )


def expected_moisture_for_humidity(humidity):
    return max(36.0, min(58.0, 28.0 + 0.35 * safe_float(humidity, 55.0)))


def humidity_mismatch(humidity, moisture):
    humidity = safe_float(humidity, 55.0)
    moisture = safe_float(moisture, 45.0)
    expected = expected_moisture_for_humidity(humidity)
    gap = moisture - expected
    reasons = []
    if gap < -10:
        reasons.append('皮肤水分明显低于当前环境湿度下的预期值')
    elif gap < -7:
        reasons.append('皮肤水分低于环境湿度匹配区间')
    if humidity >= 68 and moisture < 44:
        reasons.append('高湿环境下水分仍偏低，可能存在使用习惯或设备采集问题')
    if humidity <= 36 and moisture < 38:
        reasons.append('低湿环境叠加低水分，干燥风险较高')
    if moisture < 35:
        reasons.append('用户平均水分处于低位')

    score = max(0, int(abs(min(gap, 0)) * 8))
    if humidity <= 36:
        score += 10
    if humidity >= 68 and moisture < 44:
        score += 18
    if moisture < 35:
        score += 20
    is_abnormal = score >= 35 or bool(reasons[:2])
    level = '高' if score >= 58 else ('中' if is_abnormal else '低')
    return {
        'expected_moisture': round(expected, 1),
        'gap': round(gap, 1),
        'score': min(score, 100),
        'is_abnormal': is_abnormal,
        'level': level,
        'reason': '；'.join(reasons) if reasons else '环境湿度与皮肤水分处于可接受匹配区间',
        'recommendation': '建议客服优先回访该省低水分用户，核对设备佩戴/采集方式，并推送补水护理提醒。' if is_abnormal else '继续观察趋势，维持常规运营策略。'
    }


def dashboard_users_context(days=7):
    from models import DeviceBinding, UserProfile

    now = datetime.now()
    start_dt = now - timedelta(days=max(1, min(days, 90)))
    users = User.query.filter(User.status == 'active', User.role == 'user').all()
    if not users:
        users = User.query.filter(User.status == 'active').filter(User.username.notin_(['leader', 'support'])).all()

    profiles = {p.user_id: p for p in UserProfile.query.filter(UserProfile.user_id.in_([u.id for u in users] or [0])).all()}
    active_bindings = DeviceBinding.query.filter(DeviceBinding.status == 'active').all()
    devices = {device.device_id: device for device in Device.query.all()}
    bindings_by_user = {}
    for binding in active_bindings:
        bindings_by_user.setdefault(binding.user_id, []).append(binding)

    contexts = []
    for user in users:
        profile = profiles.get(user.id)
        meta = parse_profile_meta(profile, user)
        bindings = bindings_by_user.get(user.id, [])
        user_devices = []
        skin_device_ids = []
        env_device_ids = []
        for binding in bindings:
            device = devices.get(binding.device_id)
            if not device:
                continue
            item = device.to_dict()
            item['binding_id'] = binding.id
            item['bind_time'] = row_to_iso(binding.bind_time)
            item['is_primary'] = binding.is_primary
            user_devices.append(item)
            if is_environment_device(device):
                env_device_ids.append(device.device_id)
            else:
                skin_device_ids.append(device.device_id)

        skin_avg = avg_skin_for_devices(skin_device_ids, start_dt)
        env_avg = avg_env_for_devices(env_device_ids, start_dt)
        skin_count = safe_int(skin_avg[3] if skin_avg else 0)
        env_count = safe_int(env_avg[4] if env_avg else 0)

        contexts.append({
            'user': user,
            'profile': profile,
            'meta': meta,
            'bindings': bindings,
            'devices': user_devices,
            'skin_device_ids': skin_device_ids,
            'env_device_ids': env_device_ids,
            'skin_avg': skin_avg,
            'env_avg': env_avg,
            'skin_records': skin_count,
            'env_records': env_count,
            'avg_moisture': round(safe_float(skin_avg[0]), 1) if skin_count else None,
            'avg_humidity': round(safe_float(env_avg[0]), 1) if env_count else None,
        })
    return contexts, start_dt


def build_province_metrics(contexts, start_dt, scenario=None):
    scenario = scenario or current_demo_scenario()
    catalog = province_catalog()
    buckets = {}
    for info in ROLE_PROVINCES:
        buckets[info['name']] = {
            'province': info['name'],
            'city': info['city'],
            'region': info['region'],
            'x': info['x'],
            'y': info['y'],
            'user_count': 0,
            'device_count': 0,
            'skin_device_ids': set(),
            'env_device_ids': set(),
            'ages': [],
            'usage_values': [],
            'moisture_values': [],
            'oiliness_values': [],
            'skin_temp_values': [],
            'humidity_values': [],
            'env_temp_values': [],
            'skin_records': 0,
            'env_records': 0,
        }

    for ctx in contexts:
        province = ctx['meta']['province']
        bucket = buckets.setdefault(province, {
            'province': province,
            'city': catalog.get(province, {}).get('city', province),
            'region': catalog.get(province, {}).get('region', '其他'),
            'x': catalog.get(province, {}).get('x', 500),
            'y': catalog.get(province, {}).get('y', 450),
            'user_count': 0,
            'device_count': 0,
            'skin_device_ids': set(),
            'env_device_ids': set(),
            'ages': [],
            'usage_values': [],
            'moisture_values': [],
            'oiliness_values': [],
            'skin_temp_values': [],
            'humidity_values': [],
            'env_temp_values': [],
            'skin_records': 0,
            'env_records': 0,
        })
        bucket['user_count'] += 1
        bucket['device_count'] += len(ctx['devices'])
        bucket['skin_device_ids'].update(ctx['skin_device_ids'])
        bucket['env_device_ids'].update(ctx['env_device_ids'])
        bucket['ages'].append(ctx['meta']['age'])
        bucket['usage_values'].append(ctx['meta']['usage_frequency'])
        if ctx.get('skin_records'):
            bucket['skin_records'] += ctx['skin_records']
            bucket['moisture_values'].append(ctx['avg_moisture'])
            if ctx.get('skin_avg'):
                bucket['oiliness_values'].append(ctx['skin_avg'][1])
                bucket['skin_temp_values'].append(ctx['skin_avg'][2])
        if ctx.get('env_records'):
            bucket['env_records'] += ctx['env_records']
            bucket['humidity_values'].append(ctx['avg_humidity'])
            if ctx.get('env_avg'):
                bucket['env_temp_values'].append(ctx['env_avg'][1])

    metrics = []
    for name, bucket in buckets.items():
        province_info = catalog.get(name, {})
        scenario_values = demo_values_for_province(name, scenario)
        avg_moisture = average_numeric(bucket['moisture_values'])
        avg_oiliness = average_numeric(bucket['oiliness_values'])
        avg_skin_temp = average_numeric(bucket['skin_temp_values'])
        avg_humidity = average_numeric(bucket['humidity_values'])
        avg_env_temp = average_numeric(bucket['env_temp_values'])
        record_count = bucket['skin_records'] + bucket['env_records']
        usage_frequency = round(sum(bucket['usage_values']) / len(bucket['usage_values']), 1) if bucket['usage_values'] else 0.0
        avg_age = round(sum(bucket['ages']) / len(bucket['ages']), 1) if bucket['ages'] else None
        if avg_humidity is None:
            avg_humidity = scenario_values['humidity']
        if avg_moisture is None:
            avg_moisture = scenario_values['moisture']
        if avg_oiliness is None:
            avg_oiliness = scenario_values['oiliness']
        if avg_skin_temp is None:
            avg_skin_temp = scenario_values['skin_temperature']
        if avg_env_temp is None:
            avg_env_temp = scenario_values['environment_temperature']
        mismatch = humidity_mismatch(avg_humidity, avg_moisture)
        metrics.append({
            'province': name,
            'city': bucket['city'],
            'region': bucket['region'],
            'x': bucket['x'],
            'y': bucket['y'],
            'user_count': bucket['user_count'],
            'device_count': bucket['device_count'],
            'active_devices': len(bucket['skin_device_ids']) + len(bucket['env_device_ids']),
            'avg_moisture': avg_moisture,
            'avg_oiliness': avg_oiliness,
            'avg_skin_temperature': avg_skin_temp,
            'avg_humidity': avg_humidity,
            'avg_environment_temperature': avg_env_temp,
            'record_count': record_count,
            'usage_frequency': usage_frequency,
            'avg_age': avg_age,
            'mismatch': mismatch,
            'is_abnormal': mismatch['is_abnormal'],
            'risk_level': mismatch['level'],
        })
    # === 2026-06-05: 追加数据库真实设备位置数据 ===
    try:
        db_devices = Device.query.filter(Device.location.isnot(None)).filter(Device.location != '').all()
        db_prov_count = {}
        for dev in db_devices:
            loc = (dev.location or '').strip()
            if not loc or loc in ('??', '?????'):
                continue
            parts = loc.split('-')
            prov = parts[0].strip() if parts else loc
            if not prov:
                continue
            bucket = db_prov_count.setdefault(prov, {'devices': 0, 'skin': 0, 'env': 0, 'samples': set()})
            bucket['devices'] += 1
            if dev.device_type == 'environment':
                bucket['env'] += 1
            else:
                bucket['skin'] += 1
            bucket['samples'].add(loc)
        # 把数据库真实数量写回 metrics 中已存在的省份
        for p in metrics:
            db_data = db_prov_count.get(p['province'])
            if db_data:
                p['db_device_count'] = db_data['devices']
                p['db_skin_devices'] = db_data['skin']
                p['db_env_devices'] = db_data['env']
                p['db_location_samples'] = list(db_data['samples'])[:3]
    except Exception as _e:
        logger.warning(f"加载数据库设备位置失败: {_e}")

    return sorted(metrics, key=lambda item: (item['is_abnormal'], item['mismatch']['score'], item['user_count'], item['record_count']), reverse=True)


def build_daily_trend(days=14, scenario=None):
    now = datetime.now()
    start_date = (now - timedelta(days=days - 1)).date()
    stat_rows = {
        row.stat_date.isoformat(): row
        for row in DailyStatistics.query.filter(
            DailyStatistics.stat_date >= start_date,
            DailyStatistics.stat_date <= now.date()
        ).all()
    }

    rows = []
    for offset in range(days):
        day = start_date + timedelta(days=offset)
        key = day.isoformat()
        stat = stat_rows.get(key)
        fallback = demo_values_for_province(ROLE_PROVINCES[offset % len(ROLE_PROVINCES)]['name'])
        total_records = safe_int(getattr(stat, 'total_records', 0), 0) if stat else 0
        active_devices = safe_int(getattr(stat, 'active_devices', 0), 0) if stat else 0
        rows.append({
            'date': key,
            'avg_moisture': round(safe_float(getattr(stat, 'avg_moisture', None), fallback['moisture']), 1),
            'avg_humidity': round(safe_float(getattr(stat, 'avg_humidity', None), fallback['humidity']), 1),
            'skin_records': total_records,
            'environment_records': 0,
            'active_devices': active_devices or stable_int(f"trend-active:{key}", 78, 100)
        })
    return rows


def build_age_segments(contexts):
    result = []
    for label, min_age, max_age in AGE_SEGMENTS:
        subset = [ctx for ctx in contexts if min_age <= ctx['meta']['age'] <= max_age]
        moisture_values = []
        humidity_values = []
        mismatch_count = 0
        for ctx in subset:
            values = demo_values_for_province(ctx['meta']['province'])
            moisture = ctx.get('avg_moisture') if ctx.get('avg_moisture') is not None else values['moisture']
            humidity = ctx.get('avg_humidity') if ctx.get('avg_humidity') is not None else values['humidity']
            moisture_values.append(moisture)
            humidity_values.append(humidity)
            mismatch_count += 1 if humidity_mismatch(humidity, moisture)['is_abnormal'] else 0
        usage = [ctx['meta']['usage_frequency'] for ctx in subset]
        result.append({
            'segment': label,
            'user_count': len(subset),
            'avg_moisture': round(sum(moisture_values) / len(moisture_values), 1) if moisture_values else 0,
            'avg_humidity': round(sum(humidity_values) / len(humidity_values), 1) if humidity_values else 0,
            'avg_usage_frequency': round(sum(usage) / len(usage), 1) if usage else 0,
            'abnormal_rate': round((mismatch_count / len(subset)) * 100, 1) if subset else 0,
            'insight': '年轻用户活跃度更高，适合推送即时补水反馈。' if label in ('18-25', '26-35') else '该年龄段更需要稳定护理提醒和客服跟进。'
        })
    return result


def support_user_summary(user, profile=None, devices=None):
    meta = parse_profile_meta(profile, user)
    return {
        'id': user.id,
        'username': user.username,
        'nickname': user.nickname,
        'phone': user.phone,
        'role': user.role,
        'status': user.status,
        'last_login': row_to_iso(user.last_login),
        'created_at': row_to_iso(user.created_at),
        'profile': meta,
        'device_count': len(devices or [])
    }


def is_broken_text(value):
    text = str(value or '').strip()
    if not text:
        return True
    if text in {'?', '??', '???', '????', '?????', '??????', '--'}:
        return True
    return text.count('?') >= max(2, len(text) // 2) or '\ufffd' in text


def device_region_meta(device, user=None, profile=None):
    meta = parse_profile_meta(profile, user) if user else None
    location = str(getattr(device, 'location', None) or '').strip()
    province = meta['province'] if meta else None
    city = meta['city'] if meta else None
    prefer_profile_location = False

    if location and not is_broken_text(location):
        normalized = location.replace('－', '-').replace('—', '-').replace(' ', '-')
        parts = [part for part in normalized.split('-') if part]
        location_province = parts[0] if parts else None
        if meta and location_province and location_province != meta['province']:
            prefer_profile_location = True
        if parts:
            province = province or parts[0]
        if len(parts) > 1:
            city = city or parts[1]

    if not province:
        province = '未分配地区'
    if not city:
        city = province

    if is_broken_text(location) or prefer_profile_location:
        location_display = f"{province}-{city}-设备点位"
    else:
        location_display = location

    return {
        'province': province,
        'city': city,
        'region': (meta or {}).get('region') if meta else None,
        'location_display': location_display
    }


def support_device_summary(device, binding=None, user=None):
    from models import UserProfile

    profile = UserProfile.query.filter_by(user_id=user.id).first() if user else None
    region_meta = device_region_meta(device, user, profile)
    latest_rows, data_type = latest_device_rows(device, limit=1)
    latest = latest_rows[0] if latest_rows else None
    return {
        'id': device.id,
        'device_id': device.device_id,
        'device_type': 'environment' if is_environment_device(device) else 'skin',
        'firmware_version': device.firmware_version,
        'location': device.location,
        'location_display': region_meta['location_display'],
        'province': region_meta['province'],
        'city': region_meta['city'],
        'region': region_meta['region'],
        'status': device.status,
        'battery_level': device.battery_level,
        'signal_strength': device.signal_strength,
        'last_heartbeat': row_to_iso(device.last_heartbeat),
        'binding_id': binding.id if binding else None,
        'bind_time': row_to_iso(binding.bind_time) if binding else None,
        'is_primary': binding.is_primary if binding else False,
        'user': {
            'id': user.id,
            'username': user.username,
            'nickname': user.nickname,
            'status': user.status,
            'profile': parse_profile_meta(profile, user)
        } if user else None,
        'data_type': data_type,
        'latest': latest
    }


@miniprogram_bp.route('/role-dashboard/me', methods=['GET'])
@token_required
def role_dashboard_me(current_user):
    return jsonify({
        'success': True,
        'user': account_payload(current_user),
        'role': current_user.role,
        'permissions': user_permissions(current_user),
        'permission_definitions': PERMISSION_DEFINITIONS
    }), 200


@miniprogram_bp.route('/role-dashboard/regions', methods=['GET'])
@token_required
def role_dashboard_regions(current_user):
    denied = require_permission(current_user, 'leader.map.read')
    if denied:
        return denied
    try:
        scenario = current_demo_scenario()
        ensure_role_demo_dataset(scenario)
        contexts, start_dt = dashboard_users_context(days=7)
        metrics = build_province_metrics(contexts, start_dt, scenario=scenario)
        return jsonify({
            'success': True,
            'regions': [{
                'province': item['province'],
                'city': item['city'],
                'region': item['region'],
                'user_count': item['user_count'],
                'device_count': item['device_count'],
                'avg_humidity': item['avg_humidity'],
                'avg_moisture': item['avg_moisture'],
                'is_abnormal': item['is_abnormal']
            } for item in metrics],
            'total': len(metrics)
        }), 200
    except Exception as e:
        logger.error(f"regions dashboard failed: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@miniprogram_bp.route('/role-dashboard/accounts', methods=['GET'])
@token_required
def role_dashboard_accounts(current_user):
    denied = require_permission(current_user, 'admin.accounts.read')
    if denied:
        return denied
    try:
        ensure_admin_account()
        rows = User.query.filter(User.role.in_(['admin', 'leader', 'support'])).order_by(User.created_at.desc()).all()
        return jsonify({
            'success': True,
            'accounts': [account_payload(user) for user in rows],
            'permission_definitions': PERMISSION_DEFINITIONS,
            'role_defaults': DEFAULT_ROLE_PERMISSIONS
        }), 200
    except Exception as e:
        logger.error(f"accounts list failed: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@miniprogram_bp.route('/role-dashboard/accounts', methods=['POST'])
@token_required
def role_dashboard_create_account(current_user):
    denied = require_permission(current_user, 'admin.accounts.edit')
    if denied:
        return denied
    try:
        data = request.get_json() or {}
        username = str(data.get('username') or '').strip()
        password = str(data.get('password') or '').strip()
        nickname = str(data.get('nickname') or username).strip()
        role = str(data.get('role') or 'support').strip().lower()
        if role not in {'admin', 'leader', 'support'}:
            return jsonify({'success': False, 'message': '角色只能是超级管理员、领导号或客服号'}), 400
        if not re.match(r'^[A-Za-z0-9_]{3,30}$', username):
            return jsonify({'success': False, 'message': '账号只能包含字母、数字、下划线，长度3-30位'}), 400
        if len(password) < 6:
            return jsonify({'success': False, 'message': '密码至少6位'}), 400
        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'message': '账号已存在'}), 409

        now = datetime.now()
        user = User(
            username=username,
            password_hash=hash_password(password),
            phone=str(data.get('phone') or stable_phone(username)),
            nickname=nickname,
            role=role,
            status='active',
            created_at=now,
            updated_at=now
        )
        requested_permissions = normalize_permissions(data.get('permissions') or DEFAULT_ROLE_PERMISSIONS.get(role, []))
        if not has_read_permission(requested_permissions):
            return jsonify({'success': False, 'message': '请至少勾选一个阅读权限'}), 400
        set_user_permissions(user, requested_permissions)
        db.session.add(user)
        db.session.commit()
        return jsonify({'success': True, 'account': account_payload(user)}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"account create failed: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@miniprogram_bp.route('/role-dashboard/accounts/<int:user_id>', methods=['PUT'])
@token_required
def role_dashboard_update_account(current_user, user_id):
    denied = require_permission(current_user, 'admin.accounts.edit')
    if denied:
        return denied
    try:
        data = request.get_json() or {}
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': '账号不存在'}), 404
        username = str(data.get('username') or user.username or '').strip()
        if not re.match(r'^[A-Za-z0-9_]{3,30}$', username):
            return jsonify({'success': False, 'message': '账号只能包含字母、数字、下划线，长度 3-30 位'}), 400
        existing = User.query.filter(User.username == username, User.id != user.id).first()
        if existing:
            return jsonify({'success': False, 'message': '账号已存在'}), 409
        role = str(data.get('role') or user.role or 'support').strip().lower()
        if role not in {'admin', 'leader', 'support'}:
            return jsonify({'success': False, 'message': '角色只能是超级管理员、领导号或客服号'}), 400
        user.username = username
        user.role = role
        if data.get('nickname') is not None:
            user.nickname = str(data.get('nickname') or user.username).strip()
        if data.get('password'):
            password = str(data.get('password')).strip()
            if len(password) < 6:
                return jsonify({'success': False, 'message': '密码至少6位'}), 400
            user.password_hash = hash_password(password)
        if data.get('status') in {'active', 'disabled'}:
            user.status = data.get('status')
        requested_permissions = normalize_permissions(data.get('permissions') or DEFAULT_ROLE_PERMISSIONS.get(role, []))
        if role != 'admin' and not has_read_permission(requested_permissions):
            return jsonify({'success': False, 'message': '请至少勾选一个阅读权限'}), 400
        user.role = role
        set_user_permissions(user, ADMIN_PERMISSIONS if role == 'admin' else requested_permissions)
        user.updated_at = datetime.now()
        db.session.commit()
        return jsonify({'success': True, 'account': account_payload(user)}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"account update failed: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@miniprogram_bp.route('/role-dashboard/leader', methods=['GET'])
@token_required
def role_dashboard_leader(current_user):
    if not (LEADER_READ_PERMISSIONS & set(user_permissions(current_user))):
        denied = jsonify({'success': False, 'message': '当前账号没有领导端阅读权限'}), 403
    else:
        denied = None
    if denied:
        return denied
    try:
        days = max(1, min(request.args.get('days', 7, type=int) or 7, 90))
        scenario = current_demo_scenario()
        demo_state = ensure_role_demo_dataset(scenario)
        contexts, start_dt = dashboard_users_context(days=days)
        province_metrics = build_province_metrics(contexts, start_dt, scenario=scenario)
        abnormal = [item for item in province_metrics if item['is_abnormal']]
        trend = build_daily_trend(days=14, scenario=scenario)
        age_segments = build_age_segments(contexts)
        populated = [p for p in province_metrics if p['user_count']]
        total_users = len(contexts)
        total_devices = sum(len(ctx['devices']) for ctx in contexts)
        avg_moisture = round(sum([p['avg_moisture'] for p in populated]) / max(len(populated), 1), 1)
        avg_humidity = round(sum([p['avg_humidity'] for p in populated]) / max(len(populated), 1), 1)
        active_today = safe_int(trend[-1]['active_devices'] if trend else 0)
        summary = {
            'users': total_users,
            'devices': total_devices,
            'provinces': len(populated),
            'abnormal_provinces': len(abnormal),
            'avg_moisture': avg_moisture,
            'avg_humidity': avg_humidity,
            'active_devices_24h': active_today,
            'usage_frequency': round(sum(ctx['meta']['usage_frequency'] for ctx in contexts) / max(total_users, 1), 1),
            'decision_index': max(0, 100 - len(abnormal) * 6)
        }
        suggestions = [
            {'title': '异常省份优先回访', 'content': '优先处理地图标红省份，核对当地环境湿度与用户水分差值，安排客服抽样回访。'},
            {'title': '按年龄做精细化运营', 'content': '18-35 岁用户活跃度高，适合推送即时反馈；36 岁以上用户更适合周报和护理提醒。'},
            {'title': '补齐环境采集覆盖', 'content': '环境设备覆盖不足的省份应优先补发环境传感器，避免只看皮肤数据导致误判。'}
        ]
        return jsonify({
            'success': True,
            'generated_at': datetime.now().isoformat(),
            'scenario': {
                'generated_at': scenario['generated_at'],
                'abnormal_count': len(scenario['abnormal_provinces']),
                'abnormal_provinces': sorted(scenario['abnormal_provinces']),
                'demo_users': demo_state['users'],
                'demo_devices': demo_state['devices']
            },
            'summary': summary,
            'province_metrics': province_metrics,
            'abnormal_provinces': abnormal[:8],
            'age_segments': age_segments,
            'trend': trend,
            'suggestions': suggestions,
            'leader_decisions': load_leader_decisions(),
            'mismatch_rule': {
                'name': '环境湿度-皮肤水分运营匹配规则',
                'formula': 'expected_moisture = clamp(28 + 0.35 * humidity, 36, 58)',
                'alert': '实际水分低于预期 7 个点以上，或低湿/高湿场景叠加低水分时标红'
            }
        }), 200
    except Exception as e:
        logger.error(f"leader dashboard failed: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@miniprogram_bp.route('/role-dashboard/leader/decisions', methods=['POST'])
@token_required
def role_dashboard_add_decision(current_user):
    denied = require_permission(current_user, 'leader.decision.edit')
    if denied:
        return denied
    try:
        data = request.get_json() or {}
        title = str(data.get('title') or '').strip()
        content = str(data.get('content') or '').strip()
        if not title:
            return jsonify({'success': False, 'message': '请填写决策标题'}), 400
        if not content:
            return jsonify({'success': False, 'message': '请填写决策内容'}), 400
        if len(title) > 80:
            return jsonify({'success': False, 'message': '决策标题不能超过80个字'}), 400
        if len(content) > 500:
            return jsonify({'success': False, 'message': '决策内容不能超过500个字'}), 400

        now = datetime.now().replace(microsecond=0)
        rows = load_leader_decisions()
        decision = {
            'id': uuid.uuid4().hex[:12],
            'title': title,
            'content': content,
            'author': current_user.nickname or current_user.username,
            'created_at': now.isoformat()
        }
        rows.insert(0, decision)
        save_leader_decisions(rows)
        return jsonify({'success': True, 'decision': decision, 'leader_decisions': rows[:80]}), 201
    except Exception as e:
        logger.error(f"add leader decision failed: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@miniprogram_bp.route('/role-dashboard/province/<province>', methods=['GET'])
@token_required
def role_dashboard_province(current_user, province):
    denied = require_permission(current_user, 'leader.map.read')
    if denied:
        return denied
    try:
        days = max(1, min(request.args.get('days', 7, type=int) or 7, 90))
        scenario = current_demo_scenario()
        ensure_role_demo_dataset(scenario)
        contexts, start_dt = dashboard_users_context(days=days)
        metrics = build_province_metrics(contexts, start_dt, scenario=scenario)
        selected = next((item for item in metrics if item['province'] == province), None)
        if not selected:
            return jsonify({'success': False, 'message': '省份不存在'}), 404
        province_users = [ctx for ctx in contexts if ctx['meta']['province'] == province]
        top_users = []
        for ctx in sorted(province_users, key=lambda item: item['skin_records'] + item['env_records'], reverse=True)[:10]:
            values = demo_values_for_province(province, scenario)
            moisture = ctx.get('avg_moisture') if ctx.get('avg_moisture') is not None else values['moisture']
            humidity = ctx.get('avg_humidity') if ctx.get('avg_humidity') is not None else values['humidity']
            top_users.append({
                'id': ctx['user'].id,
                'username': ctx['user'].username,
                'nickname': ctx['user'].nickname,
                'age': ctx['meta']['age'],
                'city': ctx['meta']['city'],
                'device_count': len(ctx['devices']),
                'avg_moisture': moisture,
                'avg_humidity': humidity,
                'records': ctx['skin_records'] + ctx['env_records']
            })
        age_breakdown = []
        for label, min_age, max_age in AGE_SEGMENTS:
            subset = [ctx for ctx in province_users if min_age <= ctx['meta']['age'] <= max_age]
            age_breakdown.append({'segment': label, 'user_count': len(subset)})
        return jsonify({
            'success': True,
            'province': selected,
            'users': top_users,
            'age_breakdown': age_breakdown,
            'analysis': {
                'summary': selected['mismatch']['reason'],
                'expected_moisture': selected['mismatch']['expected_moisture'],
                'actual_moisture': selected['avg_moisture'],
                'humidity': selected['avg_humidity'],
                'recommendation': selected['mismatch']['recommendation'],
                'business_action': '标红省份建议进入客服抽样名单；如果连续三天异常，领导端可安排区域运营策略。'
            }
        }), 200
    except Exception as e:
        logger.error(f"province dashboard failed: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@miniprogram_bp.route('/role-dashboard/support', methods=['GET'])
@token_required
def role_dashboard_support(current_user):
    if not (SUPPORT_READ_PERMISSIONS & set(user_permissions(current_user))):
        denied = jsonify({'success': False, 'message': '当前账号没有客服端阅读权限'}), 403
    else:
        denied = None
    if denied:
        return denied
    try:
        from models import DeviceBinding, UserProfile

        scenario = current_demo_scenario()
        ensure_role_demo_dataset(scenario)
        user_rows = User.query.filter(User.status == 'active', User.role == 'user').order_by(User.created_at.desc()).limit(100).all()
        profiles = {p.user_id: p for p in UserProfile.query.filter(UserProfile.user_id.in_([u.id for u in user_rows] or [0])).all()}
        active_bindings = DeviceBinding.query.filter(DeviceBinding.status == 'active').all()
        devices = {device.device_id: device for device in Device.query.all()}
        bindings_by_user = {}
        for binding in active_bindings:
            bindings_by_user.setdefault(binding.user_id, []).append(binding)

        users = []
        for user in user_rows:
            bound_devices = [devices[b.device_id].to_dict() for b in bindings_by_user.get(user.id, []) if b.device_id in devices]
            users.append(support_user_summary(user, profiles.get(user.id), bound_devices))

        device_cards = []
        for binding in active_bindings[:160]:
            device = devices.get(binding.device_id)
            user = User.query.get(binding.user_id)
            if device:
                device_cards.append(support_device_summary(device, binding, user))

        latest_cutoff = datetime.now()
        latest_events = []
        for row in SkinSensorData.query.filter(SkinSensorData.sensor_time <= latest_cutoff).order_by(SkinSensorData.sensor_time.desc()).limit(8).all():
            latest_events.append({
                'type': 'skin',
                'device_id': row.device_id,
                'time': row_to_iso(row.sensor_time),
                'moisture': row.moisture,
                'oiliness': row.oiliness,
                'temperature': row.temperature,
                'value': f"水分 {row.moisture}% / 油脂 {row.oiliness}%"
            })
        for row in EnvironmentSensorData.query.filter(EnvironmentSensorData.sensor_time <= latest_cutoff).order_by(EnvironmentSensorData.sensor_time.desc()).limit(8).all():
            latest_events.append({
                'type': 'environment',
                'device_id': row.device_id,
                'time': row_to_iso(row.sensor_time),
                'humidity': row.humidity,
                'temperature': row.temperature,
                'pm25': row.pm25,
                'co2': row.co2,
                'value': f"湿度 {row.humidity}% / 温度 {row.temperature}℃"
            })
        latest_events = sorted(latest_events, key=lambda item: item['time'] or '', reverse=True)[:12]

        return jsonify({
            'success': True,
            'summary': {
                'users': len(users),
                'devices': Device.query.count(),
                'active_bindings': len(active_bindings),
                'online_devices': Device.query.filter_by(status='online').count(),
                'unbound_devices': max(Device.query.count() - len(active_bindings), 0),
                'today_records': db.session.query(func.count(SkinSensorData.id)).filter(SkinSensorData.sensor_time >= datetime.now() - timedelta(days=1)).scalar() or 0
            },
            'users': users[:90],
            'devices': device_cards[:120],
            'events': latest_events
        }), 200
    except Exception as e:
        logger.error(f"support dashboard failed: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@miniprogram_bp.route('/role-dashboard/search', methods=['GET'])
@token_required
def role_dashboard_search(current_user):
    denied = require_permission(current_user, 'support.search.read')
    if denied:
        return denied
    try:
        from models import DeviceBinding, UserProfile

        ensure_role_demo_dataset(current_demo_scenario())
        keyword = (request.args.get('q') or '').strip()
        like = f"%{keyword}%"
        if keyword:
            user_query = User.query.filter(
                User.role == 'user',
                or_(
                    User.username.like(like),
                    User.nickname.like(like),
                    User.phone.like(like),
                    User.email.like(like),
                    User.id == safe_int(keyword, -1)
                )
            )
            device_query = Device.query.filter(or_(Device.device_id.like(like), Device.location.like(like), Device.device_type.like(like)))
        else:
            user_query = User.query.filter(User.role == 'user')
            device_query = Device.query

        users = user_query.order_by(User.last_login.desc()).limit(30).all()
        devices = device_query.order_by(Device.last_heartbeat.desc()).limit(40).all()
        profiles = {p.user_id: p for p in UserProfile.query.filter(UserProfile.user_id.in_([u.id for u in users] or [0])).all()}

        user_payload = []
        for user in users:
            bindings = DeviceBinding.query.filter_by(user_id=user.id, status='active').all()
            device_list = [Device.query.filter_by(device_id=b.device_id).first() for b in bindings]
            device_list = [d.to_dict() for d in device_list if d]
            user_payload.append(support_user_summary(user, profiles.get(user.id), device_list))

        device_payload = []
        for device in devices:
            binding = DeviceBinding.query.filter_by(device_id=device.device_id, status='active').first()
            user = User.query.get(binding.user_id) if binding else None
            device_payload.append(support_device_summary(device, binding, user))

        return jsonify({'success': True, 'users': user_payload, 'devices': device_payload}), 200
    except Exception as e:
        logger.error(f"support search failed: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@miniprogram_bp.route('/role-dashboard/user/<int:user_id>', methods=['GET'])
@token_required
def role_dashboard_user_detail(current_user, user_id):
    denied = require_permission(current_user, 'support.users.read')
    if denied:
        return denied
    try:
        from models import DeviceBinding, UserProfile

        scenario = current_demo_scenario()
        ensure_role_demo_dataset(scenario)
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        profile = UserProfile.query.filter_by(user_id=user.id).first()
        bindings = DeviceBinding.query.filter_by(user_id=user.id, status='active').all()
        devices = []
        streams = []
        for binding in bindings:
            device = Device.query.filter_by(device_id=binding.device_id).first()
            if not device:
                continue
            device_payload = support_device_summary(device, binding, user)
            rows, data_type = latest_device_rows(device, limit=10)
            device_payload['data'] = rows
            devices.append(device_payload)
            streams.extend([dict(row, data_type=data_type, owner=user.nickname or user.username) for row in rows[:5]])
        streams = sorted(streams, key=lambda item: item.get('sensor_time') or '', reverse=True)[:20]
        return jsonify({
            'success': True,
            'user': support_user_summary(user, profile, devices),
            'devices': devices,
            'stream': streams,
            'service_notes': [
                {'time': datetime.now().isoformat(), 'content': '系统自动生成：可核对用户最近一次皮肤水分与所在地环境湿度是否匹配。'},
                {'time': datetime.now().isoformat(), 'content': '客服动作：必要时重新绑定设备或指导用户重新采集。'}
            ]
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"user detail failed: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@miniprogram_bp.route('/role-dashboard/device/<device_id>', methods=['GET'])
@token_required
def role_dashboard_device_detail(current_user, device_id):
    denied = require_permission(current_user, 'support.devices.read')
    if denied:
        return denied
    try:
        from models import DeviceBinding, UserProfile

        scenario = current_demo_scenario()
        ensure_role_demo_dataset(scenario)
        device = Device.query.filter_by(device_id=device_id).first()
        if not device:
            return jsonify({'success': False, 'message': '设备不存在'}), 404
        binding = DeviceBinding.query.filter_by(device_id=device.device_id, status='active').first()
        user = User.query.get(binding.user_id) if binding else None
        profile = UserProfile.query.filter_by(user_id=user.id).first() if user else None
        rows, data_type = latest_device_rows(device, limit=24)
        return jsonify({
            'success': True,
            'device': support_device_summary(device, binding, user),
            'user': support_user_summary(user, profile, []) if user else None,
            'data_type': data_type,
            'stream': rows,
            'analysis': {
                'status': '在线正常' if device.status == 'online' else '离线待处理',
                'battery': device.battery_level,
                'signal': device.signal_strength,
                'advice': '信号低于 -68 dBm 时建议客服确认用户摆放位置；实时数据会随刷新继续写入。'
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"device detail failed: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@miniprogram_bp.route('/role-dashboard/bind', methods=['POST'])
@token_required
def role_dashboard_bind(current_user):
    denied = require_permission(current_user, 'support.bind.edit')
    if denied:
        return denied
    try:
        from models import DeviceBinding

        data = request.get_json() or {}
        user_id = safe_int(data.get('user_id'))
        device_id = str(data.get('device_id') or '').strip().upper()
        user = User.query.get(user_id)
        device = Device.query.filter_by(device_id=device_id).first()
        if not user or not device:
            return jsonify({'success': False, 'message': '用户或设备不存在'}), 404
        now = datetime.now()
        for binding in DeviceBinding.query.filter_by(device_id=device_id, status='active').all():
            binding.status = 'unbound'
            binding.unbind_time = now
        existing = DeviceBinding.query.filter_by(user_id=user.id, device_id=device_id).first()
        if existing:
            existing.status = 'active'
            existing.unbind_time = None
            existing.bind_time = now
            existing.is_primary = bool(data.get('is_primary', False))
            existing.notes = data.get('notes') or existing.notes
        else:
            db.session.add(DeviceBinding(
                user_id=user.id,
                device_id=device_id,
                bind_time=now,
                is_primary=bool(data.get('is_primary', False)),
                status='active',
                notes=data.get('notes') or 'support-dashboard'
            ))
        device.status = 'online'
        device.last_heartbeat = now
        device.updated_at = now
        db.session.commit()
        return jsonify({'success': True, 'message': '绑定成功'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"role bind failed: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@miniprogram_bp.route('/role-dashboard/unbind', methods=['POST'])
@token_required
def role_dashboard_unbind(current_user):
    denied = require_permission(current_user, 'support.bind.edit')
    if denied:
        return denied
    try:
        from models import DeviceBinding

        data = request.get_json() or {}
        binding_id = data.get('binding_id')
        device_id = str(data.get('device_id') or '').strip().upper()
        user_id = data.get('user_id')
        query = DeviceBinding.query.filter_by(status='active')
        if binding_id:
            query = query.filter_by(id=safe_int(binding_id))
        if device_id:
            query = query.filter_by(device_id=device_id)
        if user_id:
            query = query.filter_by(user_id=safe_int(user_id))
        rows = query.all()
        now = datetime.now()
        for binding in rows:
            binding.status = 'unbound'
            binding.unbind_time = now
        db.session.commit()
        return jsonify({'success': True, 'message': '解绑成功', 'affected': len(rows)}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"role unbind failed: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


def init_app(app):
    """初始化小程序路由"""
    app.register_blueprint(miniprogram_bp)
    app.register_blueprint(auth_bp)  # 注册auth蓝图以兼容小程序调用
    app.register_blueprint(short_path_bp)  # 注册简短路径兼容层
    logger.info("✅ 小程序路由注册成功")
