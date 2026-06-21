"""
管理员管理端API路由
提供对系统全局数据的管理和统计分析功能
"""

from flask import Blueprint, request, jsonify
from models import db, Device, SkinSensorData, EnvironmentSensorData, DailyStatistics, User, DeviceBinding
from datetime import datetime, timedelta
from sqlalchemy import func, extract

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


# =====================================================
# 仪表盘统计接口
# =====================================================

@admin_bp.route('/dashboard', methods=['GET'])
def get_dashboard_stats():
    """获取仪表盘统计数据"""
    try:
        # 设备统计
        total_devices = Device.query.count()
        online_devices = Device.query.filter_by(status='online').count()
        offline_devices = Device.query.filter_by(status='offline').count()
        
        # 用户统计
        total_users = User.query.count()
        active_users = User.query.filter(User.last_login >= datetime.now() - timedelta(days=30)).count()
        
        # 今日数据统计
        today = datetime.now().date()
        today_skin_data = SkinSensorData.query.filter(
            func.date(SkinSensorData.sensor_time) == today
        ).count()
        today_env_data = EnvironmentSensorData.query.filter(
            func.date(EnvironmentSensorData.sensor_time) == today
        ).count()
        
        # 最近7天的数据趋势
        last_7_days = []
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            skin_count = SkinSensorData.query.filter(
                func.date(SkinSensorData.sensor_time) == date
            ).count()
            env_count = EnvironmentSensorData.query.filter(
                func.date(EnvironmentSensorData.sensor_time) == date
            ).count()
            last_7_days.append({
                'date': date.isoformat(),
                'skin_count': skin_count,
                'env_count': env_count
            })
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'devices': {
                    'total': total_devices,
                    'online': online_devices,
                    'offline': offline_devices,
                    'online_rate': round(online_devices / max(total_devices, 1) * 100, 2)
                },
                'users': {
                    'total': total_users,
                    'active': active_users,
                    'active_rate': round(active_users / max(total_users, 1) * 100, 2)
                },
                'today': {
                    'skin_records': today_skin_data,
                    'env_records': today_env_data,
                    'total_records': today_skin_data + today_env_data
                },
                'weekly_trend': last_7_days
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'查询失败: {str(e)}'}), 500


# =====================================================
# 设备管理接口
# =====================================================

@admin_bp.route('/devices', methods=['GET'])
def get_all_devices():
    """获取所有设备列表（管理员视角）"""
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
        
        devices = []
        for device in pagination.items:
            device_dict = device.to_dict()
            # 添加绑定用户信息
            bindings = DeviceBinding.query.filter_by(device_id=device.device_id).all()
            device_dict['bind_count'] = len(bindings)
            device_dict['bind_users'] = [b.user_id for b in bindings]
            devices.append(device_dict)
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'items': devices,
                'total': pagination.total,
                'page': page,
                'per_page': per_page,
                'pages': pagination.pages
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'查询失败: {str(e)}'}), 500


@admin_bp.route('/devices/<string:device_id>', methods=['PUT'])
def admin_update_device(device_id):
    """管理员更新设备信息"""
    try:
        device = Device.query.filter_by(device_id=device_id).first()
        if not device:
            return jsonify({'code': 404, 'message': '设备不存在'}), 404
        
        data = request.get_json()
        
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
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '设备更新成功',
            'data': device.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'更新失败: {str(e)}'}), 500


@admin_bp.route('/devices/<string:device_id>', methods=['DELETE'])
def admin_delete_device(device_id):
    """管理员删除设备"""
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
# 用户管理接口
# =====================================================

@admin_bp.route('/users', methods=['GET'])
def get_all_users():
    """获取所有用户列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        role = request.args.get('role', None)
        status = request.args.get('status', None)
        
        query = User.query
        
        if role:
            query = query.filter(User.role == role)
        if status:
            query = query.filter(User.status == status)
        
        pagination = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        users = []
        for user in pagination.items:
            user_dict = user.to_dict()
            # 添加设备绑定数量
            bind_count = DeviceBinding.query.filter_by(user_id=user.id, status='active').count()
            user_dict['device_count'] = bind_count
            users.append(user_dict)
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'items': users,
                'total': pagination.total,
                'page': page,
                'per_page': per_page,
                'pages': pagination.pages
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'查询失败: {str(e)}'}), 500


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
def admin_update_user(user_id):
    """管理员更新用户信息"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        data = request.get_json()
        
        if 'nickname' in data:
            user.nickname = data['nickname']
        if 'email' in data:
            user.email = data['email']
        if 'role' in data:
            user.role = data['role']
        if 'status' in data:
            user.status = data['status']
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '用户更新成功',
            'data': user.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'更新失败: {str(e)}'}), 500


# =====================================================
# 数据统计分析接口
# =====================================================

