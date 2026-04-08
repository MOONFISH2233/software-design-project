"""
云端到云端数据传输
实现不同云服务器之间的数据同步
"""

import requests
import json
from datetime import datetime

class CloudToCloudTransfer:
    def __init__(self, source_server, target_server):
        """
        初始化云端传输器
        :param source_server: 源服务器地址
        :param target_server: 目标服务器地址
        """
        self.source_server = source_server
        self.target_server = target_server
        self.transfer_log = []
    
    def fetch_data_from_source(self, endpoint='/api/logs'):
        """
        从源服务器获取数据
        :param endpoint: API 端点
        :return: 获取的数据
        """
        try:
            response = requests.get(
                f'{self.source_server}{endpoint}',
                timeout=30
            )
            return response.json()
        except Exception as e:
            print(f"从源服务器获取数据失败：{str(e)}")
            return None
    
    def push_data_to_target(self, data, description=""):
        """
        推送数据到目标服务器
        :param data: 要推送的数据
        :param description: 数据描述
        :return: 推送结果
        """
        try:
            payload = {
                'data': data,
                'description': description,
                'source': f'cloud_sync_{self.source_server}',
                'sync_time': datetime.now().isoformat()
            }
            
            response = requests.post(
                f'{self.target_server}/api/receive',
                json=payload,
                timeout=30
            )
            return response.json()
        except Exception as e:
            print(f"推送到目标服务器失败：{str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def sync(self, endpoint='/api/logs', description="云端同步数据"):
        """
        执行同步：从源服务器获取数据并推送到目标服务器
        :param endpoint: 源服务器 API 端点
        :param description: 同步描述
        :return: 同步结果
        """
        print(f"开始同步：{self.source_server} -> {self.target_server}")
        
        # 1. 从源服务器获取数据
        source_data = self.fetch_data_from_source(endpoint)
        if not source_data:
            return {'status': 'error', 'message': '源服务器数据获取失败'}
        
        # 2. 推送到目标服务器
        result = self.push_data_to_target(source_data, description)
        
        # 3. 记录同步日志
        self.transfer_log.append({
            'time': datetime.now().isoformat(),
            'source': self.source_server,
            'target': self.target_server,
            'endpoint': endpoint,
            'status': result.get('status', 'unknown'),
            'filename': result.get('filename', 'unknown')
        })
        
        if result.get('status') == 'success':
            print(f"✓ 同步成功：{result.get('filename')}")
        else:
            print(f" 同步失败：{result.get('message', '未知错误')}")
        
        return result
    
    def get_transfer_history(self):
        """获取传输历史"""
        return self.transfer_log


# 使用示例
if __name__ == '__main__':
    # 示例：从服务器 A 同步到服务器 B
    # 请根据实际情况修改服务器地址
    transfer = CloudToCloudTransfer(
        source_server='http://47.103.108.47:5000',
        target_server='http://47.103.108.47:5000'  # 可以改为另一个服务器地址
    )
    
    # 执行同步
    result = transfer.sync('/api/logs', "日志数据同步")
    print("同步结果:", result)
    
    # 查看传输历史
    print("\n传输历史:")
    for record in transfer.get_transfer_history():
        print(f"  {record['time']}")
        print(f"  {record['source']} -> {record['target']}")
        print(f"  状态：{record['status']}, 文件：{record['filename']}\n")
