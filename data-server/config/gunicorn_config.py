"""
Gunicorn 生产级配置文件
用于高并发、高性能部署 Flask 应用
"""

import multiprocessing
import os

# ==================== 服务器绑定 ====================
# 绑定地址和端口
bind = "0.0.0.0:5000"

# ==================== Worker 配置 ====================
# Worker 数量：推荐 (2 * CPU核心数) + 1
workers = multiprocessing.cpu_count() * 2 + 1

# Worker 类型：gevent 支持异步 I/O，适合 I/O 密集型应用
worker_class = "gevent"

# 每个 worker 的线程数（仅在使用 gthread 时有效）
threads = 2

# Worker 最大请求数后重启（防止内存泄漏）
max_requests = 1000
max_requests_jitter = 50  # 随机抖动，避免所有 worker 同时重启

# ==================== 超时配置 ====================
# Worker 超时时间（秒）
timeout = 120

# Keep-Alive 超时时间
keepalive = 5

# ==================== 日志配置 ====================
# 访问日志
accesslog = "/root/course-project/week5/data-server/logs/gunicorn_access.log"

# 错误日志
errorlog = "/root/course-project/week5/data-server/logs/gunicorn_error.log"

# 日志级别
loglevel = "info"

# 访问日志格式
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# ==================== 进程管理 ====================
# PID 文件
pidfile = "/root/course-project/week5/data-server/gunicorn.pid"

# 守护进程模式（后台运行）
daemon = False  # 使用 systemd 或 nohup 管理，不启用 daemon

# ==================== 性能优化 ====================
# 预加载应用（节省内存，加快启动）
preload_app = True

# TCP 队列长度（ backlog ）
backlog = 2048

# ==================== 安全配置 ====================
# 限制请求行大小
limit_request_line = 4096

# 限制请求头字段数量
limit_request_fields = 100

# 限制请求头字段大小
limit_request_field_size = 8190

# ==================== 钩子函数 ====================

def on_starting(server):
    """服务器启动时的回调"""
    print("=" * 60)
    print("🚀 Gunicorn 服务器正在启动...")
    print(f"   Worker 数量: {server.cfg.workers}")
    print(f"   Worker 类型: {server.cfg.worker_class_str}")
    print(f"   绑定地址: {server.cfg.bind[0]}")
    print("=" * 60)

def when_ready(server):
    """服务器就绪后的回调"""
    print("✅ Gunicorn 服务器已就绪，开始接受请求")

def worker_int(worker):
    """Worker 被中断时的回调"""
    print(f"⚠️  Worker {worker.pid} 被中断")

def worker_abort(worker):
    """Worker 异常终止时的回调"""
    print(f"❌ Worker {worker.pid} 异常终止")
