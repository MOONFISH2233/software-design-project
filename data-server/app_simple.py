#!/usr/bin/env python3
"""
简化版Flask应用 - 第八周验收专用
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify
from models import db

# 创建Flask应用
app = Flask(__name__, static_folder='static', static_url_path='/static')

# ==================== MySQL数据库配置 ====================
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin@localhost/software_design?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True
}

# 初始化数据库
db.init_app(app)
print('✅ 数据库扩展已初始化')

# ==================== 注册路由 ====================
try:
    from routes.mysql_routes import mysql_bp
    app.register_blueprint(mysql_bp)
    print("✅ MySQL路由已注册: /api/mysql/*")
except Exception as e:
    print(f"❌ MySQL路由注册失败: {e}")
    import traceback
    traceback.print_exc()

try:
    from routes.miniprogram_routes import miniprogram_bp
    app.register_blueprint(miniprogram_bp)
    print("✅ 小程序路由已注册: /api/miniprogram/*")
except Exception as e:
    print(f"⚠️  小程序路由注册失败: {e}")

# ==================== 健康检查接口 ====================

@app.route('/')
def index():
    """前端首页"""
    from flask import send_from_directory
    return send_from_directory('static', 'index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'database': 'connected',
        'version': '1.0.0',
        'service': 'Skin Health Monitoring System'
    })

# ==================== 启动服务 ====================
if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Flask服务器启动中...")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False)
