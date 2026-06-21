"""
路由注册模块 - 将所有Blueprint注册到Flask应用
"""
import sys
import os

# 确保当前目录在Python路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from routes.mysql_routes import mysql_bp
    from routes.miniprogram_routes import miniprogram_bp
    
    def register_all_blueprints(app):
        """注册所有Blueprint"""
        # MySQL数据接口（第八周任务）
        app.register_blueprint(mysql_bp)
        
        # 小程序接口
        app.register_blueprint(miniprogram_bp)
        
        print("✅ 所有路由已注册")
        print(f"   - MySQL接口: {mysql_bp.url_prefix or '/'}/*")
        print(f"   - 小程序接口: {miniprogram_bp.url_prefix or '/'}/*")
        
except Exception as e:
    print(f"❌ 路由注册模块加载失败: {e}")
    import traceback
    traceback.print_exc()
    
    def register_all_blueprints(app):
        print("⚠️  路由注册跳过（模块加载失败）")
