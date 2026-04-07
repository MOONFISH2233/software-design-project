"""
安全增强模块 - 从 harbeat-full-dev 项目借鉴的最佳实践
功能：提供更安全的密码哈希、Token验证等安全功能
版本：v1.0
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional
import jwt
import json
import os


class EnhancedSecurityManager:
    """增强版安全管理器"""
    
    def __init__(self, security_dir: str = "security"):
        self.security_dir = security_dir
        self.users_file = os.path.join(security_dir, "users_enhanced.json")
        self._init_users_file()
    
    def _init_users_file(self):
        """初始化用户文件"""
        if not os.path.exists(self.users_file):
            # 创建默认用户（带盐值）
            default_users = {
                "admin": {
                    "password_hash": self._hash_password_with_salt("admin123"),
                    "salt": self._get_last_salt(),
                    "role": "admin",
                    "created_at": datetime.now().isoformat()
                },
                "user1": {
                    "password_hash": self._hash_password_with_salt("user123"),
                    "salt": self._get_last_salt(),
                    "role": "user",
                    "created_at": datetime.now().isoformat()
                },
                "user2": {
                    "password_hash": self._hash_password_with_salt("user123"),
                    "salt": self._get_last_salt(),
                    "role": "user",
                    "created_at": datetime.now().isoformat()
                },
                "user3": {
                    "password_hash": self._hash_password_with_salt("user123"),
                    "salt": self._get_last_salt(),
                    "role": "user",
                    "created_at": datetime.now().isoformat()
                }
            }
            self._save_users(default_users)
    
    def _hash_password_with_salt(self, password: str, salt: str = None) -> str:
        """
        加盐密码哈希（借鉴 harbeat 项目）
        优势：防止彩虹表攻击，相同密码不同盐值产生不同哈希
        """
        if salt is None:
            salt = secrets.token_hex(16)  # 生成16字节随机盐值
        
        # 盐值 + 密码组合后哈希
        salted_password = f"{salt}:{password}"
        password_hash = hashlib.sha256(salted_password.encode()).hexdigest()
        
        return password_hash
    
    def _get_last_salt(self) -> str:
        """获取最后生成的盐值（用于演示）"""
        return secrets.token_hex(16)
    
    def verify_password_with_salt(self, password: str, stored_hash: str, salt: str) -> bool:
        """验证加盐密码"""
        computed_hash = self._hash_password_with_salt(password, salt)
        return computed_hash == stored_hash
    
    def authenticate_enhanced(self, username: str, password: str, secret_key: str, expiration_hours: int = 24) -> Optional[str]:
        """
        增强版用户认证（使用加盐哈希）
        返回 JWT Token
        """
        users = self._load_users()
        
        if username not in users:
            return None
        
        user = users[username]
        
        # 使用盐值验证密码
        if not self.verify_password_with_salt(password, user['password_hash'], user['salt']):
            return None
        
        # 生成 JWT Token
        token = jwt.encode({
            'username': username,
            'role': user['role'],
            'exp': datetime.now() + timedelta(hours=expiration_hours),
            'iat': datetime.now()  # 签发时间
        }, secret_key, algorithm='HS256')
        
        # 将 bytes 解码为字符串
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        
        print(f"✅ 用户 {username} 认证成功（加盐哈希）")
        return token
    
    def register_user(self, username: str, password: str, role: str = "user") -> bool:
        """
        注册新用户（使用加盐哈希）
        """
        users = self._load_users()
        
        if username in users:
            print(f"❌ 用户 {username} 已存在")
            return False
        
        # 生成盐值并哈希密码
        salt = secrets.token_hex(16)
        password_hash = self._hash_password_with_salt(password, salt)
        
        users[username] = {
            'password_hash': password_hash,
            'salt': salt,
            'role': role,
            'created_at': datetime.now().isoformat()
        }
        
        self._save_users(users)
        print(f"✅ 用户 {username} 注册成功")
        return True
    
    def _load_users(self) -> Dict:
        """加载用户数据"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_users(self, users: Dict):
        """保存用户数据"""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
    
    def list_users_safe(self) -> Dict:
        """安全地列出用户（不显示密码哈希和盐值）"""
        users = self._load_users()
        safe_users = {
            username: {
                'role': info['role'],
                'created_at': info['created_at']
            }
            for username, info in users.items()
        }
        return safe_users


# 使用示例
if __name__ == "__main__":
    print("=" * 60)
    print("增强版安全管理器 - 使用示例")
    print("=" * 60)
    
    # 创建安全管理器
    security = EnhancedSecurityManager()
    
    # 注册新用户
    print("\n[1] 注册新用户:")
    security.register_user("testuser", "testpass123", "user")
    
    # 用户认证
    print("\n[2] 用户认证:")
    secret_key = secrets.token_hex(32)
    token = security.authenticate_enhanced("testuser", "testpass123", secret_key)
    
    if token:
        print(f"Token: {token[:50]}...")
        
        # 验证 Token
        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            print(f"Token 验证成功: {payload}")
        except jwt.ExpiredSignatureError:
            print("❌ Token 已过期")
        except jwt.InvalidTokenError:
            print("❌ Token 无效")
    
    # 列出用户
    print("\n[3] 用户列表（安全模式）:")
    users = security.list_users_safe()
    for username, info in users.items():
        print(f"  {username} - {info['role']} - 创建时间: {info['created_at']}")
    
    print("\n" + "=" * 60)
    print("增强功能说明:")
    print("  ✅ 密码加盐哈希 - 防止彩虹表攻击")
    print("  ✅ 每个用户独立盐值 - 相同密码不同哈希")
    print("  ✅ JWT Token 带签发时间 - 便于审计")
    print("  ✅ 安全的用户列表 - 不暴露敏感信息")
    print("=" * 60)
