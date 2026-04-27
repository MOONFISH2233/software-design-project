"""
MySQL数据库模型定义
使用SQLAlchemy ORM进行数据库操作
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

# =====================================================
# 1. 设备信息模型
# =====================================================
class Device(db.Model):
    __tablename__ = 'devices'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    device_id = db.Column(db.String(20), unique=True, nullable=False, comment='设备唯一标识')
    device_type = db.Column(db.String(50), comment='设备类型')
    firmware_version = db.Column(db.String(20), comment='固件版本')
    install_date = db.Column(db.Date, comment='安装日期')
    location = db.Column(db.String(100), comment='安装位置')
    status = db.Column(db.String(20), default='online', comment='设备状态')
    battery_level = db.Column(db.Integer, comment='电池电量(%)')
    signal_strength = db.Column(db.Integer, comment='信号强度')
    last_heartbeat = db.Column(db.DateTime, comment='最后心跳时间')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'device_type': self.device_type,
            'firmware_version': self.firmware_version,
            'install_date': self.install_date.isoformat() if self.install_date else None,
            'location': self.location,
            'status': self.status,
            'battery_level': self.battery_level,
            'signal_strength': self.signal_strength,
            'last_heartbeat': self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# =====================================================
# 2. 皮肤传感器数据模型
# =====================================================
class SkinSensorData(db.Model):
    __tablename__ = 'skin_sensor_data'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, comment='主键ID')
    device_id = db.Column(db.String(20), nullable=False, comment='设备ID')
    moisture = db.Column(db.Integer, nullable=False, comment='皮肤水分含量')
    oiliness = db.Column(db.Integer, nullable=False, comment='皮肤油脂度')
    temperature = db.Column(db.Float, comment='皮肤温度')
    sensor_time = db.Column(db.DateTime, nullable=False, comment='传感器采集时间')
    received_at = db.Column(db.DateTime, default=datetime.now, comment='服务器接收时间')
    client_ip = db.Column(db.String(45), comment='客户端IP地址')
    request_id = db.Column(db.String(100), comment='请求追踪ID')
    validated = db.Column(db.Boolean, default=True, comment='是否通过验证')
    quality_score = db.Column(db.Float, comment='数据质量评分')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='记录创建时间')
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'moisture': self.moisture,
            'oiliness': self.oiliness,
            'temperature': self.temperature,
            'sensor_time': self.sensor_time.isoformat() if self.sensor_time else None,
            'received_at': self.received_at.isoformat() if self.received_at else None,
            'client_ip': self.client_ip,
            'request_id': self.request_id,
            'validated': self.validated,
            'quality_score': self.quality_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# =====================================================
# 3. 环境传感器数据模型
# =====================================================
class EnvironmentSensorData(db.Model):
    __tablename__ = 'environment_sensor_data'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, comment='主键ID')
    device_id = db.Column(db.String(20), nullable=False, comment='设备ID')
    temperature = db.Column(db.Float, comment='环境温度')
    humidity = db.Column(db.Float, comment='环境湿度')
    pm25 = db.Column(db.Integer, comment='PM2.5浓度')
    co2 = db.Column(db.Integer, comment='CO2浓度')
    location = db.Column(db.String(100), comment='地理位置')
    latitude = db.Column(db.Float, comment='纬度')
    longitude = db.Column(db.Float, comment='经度')
    sensor_time = db.Column(db.DateTime, nullable=False, comment='传感器采集时间')
    received_at = db.Column(db.DateTime, default=datetime.now, comment='服务器接收时间')
    client_ip = db.Column(db.String(45), comment='客户端IP地址')
    request_id = db.Column(db.String(100), comment='请求追踪ID')
    validated = db.Column(db.Boolean, default=True, comment='是否通过验证')
    quality_score = db.Column(db.Float, comment='数据质量评分')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='记录创建时间')
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'pm25': self.pm25,
            'co2': self.co2,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'sensor_time': self.sensor_time.isoformat() if self.sensor_time else None,
            'received_at': self.received_at.isoformat() if self.received_at else None,
            'client_ip': self.client_ip,
            'request_id': self.request_id,
            'validated': self.validated,
            'quality_score': self.quality_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# =====================================================
# 4. 每日统计模型
# =====================================================
class DailyStatistics(db.Model):
    __tablename__ = 'daily_statistics'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    stat_date = db.Column(db.Date, unique=True, nullable=False, comment='统计日期')
    total_records = db.Column(db.Integer, default=0, comment='总记录数')
    active_devices = db.Column(db.Integer, default=0, comment='活跃设备数')
    avg_moisture = db.Column(db.Float, comment='平均水分含量')
    avg_oiliness = db.Column(db.Float, comment='平均油脂度')
    avg_temperature = db.Column(db.Float, comment='平均温度')
    avg_humidity = db.Column(db.Float, comment='平均湿度')
    avg_pm25 = db.Column(db.Float, comment='平均PM2.5')
    avg_co2 = db.Column(db.Float, comment='平均CO2')
    max_records_device = db.Column(db.String(20), comment='记录最多的设备ID')
    min_records_device = db.Column(db.String(20), comment='记录最少的设备ID')
    calculated_at = db.Column(db.DateTime, default=datetime.now, comment='计算时间')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    
    def to_dict(self):
        return {
            'id': self.id,
            'stat_date': self.stat_date.isoformat() if self.stat_date else None,
            'total_records': self.total_records,
            'active_devices': self.active_devices,
            'avg_moisture': self.avg_moisture,
            'avg_oiliness': self.avg_oiliness,
            'avg_temperature': self.avg_temperature,
            'avg_humidity': self.avg_humidity,
            'avg_pm25': self.avg_pm25,
            'avg_co2': self.avg_co2,
            'max_records_device': self.max_records_device,
            'min_records_device': self.min_records_device,
            'calculated_at': self.calculated_at.isoformat() if self.calculated_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# =====================================================
# 5. 用户模型
# =====================================================
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    username = db.Column(db.String(50), unique=True, nullable=False, comment='用户名')
    password_hash = db.Column(db.String(255), nullable=False, comment='密码哈希')
    nickname = db.Column(db.String(50), comment='昵称')
    phone = db.Column(db.String(20), comment='手机号')
    email = db.Column(db.String(100), comment='邮箱')
    avatar_url = db.Column(db.String(255), comment='头像URL')
    role = db.Column(db.String(20), default='user', comment='角色')
    status = db.Column(db.String(20), default='active', comment='状态')
    last_login = db.Column(db.DateTime, comment='最后登录时间')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname,
            'phone': self.phone,
            'email': self.email,
            'avatar_url': self.avatar_url,
            'role': self.role,
            'status': self.status,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# =====================================================
# 6. 用户详细档案模型
# =====================================================
class UserProfile(db.Model):
    __tablename__ = 'user_profiles'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True, comment='用户ID')
    skin_type = db.Column(db.String(20), comment='肤质类型')
    skincare_goals = db.Column(db.JSON, comment='护肤目标')
    age = db.Column(db.Integer, comment='年龄')
    gender = db.Column(db.String(10), comment='性别')
    birthday = db.Column(db.Date, comment='生日')
    height = db.Column(db.Float, comment='身高(cm)')
    weight = db.Column(db.Float, comment='体重(kg)')
    allergies = db.Column(db.Text, comment='过敏史')
    medical_conditions = db.Column(db.Text, comment='健康状况')
    register_date = db.Column(db.DateTime, default=datetime.now, comment='注册日期')
    last_update = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='最后更新时间')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'skin_type': self.skin_type,
            'skincare_goals': self.skincare_goals,
            'age': self.age,
            'gender': self.gender,
            'birthday': self.birthday.isoformat() if self.birthday else None,
            'height': self.height,
            'weight': self.weight,
            'allergies': self.allergies,
            'medical_conditions': self.medical_conditions
        }


# =====================================================
# 7. 健康报告模型
# =====================================================
class HealthReport(db.Model):
    __tablename__ = 'health_reports'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, comment='主键ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    report_type = db.Column(db.String(20), nullable=False, comment='报告类型')
    report_date = db.Column(db.Date, nullable=False, comment='报告日期')
    start_date = db.Column(db.Date, comment='起始日期')
    end_date = db.Column(db.Date, comment='结束日期')
    content_json = db.Column(db.JSON, comment='报告内容')
    score = db.Column(db.Float, comment='综合评分')
    suggestions = db.Column(db.Text, comment='改善建议')
    is_generated = db.Column(db.Boolean, default=False, comment='是否已生成')
    generated_at = db.Column(db.DateTime, comment='生成时间')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'report_type': self.report_type,
            'report_date': self.report_date.isoformat() if self.report_date else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'content_json': self.content_json,
            'score': self.score,
            'suggestions': self.suggestions,
            'is_generated': self.is_generated,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None
        }


# =====================================================
# 8. 设备绑定关系模型
# =====================================================
class DeviceBinding(db.Model):
    __tablename__ = 'device_bindings'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    device_id = db.Column(db.String(20), db.ForeignKey('devices.device_id'), nullable=False, comment='设备ID')
    bind_time = db.Column(db.DateTime, default=datetime.now, comment='绑定时间')
    is_primary = db.Column(db.Boolean, default=False, comment='是否主要设备')
    status = db.Column(db.String(20), default='active', comment='状态')
    unbind_time = db.Column(db.DateTime, comment='解绑时间')
    notes = db.Column(db.Text, comment='备注')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'device_id': self.device_id,
            'bind_time': self.bind_time.isoformat() if self.bind_time else None,
            'is_primary': self.is_primary,
            'status': self.status,
            'unbind_time': self.unbind_time.isoformat() if self.unbind_time else None,
            'notes': self.notes
        }


# =====================================================
# 9. 社区帖子模型
# =====================================================
class CommunityPost(db.Model):
    __tablename__ = 'community_posts'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, comment='主键ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='发帖用户ID')
    title = db.Column(db.String(200), nullable=False, comment='帖子标题')
    content = db.Column(db.Text, nullable=False, comment='帖子内容')
    images_json = db.Column(db.JSON, comment='图片列表')
    tags = db.Column(db.JSON, comment='标签列表')
    category = db.Column(db.String(50), comment='分类')
    like_count = db.Column(db.Integer, default=0, comment='点赞数')
    comment_count = db.Column(db.Integer, default=0, comment='评论数')
    view_count = db.Column(db.Integer, default=0, comment='浏览数')
    share_count = db.Column(db.Integer, default=0, comment='分享数')
    is_top = db.Column(db.Boolean, default=False, comment='是否置顶')
    is_essence = db.Column(db.Boolean, default=False, comment='是否精华')
    status = db.Column(db.String(20), default='published', comment='状态')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'images_json': self.images_json,
            'tags': self.tags,
            'category': self.category,
            'like_count': self.like_count,
            'comment_count': self.comment_count,
            'view_count': self.view_count,
            'share_count': self.share_count,
            'is_top': self.is_top,
            'is_essence': self.is_essence,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# =====================================================
# 10. 帖子评论模型
# =====================================================
class PostComment(db.Model):
    __tablename__ = 'post_comments'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, comment='主键ID')
    post_id = db.Column(db.BigInteger, db.ForeignKey('community_posts.id'), nullable=False, comment='帖子ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='评论用户ID')
    parent_comment_id = db.Column(db.BigInteger, db.ForeignKey('post_comments.id'), comment='父评论ID')
    content = db.Column(db.Text, nullable=False, comment='评论内容')
    images_json = db.Column(db.JSON, comment='评论图片')
    like_count = db.Column(db.Integer, default=0, comment='点赞数')
    status = db.Column(db.String(20), default='published', comment='状态')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    def to_dict(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'user_id': self.user_id,
            'parent_comment_id': self.parent_comment_id,
            'content': self.content,
            'images_json': self.images_json,
            'like_count': self.like_count,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# =====================================================
# 11. 消息通知模型
# =====================================================
class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, comment='主键ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='接收用户ID')
    type = db.Column(db.String(20), nullable=False, comment='通知类型')
    title = db.Column(db.String(200), nullable=False, comment='通知标题')
    content = db.Column(db.Text, comment='通知内容')
    related_id = db.Column(db.String(100), comment='关联ID')
    related_type = db.Column(db.String(50), comment='关联类型')
    is_read = db.Column(db.Boolean, default=False, comment='是否已读')
    read_at = db.Column(db.DateTime, comment='阅读时间')
    action_url = db.Column(db.String(255), comment='跳转链接')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    expires_at = db.Column(db.DateTime, comment='过期时间')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'title': self.title,
            'content': self.content,
            'related_id': self.related_id,
            'related_type': self.related_type,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'action_url': self.action_url,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# =====================================================
# 12. 用户积分模型
# =====================================================
class UserPoints(db.Model):
    __tablename__ = 'user_points'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True, comment='用户ID')
    total_points = db.Column(db.Integer, default=0, comment='总积分')
    available_points = db.Column(db.Integer, default=0, comment='可用积分')
    used_points = db.Column(db.Integer, default=0, comment='已用积分')
    expired_points = db.Column(db.Integer, default=0, comment='过期积分')
    level = db.Column(db.String(20), default='bronze', comment='等级')
    last_update = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='最后更新时间')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_points': self.total_points,
            'available_points': self.available_points,
            'used_points': self.used_points,
            'expired_points': self.expired_points,
            'level': self.level
        }


# =====================================================
# 13. 护肤品数据库模型
# =====================================================
class SkincareProduct(db.Model):
    __tablename__ = 'skincare_products'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    name = db.Column(db.String(100), nullable=False, comment='产品名称')
    brand = db.Column(db.String(50), comment='品牌')
    category = db.Column(db.String(50), comment='分类')
    ingredients = db.Column(db.JSON, comment='成分列表')
    suitable_skin_type = db.Column(db.JSON, comment='适用肤质')
    price = db.Column(db.Numeric(10, 2), comment='价格')
    rating = db.Column(db.Float, comment='评分')
    review_count = db.Column(db.Integer, default=0, comment='评价数')
    description = db.Column(db.Text, comment='产品描述')
    image_url = db.Column(db.String(255), comment='产品图片')
    status = db.Column(db.String(20), default='active', comment='状态')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'brand': self.brand,
            'category': self.category,
            'ingredients': self.ingredients,
            'suitable_skin_type': self.suitable_skin_type,
            'price': float(self.price) if self.price else None,
            'rating': self.rating,
            'review_count': self.review_count,
            'description': self.description,
            'image_url': self.image_url,
            'status': self.status
        }


# =====================================================
# 14. 用户护肤记录模型
# =====================================================
class UserSkincareRecord(db.Model):
    __tablename__ = 'user_skincare_records'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, comment='主键ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    product_id = db.Column(db.Integer, db.ForeignKey('skincare_products.id'), comment='产品ID')
    product_name = db.Column(db.String(100), comment='产品名称')
    usage_time = db.Column(db.DateTime, nullable=False, comment='使用时间')
    usage_amount = db.Column(db.String(50), comment='使用量')
    skin_feel = db.Column(db.Text, comment='使用感受')
    effect_rating = db.Column(db.Integer, comment='效果评分')
    notes = db.Column(db.Text, comment='备注')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'usage_time': self.usage_time.isoformat() if self.usage_time else None,
            'usage_amount': self.usage_amount,
            'skin_feel': self.skin_feel,
            'effect_rating': self.effect_rating,
            'notes': self.notes
        }


# =====================================================
# 15. 系统配置模型
# =====================================================
class SystemConfig(db.Model):
    __tablename__ = 'system_configs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    config_key = db.Column(db.String(100), unique=True, nullable=False, comment='配置键')
    config_value = db.Column(db.Text, comment='配置值')
    config_type = db.Column(db.String(20), default='string', comment='配置类型')
    description = db.Column(db.String(255), comment='配置说明')
    is_public = db.Column(db.Boolean, default=False, comment='是否公开')
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), comment='更新人ID')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    def to_dict(self):
        return {
            'id': self.id,
            'config_key': self.config_key,
            'config_value': self.config_value,
            'config_type': self.config_type,
            'description': self.description,
            'is_public': self.is_public,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
