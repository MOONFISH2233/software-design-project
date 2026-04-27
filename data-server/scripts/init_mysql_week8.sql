-- =====================================================
-- 第八周数据库设计 - 完整建表脚本
-- 基于原有8个表扩展至15个表
-- MySQL 8.0+
-- =====================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS software_design 
    DEFAULT CHARACTER SET utf8mb4 
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE software_design;

-- =====================================================
-- 第一部分：原有表结构（第七周已完成）
-- =====================================================

-- 1. 设备信息表
CREATE TABLE IF NOT EXISTS devices (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    device_id VARCHAR(20) UNIQUE NOT NULL COMMENT '设备唯一标识',
    device_type VARCHAR(50) COMMENT '设备类型',
    firmware_version VARCHAR(20) COMMENT '固件版本',
    install_date DATE COMMENT '安装日期',
    location VARCHAR(100) COMMENT '安装位置',
    status VARCHAR(20) DEFAULT 'online' COMMENT '设备状态: online/offline/maintenance',
    battery_level INT COMMENT '电池电量(%)',
    signal_strength INT COMMENT '信号强度',
    last_heartbeat DATETIME COMMENT '最后心跳时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_device_id (device_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备信息表';

-- 2. 皮肤传感器数据表
CREATE TABLE IF NOT EXISTS skin_sensor_data (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    device_id VARCHAR(20) NOT NULL COMMENT '设备ID',
    moisture INT NOT NULL COMMENT '皮肤水分含量',
    oiliness INT NOT NULL COMMENT '皮肤油脂度',
    temperature FLOAT COMMENT '皮肤温度',
    sensor_time DATETIME NOT NULL COMMENT '传感器采集时间',
    received_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '服务器接收时间',
    client_ip VARCHAR(45) COMMENT '客户端IP地址',
    request_id VARCHAR(100) COMMENT '请求追踪ID',
    validated BOOLEAN DEFAULT TRUE COMMENT '是否通过验证',
    quality_score FLOAT COMMENT '数据质量评分',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    INDEX idx_device_id (device_id),
    INDEX idx_sensor_time (sensor_time),
    INDEX idx_received_at (received_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='皮肤传感器数据表';

-- 3. 环境传感器数据表
CREATE TABLE IF NOT EXISTS environment_sensor_data (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    device_id VARCHAR(20) NOT NULL COMMENT '设备ID',
    temperature FLOAT COMMENT '环境温度',
    humidity FLOAT COMMENT '环境湿度',
    pm25 INT COMMENT 'PM2.5浓度',
    co2 INT COMMENT 'CO2浓度',
    location VARCHAR(100) COMMENT '地理位置',
    latitude FLOAT COMMENT '纬度',
    longitude FLOAT COMMENT '经度',
    sensor_time DATETIME NOT NULL COMMENT '传感器采集时间',
    received_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '服务器接收时间',
    client_ip VARCHAR(45) COMMENT '客户端IP地址',
    request_id VARCHAR(100) COMMENT '请求追踪ID',
    validated BOOLEAN DEFAULT TRUE COMMENT '是否通过验证',
    quality_score FLOAT COMMENT '数据质量评分',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    INDEX idx_device_id (device_id),
    INDEX idx_sensor_time (sensor_time),
    INDEX idx_received_at (received_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='环境传感器数据表';

-- 4. 每日统计表
CREATE TABLE IF NOT EXISTS daily_statistics (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    stat_date DATE UNIQUE NOT NULL COMMENT '统计日期',
    total_records INT DEFAULT 0 COMMENT '总记录数',
    active_devices INT DEFAULT 0 COMMENT '活跃设备数',
    avg_moisture FLOAT COMMENT '平均水分含量',
    avg_oiliness FLOAT COMMENT '平均油脂度',
    avg_temperature FLOAT COMMENT '平均温度',
    avg_humidity FLOAT COMMENT '平均湿度',
    avg_pm25 FLOAT COMMENT '平均PM2.5',
    avg_co2 FLOAT COMMENT '平均CO2',
    max_records_device VARCHAR(20) COMMENT '记录最多的设备ID',
    min_records_device VARCHAR(20) COMMENT '记录最少的设备ID',
    calculated_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '计算时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_stat_date (stat_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='每日统计表';

-- 5. 用户基础表
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    nickname VARCHAR(50) COMMENT '昵称',
    phone VARCHAR(20) COMMENT '手机号',
    email VARCHAR(100) COMMENT '邮箱',
    avatar_url VARCHAR(255) COMMENT '头像URL',
    role VARCHAR(20) DEFAULT 'user' COMMENT '角色: admin/user',
    status VARCHAR(20) DEFAULT 'active' COMMENT '状态: active/inactive/banned',
    last_login DATETIME COMMENT '最后登录时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_username (username),
    INDEX idx_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户基础表';

-- =====================================================
-- 第二部分：新增表结构（第八周补充）
-- =====================================================

-- 6. 用户详细档案表
CREATE TABLE IF NOT EXISTS user_profiles (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    user_id INT NOT NULL COMMENT '用户ID',
    skin_type VARCHAR(20) COMMENT '肤质类型: dry/oily/mixed/sensitive',
    skincare_goals JSON COMMENT '护肤目标: ["moisturizing", "oil_control"]',
    age INT COMMENT '年龄',
    gender VARCHAR(10) COMMENT '性别: male/female/other',
    birthday DATE COMMENT '生日',
    height FLOAT COMMENT '身高(cm)',
    weight FLOAT COMMENT '体重(kg)',
    allergies TEXT COMMENT '过敏史',
    medical_conditions TEXT COMMENT '健康状况',
    register_date DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '注册日期',
    last_update DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_id (user_id),
    INDEX idx_skin_type (skin_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户详细档案表';

-- 7. 健康报告表
CREATE TABLE IF NOT EXISTS health_reports (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    user_id INT NOT NULL COMMENT '用户ID',
    report_type VARCHAR(20) NOT NULL COMMENT '报告类型: daily/weekly/monthly/yearly',
    report_date DATE NOT NULL COMMENT '报告日期',
    start_date DATE COMMENT '起始日期',
    end_date DATE COMMENT '结束日期',
    content_json JSON COMMENT '报告内容(JSON格式)',
    score FLOAT COMMENT '综合评分(0-100)',
    suggestions TEXT COMMENT '改善建议',
    is_generated BOOLEAN DEFAULT FALSE COMMENT '是否已生成',
    generated_at DATETIME COMMENT '生成时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_report_type (report_type),
    INDEX idx_report_date (report_date),
    UNIQUE KEY uk_user_report (user_id, report_type, report_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='健康报告表';

-- 8. 设备绑定关系表
CREATE TABLE IF NOT EXISTS device_bindings (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    user_id INT NOT NULL COMMENT '用户ID',
    device_id VARCHAR(20) NOT NULL COMMENT '设备ID',
    bind_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '绑定时间',
    is_primary BOOLEAN DEFAULT FALSE COMMENT '是否主要设备',
    status VARCHAR(20) DEFAULT 'active' COMMENT '状态: active/inactive/unbound',
    unbind_time DATETIME COMMENT '解绑时间',
    notes TEXT COMMENT '备注',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_device (user_id, device_id),
    INDEX idx_user_id (user_id),
    INDEX idx_device_id (device_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备绑定关系表';

-- 9. 社区帖子表
CREATE TABLE IF NOT EXISTS community_posts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    user_id INT NOT NULL COMMENT '发帖用户ID',
    title VARCHAR(200) NOT NULL COMMENT '帖子标题',
    content TEXT NOT NULL COMMENT '帖子内容',
    images_json JSON COMMENT '图片列表(JSON数组)',
    tags JSON COMMENT '标签列表',
    category VARCHAR(50) COMMENT '分类: experience/question/review/share',
    like_count INT DEFAULT 0 COMMENT '点赞数',
    comment_count INT DEFAULT 0 COMMENT '评论数',
    view_count INT DEFAULT 0 COMMENT '浏览数',
    share_count INT DEFAULT 0 COMMENT '分享数',
    is_top BOOLEAN DEFAULT FALSE COMMENT '是否置顶',
    is精华 BOOLEAN DEFAULT FALSE COMMENT '是否精华',
    status VARCHAR(20) DEFAULT 'published' COMMENT '状态: published/draft/deleted',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_category (category),
    INDEX idx_created_at (created_at),
    FULLTEXT INDEX ft_content (title, content)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='社区帖子表';

-- 10. 帖子评论表
CREATE TABLE IF NOT EXISTS post_comments (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    post_id BIGINT NOT NULL COMMENT '帖子ID',
    user_id INT NOT NULL COMMENT '评论用户ID',
    parent_comment_id BIGINT COMMENT '父评论ID(回复)',
    content TEXT NOT NULL COMMENT '评论内容',
    images_json JSON COMMENT '评论图片',
    like_count INT DEFAULT 0 COMMENT '点赞数',
    status VARCHAR(20) DEFAULT 'published' COMMENT '状态: published/deleted',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (post_id) REFERENCES community_posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_comment_id) REFERENCES post_comments(id) ON DELETE CASCADE,
    INDEX idx_post_id (post_id),
    INDEX idx_user_id (user_id),
    INDEX idx_parent_comment_id (parent_comment_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='帖子评论表';

-- 11. 消息通知表
CREATE TABLE IF NOT EXISTS notifications (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    user_id INT NOT NULL COMMENT '接收用户ID',
    type VARCHAR(20) NOT NULL COMMENT '通知类型: system/data/interaction/promotion',
    title VARCHAR(200) NOT NULL COMMENT '通知标题',
    content TEXT COMMENT '通知内容',
    related_id VARCHAR(100) COMMENT '关联ID(帖子ID/报告ID等)',
    related_type VARCHAR(50) COMMENT '关联类型: post/report/device',
    is_read BOOLEAN DEFAULT FALSE COMMENT '是否已读',
    read_at DATETIME COMMENT '阅读时间',
    action_url VARCHAR(255) COMMENT '跳转链接',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    expires_at DATETIME COMMENT '过期时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_type (type),
    INDEX idx_is_read (is_read),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='消息通知表';

-- 12. 用户积分表
CREATE TABLE IF NOT EXISTS user_points (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    user_id INT NOT NULL COMMENT '用户ID',
    total_points INT DEFAULT 0 COMMENT '总积分',
    available_points INT DEFAULT 0 COMMENT '可用积分',
    used_points INT DEFAULT 0 COMMENT '已用积分',
    expired_points INT DEFAULT 0 COMMENT '过期积分',
    level VARCHAR(20) DEFAULT 'bronze' COMMENT '等级: bronze/silver/gold/platinum',
    last_update DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_id (user_id),
    INDEX idx_level (level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户积分表';

-- 13. 护肤品数据库
CREATE TABLE IF NOT EXISTS skincare_products (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    name VARCHAR(100) NOT NULL COMMENT '产品名称',
    brand VARCHAR(50) COMMENT '品牌',
    category VARCHAR(50) COMMENT '分类: cleanser/toner/serum/moisturizer/sunscreen',
    ingredients JSON COMMENT '成分列表',
    suitable_skin_type JSON COMMENT '适用肤质',
    price DECIMAL(10, 2) COMMENT '价格',
    rating FLOAT COMMENT '评分(0-5)',
    review_count INT DEFAULT 0 COMMENT '评价数',
    description TEXT COMMENT '产品描述',
    image_url VARCHAR(255) COMMENT '产品图片',
    status VARCHAR(20) DEFAULT 'active' COMMENT '状态: active/inactive',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_brand (brand),
    INDEX idx_category (category),
    FULLTEXT INDEX ft_product (name, description)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='护肤品数据库';

-- 14. 用户护肤记录表
CREATE TABLE IF NOT EXISTS user_skincare_records (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    user_id INT NOT NULL COMMENT '用户ID',
    product_id INT COMMENT '产品ID',
    product_name VARCHAR(100) COMMENT '产品名称(手动输入)',
    usage_time DATETIME NOT NULL COMMENT '使用时间',
    usage_amount VARCHAR(50) COMMENT '使用量',
    skin_feel TEXT COMMENT '使用感受',
    effect_rating INT COMMENT '效果评分(1-5)',
    notes TEXT COMMENT '备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES skincare_products(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_usage_time (usage_time),
    INDEX idx_product_id (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户护肤记录表';

-- 15. 系统配置表
CREATE TABLE IF NOT EXISTS system_configs (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    config_key VARCHAR(100) UNIQUE NOT NULL COMMENT '配置键',
    config_value TEXT COMMENT '配置值',
    config_type VARCHAR(20) DEFAULT 'string' COMMENT '配置类型: string/int/float/boolean/json',
    description VARCHAR(255) COMMENT '配置说明',
    is_public BOOLEAN DEFAULT FALSE COMMENT '是否公开',
    updated_by INT COMMENT '更新人ID',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_config_key (config_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统配置表';

-- =====================================================
-- 初始化数据
-- =====================================================

-- 插入默认系统配置
INSERT INTO system_configs (config_key, config_value, config_type, description, is_public) VALUES
('app.name', '皮肤健康监测小程序', 'string', '应用名称', TRUE),
('app.version', '1.0.0', 'string', '应用版本', TRUE),
('data.retention_days', '365', 'int', '数据保留天数', FALSE),
('report.auto_generate', 'true', 'boolean', '是否自动生成报告', FALSE),
('notification.enabled', 'true', 'boolean', '是否启用通知', FALSE);

-- 插入示例护肤品数据
INSERT INTO skincare_products (name, brand, category, suitable_skin_type, price, rating, description) VALUES
('保湿精华液', '品牌A', 'serum', '["dry", "mixed"]', 299.00, 4.5, '深层补水，改善干燥'),
('控油洁面乳', '品牌B', 'cleanser', '["oily", "mixed"]', 89.00, 4.2, '温和清洁，控制油脂'),
('防晒乳液SPF50', '品牌C', 'sunscreen', '["dry", "oily", "mixed", "sensitive"]', 159.00, 4.7, '高效防晒，清爽不油腻');

-- =====================================================
-- 视图和存储过程
-- =====================================================

-- 创建用户数据统计视图
CREATE OR REPLACE VIEW vw_user_statistics AS
SELECT 
    u.id AS user_id,
    u.username,
    u.nickname,
    COUNT(DISTINCT db.device_id) AS bound_devices,
    COUNT(DISTINCT hr.id) AS total_reports,
    up.total_points,
    up.level
FROM users u
LEFT JOIN device_bindings db ON u.id = db.user_id AND db.status = 'active'
LEFT JOIN health_reports hr ON u.id = hr.user_id
LEFT JOIN user_points up ON u.id = up.user_id
GROUP BY u.id;

-- 创建设备数据汇总视图
CREATE OR REPLACE VIEW vw_device_summary AS
SELECT 
    d.device_id,
    d.device_type,
    d.status,
    COUNT(DISTINCT db.user_id) AS bound_users,
    MAX(ssd.sensor_time) AS last_skin_data_time,
    MAX(esd.sensor_time) AS last_env_data_time,
    COUNT(ssd.id) AS total_skin_records,
    COUNT(esd.id) AS total_env_records
FROM devices d
LEFT JOIN device_bindings db ON d.device_id = db.device_id AND db.status = 'active'
LEFT JOIN skin_sensor_data ssd ON d.device_id = ssd.device_id
LEFT JOIN environment_sensor_data esd ON d.device_id = esd.device_id
GROUP BY d.device_id;

-- =====================================================
-- 完成提示
-- =====================================================
SELECT '✅ 数据库创建完成！共15个表，包含视图和初始数据。' AS message;
