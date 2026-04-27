"""
简化版数据生成模拟器 - HTTP直连版本
功能：
1. 生成传感器数据
2. 直接通过HTTP POST发送到服务器
3. 无需Redis消息队列
4. 适合快速测试和演示
"""

import requests
import json
import time
import random
from datetime import datetime, timedelta


class SimpleSimulator:
    """简化版模拟器 - 直接HTTP发送"""
    
    def __init__(self, server_url='http://47.103.108.47:5000'):
        self.server_url = server_url
        self.device_id = f"SIM_DEV_{random.randint(100, 999)}"
        self.count = 0
        
    def generate_skin_data(self):
        """生成皮肤传感器数据"""
        data = {
            "device_id": self.device_id,
            "sensor_type": "skin",
            "data": {
                "moisture": round(random.uniform(50, 80), 1),
                "oiliness": round(random.uniform(20, 50), 1),
                "temperature": round(random.uniform(35.0, 38.0), 1)
            },
            "timestamp": datetime.utcnow().isoformat(),
            "quality_score": round(random.uniform(0.8, 1.0), 2)
        }
        return data
    
    def send_data(self, data):
        """发送数据到服务器"""
        try:
            url = f"{self.server_url}/api/receive"
            response = requests.post(
                url,
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if response.status_code == 200:
                self.count += 1
                print(f"✅ [{self.count}] 发送成功 | 水分:{data['data']['moisture']}% | 油分:{data['data']['oiliness']}%")
                return True
            else:
                print(f"❌ 发送失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 连接错误: {str(e)}")
            return False
    
    def run(self, interval=2, max_count=None):
        """运行模拟器"""
        print("="*60)
        print("  简化版数据模拟器 - HTTP直连")
        print("="*60)
        print(f"📍 服务器: {self.server_url}")
        print(f"🆔 设备ID: {self.device_id}")
        print(f"⏱️  发送间隔: {interval}秒")
        print(f"📊 按 Ctrl+C 停止\n")
        
        try:
            while True:
                if max_count and self.count >= max_count:
                    print(f"\n✅ 已发送 {max_count} 条数据，完成！")
                    break
                
                data = self.generate_skin_data()
                self.send_data(data)
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print(f"\n\n⏹️  模拟器已停止")
            print(f"📊 总计发送: {self.count} 条数据")


def main():
    """主函数"""
    simulator = SimpleSimulator(server_url='http://47.103.108.47:5000')
    simulator.run(interval=2)  # 每2秒发送一次


if __name__ == '__main__':
    main()
