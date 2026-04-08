# 性能优化指南

## 📊 压力测试结果分析

### 预期性能指标

基于 v2.0 的优化，在普通服务器上（4 核 CPU, 8GB 内存）的预期表现：

| 接口 | 并发数 | QPS | 平均响应时间 | P95 | 成功率 |
|------|--------|-----|-------------|-----|--------|
| `/api/health` | 30 | 800-1200 | <20ms | <50ms | 99.9% |
| `/api/receive` | 50 | 500-800 | <50ms | <150ms | 99.5% |

---

## 🔧 进一步优化建议

### 1. **数据库持久化** (重要)

当前使用文件系统存储，高并发下存在瓶颈：

```python
# 建议使用 Redis 或 SQLite 替代文件存储
import redis

# Redis 连接池
redis_pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    db=0,
    max_connections=100
)

@app.route('/api/receive', methods=['POST'])
def receive_data_redis():
    """使用 Redis 存储数据"""
    data = request.get_json()
    key = f"data:{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
    # 异步写入 Redis（比文件快 10-100 倍）
    r = redis.Redis(connection_pool=redis_pool)
    r.setex(key, 86400, json.dumps(data))  # 24 小时过期
    
    return jsonify({'status': 'success', 'key': key})
```

**性能提升**: 10-100x

---

### 2. **批量处理优化**

对于非实时要求高的场景，使用批量处理：

```python
from collections import deque
import threading

class BatchProcessor:
    def __init__(self, batch_size=100, flush_interval=5):
        self.queue = deque()
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.lock = threading.Lock()
        
        # 定时刷新线程
        threading.Thread(target=self._auto_flush, daemon=True).start()
    
    def add(self, item):
        with self.lock:
            self.queue.append(item)
            if len(self.queue) >= self.batch_size:
                self._flush()
    
    def _flush(self):
        """批量处理"""
        batch = list(self.queue)
        self.queue.clear()
        # 批量写入数据库/文件
        print(f"批量处理 {len(batch)} 条数据")
    
    def _auto_flush(self):
        while True:
            time.sleep(self.flush_interval)
            with self.lock:
                if self.queue:
                    self._flush()

# 使用示例
batch_processor = BatchProcessor(batch_size=100)

@app.route('/api/receive', methods=['POST'])
def receive_batch():
    data = request.get_json()
    batch_processor.add(data)  # 加入队列，立即返回
    return jsonify({'status': 'queued'})
```

**性能提升**: 5-10x

---

### 3. **缓存层优化**

使用缓存减少重复计算：

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def compute_data_hash(data_str):
    """计算数据哈希（带缓存）"""
    return hashlib.md5(data_str.encode()).hexdigest()
```

---

### 4. **连接池优化**

如果使用数据库：

```python
# SQLAlchemy 连接池配置
from sqlalchemy import create_engine

engine = create_engine(
    'mysql+pymysql://user:pass@localhost/db',
    pool_size=50,          # 连接池大小
    max_overflow=100,      # 最大溢出连接数
    pool_timeout=30,       # 获取连接超时
    pool_recycle=3600,     # 连接回收时间
    echo=False             # 关闭 SQL 日志
)
```

---

### 5. **Gunicorn 生产配置**

创建 `gunicorn_config.py`:

```python
import multiprocessing

# 工作进程数（CPU 核心数 * 2 + 1）
workers = multiprocessing.cpu_count() * 2 + 1

# 每个进程的线程数
threads = 4

# 绑定地址
bind = "0.0.0.0:5000"

# 工作模式：gevent 支持更高并发
worker_class = 'gevent'

# 单个工作进程的最大连接数
worker_connections = 1000

# 请求超时时间
timeout = 30

# 保持连接超时
keepalive = 5

# 每个工作进程处理的最大请求数（防止内存泄漏）
max_requests = 1000
max_requests_jitter = 50

# 访问日志
accesslog = 'logs/gunicorn_access.log'
errorlog = 'logs/gunicorn_error.log'
loglevel = 'info'

# 进程命名
proc_name = 'flask-data-server'

# 启动前加载应用
preload_app = True

# Worker 重启钩子
def on_exit(server):
    print("Gunicorn 主进程退出")
