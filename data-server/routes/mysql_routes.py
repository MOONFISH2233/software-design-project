"""
MySQL数据库CRUD操作路由
提供对MySQL表的增删改查接口
"""

from flask import Blueprint, request, jsonify
from models import db, Device, SkinSensorData, EnvironmentSensorData, DailyStatistics, User
from datetime import datetime, timedelta
from sqlalchemy import func

mysql_bp = Blueprint('mysql', __name__, url_prefix='/api/mysql')


# =====================================================
# 设备管理接口
# =====================================================

@mysql_bp.route('/devices', methods=['GET'])
def get_devices():
    """获取设备列表(支持分页和筛选)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status', None)
        
        query = Device.query
        
        if status:
            query = query.filter(Device.status == status)
        
        pagination = query.order_by(Device.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'items': [device.to_dict() for device in pagination.items],
                'total': pagination.total,
                'page': page,
                'per_page': per_page,
                'pages': pagination.pages
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'查询失败: {str(e)}'}), 500


@mysql_bp.route('/devices/<string:device_id>', methods=['GET'])
def get_device(device_id):
    """获取单个设备详情"""
    try:
        device = Device.query.filter_by(device_id=device_id).first()
        if not device:
            return jsonify({'code': 404, 'message': '设备不存在'}), 404
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': device.to_dict()
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'查询失败: {str(e)}'}), 500


@mysql_bp.route('/devices', methods=['POST'])
def create_device():
    """创建设备"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('device_id'):
            return jsonify({'code': 400, 'message': 'device_id不能为空'}), 400
        
        # 检查设备是否已存在
        if Device.query.filter_by(device_id=data['device_id']).first():
            return jsonify({'code': 409, 'message': '设备ID已存在'}), 409
        
        device = Device(
            device_id=data['device_id'],
            device_type=data.get('device_type'),
            firmware_version=data.get('firmware_version'),
            install_date=datetime.strptime(data['install_date'], '%Y-%m-%d').date() if data.get('install_date') else None,
            location=data.get('location'),
            status=data.get('status', 'online')
        )
        
        db.session.add(device)
        db.session.commit()
        
        return jsonify({
            'code': 201,
            'message': '设备创建成功',
            'data': device.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'创建失败: {str(e)}'}), 500


@mysql_bp.route('/devices/<string:device_id>', methods=['PUT'])
def update_device(device_id):
    """更新设备信息"""
    try:
        device = Device.query.filter_by(device_id=device_id).first()
        if not device:
            return jsonify({'code': 404, 'message': '设备不存在'}), 404
        
        data = request.get_json()
        
        # 更新字段
        if 'device_type' in data:
            device.device_type = data['device_type']
        if 'firmware_version' in data:
            device.firmware_version = data['firmware_version']
        if 'location' in data:
            device.location = data['location']
        if 'status' in data:
            device.status = data['status']
        if 'battery_level' in data:
            device.battery_level = data['battery_level']
        if 'signal_strength' in data:
            device.signal_strength = data['signal_strength']
        if 'last_heartbeat' in data:
            device.last_heartbeat = datetime.fromisoformat(data['last_heartbeat'])
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '设备更新成功',
            'data': device.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'更新失败: {str(e)}'}), 500


@mysql_bp.route('/devices/<string:device_id>', methods=['DELETE'])
def delete_device(device_id):
    """删除设备"""
    try:
        device = Device.query.filter_by(device_id=device_id).first()
        if not device:
            return jsonify({'code': 404, 'message': '设备不存在'}), 404
        
        db.session.delete(device)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '设备删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'删除失败: {str(e)}'}), 500


# =====================================================
# 皮肤传感器数据接口
# =====================================================

@mysql_bp.route('/skin-data', methods=['GET'])
def get_skin_data():
    """获取皮肤传感器数据列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        device_id = request.args.get('device_id', None)
        start_date = request.args.get('start_date', None)
        end_date = request.args.get('end_date', None)
        
        query = SkinSensorData.query
        
        if device_id:
            query = query.filter(SkinSensorData.device_id == device_id)
        if start_date:
            query = query.filter(SkinSensorData.sensor_time >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(SkinSensorData.sensor_time <= datetime.fromisoformat(end_date))
        
        pagination = query.order_by(SkinSensorData.sensor_time.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'items': [item.to_dict() for item in pagination.items],
                'total': pagination.total,
                'page': page,
                'per_page': per_page
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'查询失败: {str(e)}'}), 500


@mysql_bp.route('/skin-data', methods=['POST'])
def create_skin_data():
    """创建皮肤传感器数据记录"""
    try:
        data = request.get_json()
        
        skin_data = SkinSensorData(
            device_id=data['device_id'],
            moisture=data['moisture'],
            oiliness=data['oiliness'],
            temperature=data.get('temperature'),
            sensor_time=datetime.fromisoformat(data['sensor_time']),
            client_ip=data.get('client_ip'),
            request_id=data.get('request_id'),
            validated=data.get('validated', True),
            quality_score=data.get('quality_score')
        )
        
        db.session.add(skin_data)
        db.session.commit()
        
        return jsonify({
            'code': 201,
            'message': '数据创建成功',
            'data': skin_data.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'创建失败: {str(e)}'}), 500


# =====================================================
# 环境传感器数据接口
# =====================================================

@mysql_bp.route('/environment-data', methods=['GET'])
def get_environment_data():
    """获取环境传感器数据列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        device_id = request.args.get('device_id', None)
        
        query = EnvironmentSensorData.query
        
        if device_id:
            query = query.filter(EnvironmentSensorData.device_id == device_id)
        
        pagination = query.order_by(EnvironmentSensorData.sensor_time.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'items': [item.to_dict() for item in pagination.items],
                'total': pagination.total,
                'page': page,
                'per_page': per_page
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'查询失败: {str(e)}'}), 500


# =====================================================
# 统计数据接口
# =====================================================

@mysql_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """获取每日统计数据"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 30, type=int)
        start_date = request.args.get('start_date', None)
        end_date = request.args.get('end_date', None)
        
        query = DailyStatistics.query
        
        if start_date:
            query = query.filter(DailyStatistics.stat_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(DailyStatistics.stat_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        pagination = query.order_by(DailyStatistics.stat_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'items': [item.to_dict() for item in pagination.items],
                'total': pagination.total,
                'page': page,
                'per_page': per_page
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'查询失败: {str(e)}'}), 500


@mysql_bp.route('/statistics/latest', methods=['GET'])
def get_latest_statistics():
    """获取最新统计数据"""
    try:
        stat = DailyStatistics.query.order_by(DailyStatistics.stat_date.desc()).first()
        
        if not stat:
            return jsonify({'code': 404, 'message': '暂无统计数据'}), 404
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': stat.to_dict()
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'查询失败: {str(e)}'}), 500


# =====================================================
# 用户管理接口
# =====================================================

@mysql_bp.route('/users', methods=['GET'])
def get_users():
    """获取用户列表"""
    try:
        users = User.query.all()
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': [user.to_dict() for user in users]
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'查询失败: {str(e)}'}), 500


@mysql_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """获取用户详情"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': user.to_dict()
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'查询失败: {str(e)}'}), 500
