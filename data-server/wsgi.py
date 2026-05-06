"""
Gunicorn启动脚本 - 注册所有蓝图
"""
from app import app, db

# ==================== 立即注册小程序API蓝图 ====================
from routes.miniprogram_routes import miniprogram_bp
app.register_blueprint(miniprogram_bp)
print("✅ 小程序API蓝图已注册")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