@admin_bp.route('/statistics/skin', methods=['GET'])
def get_skin_statistics():
    """获取皮肤数据统计分析"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = SkinSensorData.query
        
        if start_date:
            query = query.filter(SkinSensorData.sensor_time >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(SkinSensorData.sensor_time <= datetime.fromisoformat(end_date))
        
        # 计算平均值
        stats = query.with_entities(
            func.avg(SkinSensorData.moisture).label('avg_moisture'),
            func.avg(SkinSensorData.oiliness).label('avg_oiliness'),
            func.avg(SkinSensorData.temperature).label('avg_temperature'),
            func.count(SkinSensorData.id).label('total_count')
        ).first()
        
        # 按设备分组统计
        device_stats = db.session.query(
            SkinSensorData.device_id,
            func.count(SkinSensorData.id).label('count'),
            func.avg(SkinSensorData.moisture).label('avg_moisture'),
            func.avg(SkinSensorData.oiliness).label('avg_oiliness')
        ).group_by(SkinSensorData.device_id).all()
        
        device_stats_list = []
        for ds in device_stats:
            device = Device.query.filter_by(device_id=ds.device_id).first()
            device_stats_list.append({
                'device_id': ds.device_id,
                'device_name': device.device_type if device else 'Unknown',
                'count': ds.count,
                'avg_moisture': round(float(ds.avg_moisture), 2) if ds.avg_moisture else 0,
                'avg_oiliness': round(float(ds.avg_oiliness), 2) if ds.avg_oiliness else 0
            })
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'summary': {
                    'total_count': stats.total_count or 0,
                    'avg_moisture': round(float(stats.avg_moisture), 2) if stats.avg_moisture else 0,
                    'avg_oiliness': round(float(stats.avg_oiliness), 2) if stats.avg_oiliness else 0,
                    'avg_temperature': round(float(stats.avg_temperature), 2) if stats.avg_temperature else 0
                },
                'by_device': device_stats_list
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'查询失败: {str(e)}'}), 500


@admin_bp.route('/statistics/environment', methods=['GET'])
def get_environment_statistics():
    """获取环境数据统计分析"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = EnvironmentSensorData.query
        
        if start_date:
            query = query.filter(EnvironmentSensorData.sensor_time >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(EnvironmentSensorData.sensor_time <= datetime.fromisoformat(end_date))
        
        stats = query.with_entities(
            func.avg(EnvironmentSensorData.temperature).label('avg_temp'),
            func.avg(EnvironmentSensorData.humidity).label('avg_humidity'),
            func.avg(EnvironmentSensorData.pm25).label('avg_pm25'),
            func.avg(EnvironmentSensorData.co2).label('avg_co2'),
            func.count(EnvironmentSensorData.id).label('total_count')
        ).first()
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'total_count': stats.total_count or 0,
                'avg_temperature': round(float(stats.avg_temp), 2) if stats.avg_temp else 0,
                'avg_humidity': round(float(stats.avg_humidity), 2) if stats.avg_humidity else 0,
                'avg_pm25': round(float(stats.avg_pm25), 2) if stats.avg_pm25 else 0,
                'avg_co2': round(float(stats.avg_co2), 2) if stats.avg_co2 else 0
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'查询失败: {str(e)}'}), 500


@admin_bp.route('/statistics/monthly', methods=['GET'])
def get_monthly_statistics():
    """获取月度统计数据"""
    try:
        year = request.args.get('year', datetime.now().year, type=int)
        
        monthly_stats = db.session.query(
            extract('month', SkinSensorData.sensor_time).label('month'),
            func.count(SkinSensorData.id).label('skin_count'),
            func.avg(SkinSensorData.moisture).label('avg_moisture'),
            func.avg(SkinSensorData.oiliness).label('avg_oiliness')
        ).filter(extract('year', SkinSensorData.sensor_time) == year)\
         .group_by(extract('month', SkinSensorData.sensor_time))\
         .order_by('month').all()
        
        result = []
        for ms in monthly_stats:
            result.append({
                'month': int(ms.month),
                'skin_count': ms.skin_count,
                'avg_moisture': round(float(ms.avg_moisture), 2) if ms.avg_moisture else 0,
                'avg_oiliness': round(float(ms.avg_oiliness), 2) if ms.avg_oiliness else 0
            })
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'year': year,
                'monthly_data': result
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'查询失败: {str(e)}'}), 500


# =====================================================
# 设备地域分布接口
# =====================================================

@admin_bp.route('/devices/geo-distribution', methods=['GET'])
def get_device_geo_distribution():
    """获取设备地域分布"""
    try:
        geo_stats = db.session.query(
            Device.location,
            func.count(Device.id).label('count')
        ).filter(Device.location.isnot(None)).group_by(Device.location).all()
        
        distribution = []
        for gs in geo_stats:
            distribution.append({
                'location': gs.location,
                'count': gs.count
            })
        
        # 按数量排序
        distribution.sort(key=lambda x: x['count'], reverse=True)
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': distribution
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'查询失败: {str(e)}'}), 500


# =====================================================
# 实时数据接口
# =====================================================

@admin_bp.route('/realtime/skin', methods=['GET'])
def get_realtime_skin_data():
    """获取最新皮肤传感器数据"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        recent_data = SkinSensorData.query.order_by(SkinSensorData.sensor_time.desc()).limit(limit).all()
        
        result = []
        for data in recent_data:
            device = Device.query.filter_by(device_id=data.device_id).first()
            result.append({
                'id': data.id,
                'device_id': data.device_id,
                'device_type': device.device_type if device else 'Unknown',
                'moisture': data.moisture,
                'oiliness': data.oiliness,
                'temperature': data.temperature,
                'sensor_time': data.sensor_time.isoformat(),
                'received_at': data.received_at.isoformat() if data.received_at else None
            })
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': result
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'查询失败: {str(e)}'}), 500


@admin_bp.route('/realtime/environment', methods=['GET'])
def get_realtime_env_data():
    """获取最新环境传感器数据"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        recent_data = EnvironmentSensorData.query.order_by(EnvironmentSensorData.sensor_time.desc()).limit(limit).all()
        
        result = []
        for data in recent_data:
            device = Device.query.filter_by(device_id=data.device_id).first()
            result.append({
                'id': data.id,
                'device_id': data.device_id,
                'device_type': device.device_type if device else 'Unknown',
                'temperature': data.temperature,
                'humidity': data.humidity,
                'pm25': data.pm25,
                'co2': data.co2,
                'sensor_time': data.sensor_time.isoformat(),
                'received_at': data.received_at.isoformat() if data.received_at else None
            })
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': result
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'查询失败: {str(e)}'}), 500
