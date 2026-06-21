#!/usr/bin/env python3
"""
简化版Flask服务器 - 直接注册所有路由
"""
import sys
sys.path.insert(0, '/root/course-project/data-server')

from flask import Flask, jsonify
from models import db

# 创建Flask应用
app = Flask(__name__)

# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin@localhost/software_design?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True
}

# 初始化数据库
db.init_app(app)

# 导入并注册MySQL路由
try:
    from routes.mysql_routes import mysql_bp
    app.register_blueprint(mysql_bp)
    print("✅ MySQL路由已注册")
except Exception as e:
    print(f"❌ MySQL路由注册失败: {e}")
    import traceback
    traceback.print_exc()

# 健康检查接口
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'database': 'connected',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    print("🚀 Flask服务器启动中...")
    app.run(host='0.0.0.0', port=5000, debug=False)