```

运行：
```bash
gunicorn -c gunicorn_config.py app:app
```

**性能提升**: 相比 Flask 内置服务器 5-10x

---

### 6. **监控和告警**

添加 Prometheus 监控：

```python
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)

# 自定义指标
request_counter = metrics.Counter(
    'api_requests_total',
    'Total API requests',
    ['endpoint', 'status']
)

@app.route('/api/receive', methods=['POST'])
@metrics.counter('receive_requests', 'Receive endpoint requests')
def receive_data():
    # ... 业务逻辑
    pass
```

配合 Grafana 仪表盘实时监控。

---

### 7. **异步 IO 优化**

使用 aiohttp 替代 Flask（终极方案）：

```python
from aiohttp import web
import asyncio
import aiofiles

async def handle_receive(request):
    data = await request.json()
    
    # 异步文件写入
    async with aiofiles.open(filepath, 'w') as f:
        await f.write(json.dumps(data))
    
    return web.json_response({'status': 'success'})

app = web.Application()
app.router.add_post('/api/receive', handle_receive)

if __name__ == '__main__':
    web.run_app(app, port=5000)
```

**性能提升**: 2-5x（相比 Flask）

---

## 📈 性能对比表

| 优化方案 | 实施难度 | 性能提升 | 推荐度 |
|---------|---------|---------|--------|
| 当前版本 (v2.0) | ⭐ | 基准 | ⭐⭐⭐ |
| + Redis 存储 | ⭐⭐ | 10-100x | ⭐⭐⭐⭐⭐ |
| + 批量处理 | ⭐⭐ | 5-10x | ⭐⭐⭐⭐ |
| + Gunicorn | ⭐ | 5-10x | ⭐⭐⭐⭐⭐ |
| + 连接池 | ⭐⭐ | 2-5x | ⭐⭐⭐⭐ |
| 完整优化 | ⭐⭐⭐⭐ | 50-500x | ⭐⭐⭐⭐⭐ |

---

## 🎯 最佳实践建议

### 开发环境
```bash
# 使用 Flask 内置服务器即可
python app.py
```

### 测试环境
```bash
# 使用 Gunicorn
gunicorn -w 2 -b 0.0.0.0:5000 --threads=2 app:app
```

### 生产环境（中小规模）
```bash
# Gunicorn + 多进程
gunicorn -c gunicorn_config.py app:app
```

### 生产环境（大规模）
```bash
# Docker + Kubernetes + Redis + 监控
# 参考 docker-compose.yml 配置
```

---

## 🔍 性能瓶颈诊断

使用以下工具进行性能分析：

### 1. Python Profiler
```bash
python -m cProfile -o profile.stats app.py
snakeviz profile.stats  # 可视化分析
```

### 2. 内存分析
```python
from memory_profiler import profile

@profile
def receive_data():
    # ... 函数实现
    pass
```

### 3. 实时日志监控
```bash
# 查看错误日志
tail -f logs/error_*.log

# 分析慢请求
grep "慢请求" logs/server_*.log | awk '{print $NF}'
```

---

## 💡 常见问题 FAQ

### Q1: 日志队列满了会怎样？
A: DEBUG/INFO 级别会被丢弃，ERROR/CRITICAL 会等待，不会丢失重要日志。

### Q2: 采样率设置多少合适？
A: 
- 开发环境：1.0 (100%)
- 测试环境：0.5 (50%)
- 生产环境：0.1 (10%)
- 超高并发：0.01 (1%)

### Q3: 如何调优 Gunicorn 参数？
A: 根据 CPU 核心数和内存调整：
- workers = CPU 核心数 * 2 + 1
- threads = 4-8
- 监控内存使用，避免 OOM

### Q4: 文件存储的极限是多少？
A: 取决于磁盘 I/O：
- HDD: ~100-200 QPS
- SSD: ~500-1000 QPS
- NVMe: ~2000+ QPS

---

## 📚 参考资料

- [Flask 官方文档](https://flask.palletsprojects.com/)
- [Gunicorn 配置指南](https://docs.gunicorn.org/)
- [Prometheus 监控](https://prometheus.io/)
- [Redis 最佳实践](https://redis.io/topics/best-practices)
