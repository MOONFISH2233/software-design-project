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

# 创建蓝图
miniprogram_bp = Blueprint('miniprogram', __name__, url_prefix='/api/miniprogram')

# 配置日志
logger = logging.getLogger(__name__)

# JWT密钥（应从配置文件读取）
JWT_SECRET_KEY = 'your-secret-key-change-in-production'


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
            password_hash=data['password'],  # 实际应使用bcrypt加密
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
        data = request.get_json()
        
        if 'username' not in data or 'password' not in data:
            return jsonify({'success': False, 'message': '缺少用户名或密码'}), 400
        
        # 查找用户
        user = User.query.filter_by(username=data['username']).first()
        
        if not user:
            return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
        
        # 验证密码（实际应使用bcrypt.check_password_hash）
        if user.password_hash != data['password']:
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
                'role': user.role
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

@miniprogram_bp.route('/device/bind', methods=['POST'])
@token_required
def bind_device(current_user):
    """绑定设备"""
    try:
        data = request.get_json()
        
        if 'device_id' not in data:
            return jsonify({'success': False, 'message': '缺少设备ID'}), 400
        
        device_id = data['device_id']
        
        # 检查设备是否存在
        device = Device.query.filter_by(device_id=device_id).first()
        if not device:
            return jsonify({'success': False, 'message': '设备不存在'}), 404
        
        # 检查是否已绑定
        from models import DeviceBinding
        existing_binding = DeviceBinding.query.filter_by(
            user_id=current_user.id,
            device_id=device_id
        ).first()
        
        if existing_binding:
            return jsonify({'success': False, 'message': '设备已绑定'}), 409
        
        # 创建绑定关系
        new_binding = DeviceBinding(
            user_id=current_user.id,
            device_id=device_id,
            is_primary=data.get('is_primary', False),
            status='active'
        )
        
        db.session.add(new_binding)
        db.session.commit()
        
        logger.info(f"设备绑定成功: 用户{current_user.username}, 设备{device_id}")
        
        return jsonify({
            'success': True,
            'message': '设备绑定成功'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"设备绑定失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


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
    """查询统计数据"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        days = request.args.get('days', type=int)  # 支持days参数
        
        query = DailyStatistics.query
        
        if start_date:
            query = query.filter(DailyStatistics.stat_date >= datetime.fromisoformat(start_date).date())
        
        if end_date:
            query = query.filter(DailyStatistics.stat_date <= datetime.fromisoformat(end_date).date())
        
        # 如果指定了days，计算起始日期
        if days and not start_date:
            from datetime import timedelta
            start = (datetime.now() - timedelta(days=days)).date()
            query = query.filter(DailyStatistics.stat_date >= start)
        
        # 按日期倒序排列
        query = query.order_by(DailyStatistics.stat_date.desc())
        
        statistics = [item.to_dict() for item in query.all()]
        
        return jsonify({
            'success': True,
            'statistics': statistics,
            'total': len(statistics)
        }), 200
        
    except Exception as e:
        logger.error(f"查询统计数据失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


# =====================================================
# 健康报告接口
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
# 注册蓝图
# =====================================================
def init_app(app):
    """初始化小程序路由"""
    app.register_blueprint(miniprogram_bp)
    logger.info("✅ 小程序路由注册成功")
