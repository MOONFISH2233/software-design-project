#!/usr/bin/env python3
"""修复 app.py 中的加密解密函数"""

import sys

def fix_app_py(filepath):
    """修复 app.py 文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 找到需要修复的位置
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # 修复 encrypt_data 函数
        if '@app.route(\'/api/encrypt\'' in line:
            # 保留装饰器
            new_lines.append(line)
            i += 1
            new_lines.append(lines[i])  # @limiter.limit
            i += 1
            new_lines.append(lines[i])  # def encrypt_data():
            i += 1
            
            # 添加完整的函数体
            new_lines.append('    """数据加密接口"""\n')
            new_lines.append('    try:\n')
            new_lines.append('        data = request.get_json()\n')
            new_lines.append('        if not data:\n')
            new_lines.append("            return jsonify({'error': '缺少数据'}), 400\n")
            new_lines.append('        \n')
            new_lines.append('        encrypted = security_manager.encrypt_data(json.dumps(data))\n')
            new_lines.append('        return jsonify({\n')
            new_lines.append("            'status': 'success',\n")
            new_lines.append("            'encrypted_data': encrypted,\n")
            new_lines.append("            'timestamp': datetime.now().isoformat()\n")
            new_lines.append('        })\n')
            new_lines.append('    except Exception as e:\n')
            new_lines.append('        logger.error(f"加密失败：{e}")\n')
            new_lines.append("        return jsonify({'error': str(e)}), 500\n")
            new_lines.append('\n')
            
        # 修复 decrypt_data 函数
        elif '@app.route(\'/api/decrypt\'' in line:
            # 保留装饰器
            new_lines.append(line)
            i += 1
            new_lines.append(lines[i])  # @limiter.limit
            i += 1
            new_lines.append(lines[i])  # def decrypt_data():
            i += 1
            
            # 添加完整的函数体
            new_lines.append('    """数据解密接口"""\n')
            new_lines.append('    try:\n')
            new_lines.append('        data = request.get_json()\n')
            new_lines.append("        if not data or 'encrypted_data' not in data:\n")
            new_lines.append("            return jsonify({'error': '缺少 encrypted_data 参数'}), 400\n")
            new_lines.append('        \n')
            new_lines.append("        decrypted = security_manager.decrypt_data(data['encrypted_data'])\n")
            new_lines.append('        return jsonify({\n')
            new_lines.append("            'status': 'success',\n")
            new_lines.append("            'decrypted_data': json.loads(decrypted),\n")
            new_lines.append("            'timestamp': datetime.now().isoformat()\n")
            new_lines.append('        })\n')
            new_lines.append('    except Exception as e:\n')
            new_lines.append('        logger.error(f"解密失败：{e}")\n')
            new_lines.append("        return jsonify({'error': str(e)}), 500\n")
            new_lines.append('\n')
        else:
            new_lines.append(line)
            i += 1
    
    # 写回文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"✅ 已修复 {filepath}")

if __name__ == '__main__':
    filepath = sys.argv[1] if len(sys.argv) > 1 else 'app.py'
    fix_app_py(filepath)
