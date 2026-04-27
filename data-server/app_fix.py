# ==================== 加密解密接口 ====================

@app.route('/api/encrypt', methods=['POST'])
@limiter.limit("20 per minute")
def encrypt_data():
    """数据加密接口"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '缺少数据'}), 400
        
        encrypted = security_manager.encrypt_data(json.dumps(data))
        return jsonify({
            'status': 'success',
            'encrypted_data': encrypted,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"加密失败：{e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/decrypt', methods=['POST'])
@limiter.limit("10 per minute")
def decrypt_data():
    """数据解密接口"""
    try:
        data = request.get_json()
        if not data or 'encrypted_data' not in data:
            return jsonify({'error': '缺少 encrypted_data 参数'}), 400
        
        decrypted = security_manager.decrypt_data(data['encrypted_data'])
        return jsonify({
            'status': 'success',
            'decrypted_data': json.loads(decrypted),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"解密失败：{e}")
        return jsonify({'error': str(e)}), 500


# ==================== 认证接口 ====================

@app.route('/api/auth/login', methods=['POST'])
