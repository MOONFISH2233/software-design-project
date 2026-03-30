"""
本地到云端数据传输客户端
"""

import requests
import json
import os
from datetime import datetime

class DataUploader:
    def __init__(self, server_url):
        """
        初始化上传器
        :param server_url: 云端服务器地址，如 http://47.103.108.47:5000
        """
        self.server_url = server_url
        self.upload_log = []
    
    def upload_data(self, data, description=""):
        """
        上传数据到云端
        :param data: 要上传的数据（字典）
        :param description: 数据描述
        :return: 上传结果
        """
        try:
            # 添加元数据
            payload = {
                'data': data,
                'description': description,
                'source': 'local',
                'upload_time': datetime.now().isoformat()
            }
            
            # 发送 POST 请求
            response = requests.post(
                f'{self.server_url}/api/receive',
                json=payload,
                timeout=30
            )
            
            result = response.json()
            
            # 记录上传日志
            self.upload_log.append({
                'time': datetime.now().isoformat(),
                'status': result.get('status', 'unknown'),
                'filename': result.get('filename', 'unknown'),
                'description': description
            })
            
            print(f"✓ 上传成功：{result.get('filename')}")
            return result
        
        except Exception as e:
            print(f"✗ 上传失败：{str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def upload_file(self, filepath, description=""):
        """
        上传本地文件到云端
        :param filepath: 本地文件路径
        :param description: 文件描述
        :return: 上传结果
        """
        try:
            # 读取文件
            with open(filepath, 'r', encoding='utf-8') as f:
                if filepath.endswith('.json'):
                    data = json.load(f)
                else:
                    data = {'content': f.read()}
            
            # 添加文件信息
            data['filename'] = os.path.basename(filepath)
            data['filepath'] = filepath
            
            return self.upload_data(data, description)
        
        except Exception as e:
            print(f" 文件上传失败：{str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def health_check(self):
        """检查服务器状态"""
        try:
            response = requests.get(f'{self.server_url}/api/health', timeout=10)
            return response.json()
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_upload_history(self):
        """获取上传历史"""
        return self.upload_log


# 使用示例
if __name__ == '__main__':
    # 初始化上传器（替换为你的服务器地址）
    uploader = DataUploader('http://47.103.108.47:5000')
    
    # 检查服务器状态
    print("服务器状态:", uploader.health_check())
    
    # 示例 1: 上传字典数据
    sample_data = {
        'temperature': 25.5,
        'humidity': 60,
        'location': '实验室',
        'device_id': 'sensor_001'
    }
    uploader.upload_data(sample_data, "环境传感器数据")
    
    # 示例 2: 上传文件
    # uploader.upload_file('local_data.json', "本地数据文件")
    
    # 查看上传历史
    print("\n上传历史:")
    for record in uploader.get_upload_history():
        print(f"  {record['time']} - {record['status']} - {record['filename']}")
