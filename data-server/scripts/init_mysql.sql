-- =====================================================
-- 传感器数据服务器 - MySQL数据库初始化脚本
-- 版本: V1.0
-- 日期: 2026-04-25
-- 说明: 从MongoDB集合设计转换为MySQL表结构
-- =====================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS sensor_project 
DEFAULT CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE sensor_project;

-- =====================================================
-- 1. 设备信息表 (devices)
-- 对应MongoDB: device_status集合的设备基础信息
-- =====================================================
DROP TABLE IF EXISTS devices;
CREATE TABLE devices (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    device_id VARCHAR(20) NOT NULL UNIQUE COMMENT '设备唯一标识',
    device_type VARCHAR(50) DEFAULT NULL COMMENT '设备类型',
    firmware_version VARCHAR(20) DEFAULT NULL COMMENT '固件版本',
    install_date DATE DEFAULT NULL COMMENT '安装日期',
    location VARCHAR(100) DEFAULT NULL COMMENT '安装位置',
    status VARCHAR(20) DEFAULT 'online' COMMENT '设备状态: online/offline/maintenance',
    battery_level INT DEFAULT NULL COMMENT '电池电量(%)',
    signal_strength INT DEFAULT NULL COMMENT '信号强度',
    last_heartbeat DATETIME DEFAULT NULL COMMENT '最后心跳时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_device_id (device_id),
    INDEX idx_status (status),
    INDEX idx_last_heartbeat (last_heartbeat)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备信息表';

-- =====================================================
-- 2. 皮肤传感器数据表 (skin_sensor_data)
-- 对应MongoDB: skin_sensor集合
-- =====================================================
DROP TABLE IF EXISTS skin_sensor_data;
CREATE TABLE skin_sensor_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    device_id VARCHAR(20) NOT NULL COMMENT '设备ID',
    moisture INT NOT NULL COMMENT '皮肤水分含量(0-100%)',
    oiliness INT NOT NULL COMMENT '皮肤油脂度(0-100%)',
    temperature DOUBLE DEFAULT NULL COMMENT '皮肤温度(℃)',
    sensor_time DATETIME NOT NULL COMMENT '传感器采集时间',
    received_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '服务器接收时间',
    client_ip VARCHAR(45) DEFAULT NULL COMMENT '客户端IP地址',
    request_id VARCHAR(100) DEFAULT NULL COMMENT '请求追踪ID',
    validated BOOLEAN DEFAULT TRUE COMMENT '是否通过验证',
    quality_score DOUBLE DEFAULT NULL COMMENT '数据质量评分(0-1)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    
    INDEX idx_device_id (device_id),
    INDEX idx_sensor_time (sensor_time),
    INDEX idx_received_at (received_at),
    INDEX idx_device_time (device_id, sensor_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='皮肤传感器数据表';

-- =====================================================
-- 3. 环境传感器数据表 (environment_sensor_data)
-- 对应MongoDB: environment_sensor集合
-- =====================================================
DROP TABLE IF EXISTS environment_sensor_data;
CREATE TABLE environment_sensor_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    device_id VARCHAR(20) NOT NULL COMMENT '设备ID',
    temperature DOUBLE DEFAULT NULL COMMENT '环境温度(℃)',
    humidity DOUBLE DEFAULT NULL COMMENT '环境湿度(%)',
    pm25 INT DEFAULT NULL COMMENT 'PM2.5浓度(μg/m³)',
    co2 INT DEFAULT NULL COMMENT 'CO2浓度(ppm)',
    location VARCHAR(100) DEFAULT NULL COMMENT '地理位置',
    latitude DOUBLE DEFAULT NULL COMMENT '纬度',
    longitude DOUBLE DEFAULT NULL COMMENT '经度',
    sensor_time DATETIME NOT NULL COMMENT '传感器采集时间',
    received_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '服务器接收时间',
    client_ip VARCHAR(45) DEFAULT NULL COMMENT '客户端IP地址',
    request_id VARCHAR(100) DEFAULT NULL COMMENT '请求追踪ID',
    validated BOOLEAN DEFAULT TRUE COMMENT '是否通过验证',
    quality_score DOUBLE DEFAULT NULL COMMENT '数据质量评分(0-1)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    
    INDEX idx_device_id (device_id),
    INDEX idx_sensor_time (sensor_time),
    INDEX idx_location (location),
    INDEX idx_lat_lng (latitude, longitude),
    INDEX idx_device_time (device_id, sensor_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='环境传感器数据表';

-- =====================================================
-- 4. 设备状态历史表 (device_status_history)
-- 对应MongoDB: device_status集合的状态历史记录
-- =====================================================
DROP TABLE IF EXISTS device_status_history;
CREATE TABLE device_status_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    device_id VARCHAR(20) NOT NULL COMMENT '设备ID',
    status VARCHAR(20) NOT NULL COMMENT '设备状态',
    battery_level INT DEFAULT NULL COMMENT '电池电量(%)',
    signal_strength INT DEFAULT NULL COMMENT '信号强度',
    firmware_version VARCHAR(20) DEFAULT NULL COMMENT '固件版本',
    last_heartbeat DATETIME NOT NULL COMMENT '心跳时间',
    error_code VARCHAR(50) DEFAULT NULL COMMENT '错误代码',
    error_message TEXT DEFAULT NULL COMMENT '错误信息',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    
    INDEX idx_device_id (device_id),
    INDEX idx_status (status),
    INDEX idx_heartbeat (last_heartbeat),
    INDEX idx_device_heartbeat (device_id, last_heartbeat)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备状态历史表';

-- =====================================================
-- 5. 每日统计表 (daily_statistics)
-- 用于存储定时任务计算的统计数据
-- =====================================================
DROP TABLE IF EXISTS daily_statistics;
CREATE TABLE daily_statistics (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    stat_date DATE NOT NULL UNIQUE COMMENT '统计日期',
    total_records INT DEFAULT 0 COMMENT '总记录数',
    active_devices INT DEFAULT 0 COMMENT '活跃设备数',
    avg_moisture DOUBLE DEFAULT NULL COMMENT '平均水分含量',
    avg_oiliness DOUBLE DEFAULT NULL COMMENT '平均油脂度',
    avg_temperature DOUBLE DEFAULT NULL COMMENT '平均温度',
    avg_humidity DOUBLE DEFAULT NULL COMMENT '平均湿度',
    avg_pm25 DOUBLE DEFAULT NULL COMMENT '平均PM2.5',
    avg_co2 DOUBLE DEFAULT NULL COMMENT '平均CO2',
    max_records_device VARCHAR(20) DEFAULT NULL COMMENT '记录最多的设备ID',
    min_records_device VARCHAR(20) DEFAULT NULL COMMENT '记录最少的设备ID',
    calculated_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '计算时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    INDEX idx_stat_date (stat_date),
    INDEX idx_calculated_at (calculated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='每日统计表';

-- =====================================================
-- 6. 用户表 (users) - 小程序用户管理
-- =====================================================
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    nickname VARCHAR(50) DEFAULT NULL COMMENT '昵称',
    phone VARCHAR(20) DEFAULT NULL COMMENT '手机号',
    email VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
    avatar_url VARCHAR(255) DEFAULT NULL COMMENT '头像URL',
    role VARCHAR(20) DEFAULT 'user' COMMENT '角色: admin/user',
    status VARCHAR(20) DEFAULT 'active' COMMENT '状态: active/inactive',
    last_login DATETIME DEFAULT NULL COMMENT '最后登录时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_username (username),
    INDEX idx_phone (phone),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- =====================================================
-- 7. 设备绑定表 (user_device_bindings) - 用户与设备的关联
-- =====================================================
DROP TABLE IF EXISTS user_device_bindings;
CREATE TABLE user_device_bindings (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    user_id INT NOT NULL COMMENT '用户ID',
    device_id VARCHAR(20) NOT NULL COMMENT '设备ID',
    binding_type VARCHAR(20) DEFAULT 'owner' COMMENT '绑定类型: owner/viewer',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '绑定时间',
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_device (user_id, device_id),
    INDEX idx_device_id (device_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户设备绑定表';

-- =====================================================
-- 8. 告警记录表 (alerts) - 异常数据告警
-- =====================================================
DROP TABLE IF EXISTS alerts;
CREATE TABLE alerts (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    device_id VARCHAR(20) NOT NULL COMMENT '设备ID',
    alert_type VARCHAR(50) NOT NULL COMMENT '告警类型',
    alert_level VARCHAR(20) DEFAULT 'warning' COMMENT '告警级别: info/warning/error/critical',
    alert_message TEXT NOT NULL COMMENT '告警消息',
    threshold_value DOUBLE DEFAULT NULL COMMENT '阈值',
    actual_value DOUBLE DEFAULT NULL COMMENT '实际值',
    is_read BOOLEAN DEFAULT FALSE COMMENT '是否已读',
    handled_by INT DEFAULT NULL COMMENT '处理人ID',
    handled_at DATETIME DEFAULT NULL COMMENT '处理时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '告警时间',
    
    FOREIGN KEY (handled_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_device_id (device_id),
    INDEX idx_alert_type (alert_type),
    INDEX idx_created_at (created_at),
    INDEX idx_is_read (is_read)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='告警记录表';

-- =====================================================
-- 插入测试数据
-- =====================================================

-- 插入测试设备
INSERT INTO devices (device_id, device_type, firmware_version, install_date, location, status) VALUES
('DEV_001', 'skin_sensor', 'v1.0.0', '2026-01-15', '北京市朝阳区', 'online'),
('DEV_002', 'environment_sensor', 'v1.0.0', '2026-01-20', '上海市浦东新区', 'online'),
('DEV_003', 'skin_sensor', 'v1.1.0', '2026-02-10', '广州市天河区', 'offline');

-- 插入测试用户
INSERT INTO users (username, password_hash, nickname, role) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYILp92S.0i', '管理员', 'admin'),
('user1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYILp92S.0i', '张三', 'user');

-- 插入用户设备绑定
INSERT INTO user_device_bindings (user_id, device_id, binding_type) VALUES
(1, 'DEV_001', 'owner'),
(1, 'DEV_002', 'owner'),
(2, 'DEV_001', 'viewer');

-- =====================================================
-- 完成提示
-- =====================================================
SELECT '✅ 数据库初始化完成!' AS message;
SELECT COUNT(*) AS device_count FROM devices;
SELECT COUNT(*) AS user_count FROM users;
SELECT COUNT(*) AS table_count FROM information_schema.tables WHERE table_schema = 'sensor_project';
