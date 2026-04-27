"""
每日统计数据定时任务
每天凌晨2点自动计算前一天的统计数据并写入MySQL
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from pymongo import MongoClient
import pymysql
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/daily_statistics.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('daily_statistics')


class DailyStatisticsTask:
    """每日统计数据定时任务类"""
    
    def __init__(self):
        # MongoDB连接
        self.mongo_client = MongoClient('mongodb://localhost:27017/')
        self.mongo_db = self.mongo_client['sensor_data']
        
        # MySQL连接
        self.mysql_conn = pymysql.connect(
            host='localhost',
            user='root',
            password='admin',
            database='sensor_project',
            charset='utf8mb4'
        )
        self.mysql_cursor = self.mysql_conn.cursor()
        
        logger.info("✅ 定时任务初始化完成")
    
    def calculate_daily_statistics(self, target_date=None):
        """
        计算指定日期的统计数据
        
        Args:
            target_date: 目标日期，默认为昨天
        """
        if target_date is None:
            target_date = (datetime.now() - timedelta(days=1)).date()
        
        logger.info(f"开始计算 {target_date} 的统计数据...")
        
        try:
            # 从MongoDB读取数据
            start_time = datetime.combine(target_date, datetime.min.time())
            end_time = datetime.combine(target_date, datetime.max.time())
            
            # 1. 统计总记录数
            skin_count = self.mongo_db.skin_sensor.count_documents({
                'timestamp': {'$gte': start_time, '$lte': end_time}
            })
            env_count = self.mongo_db.environment_sensor.count_documents({
                'timestamp': {'$gte': start_time, '$lte': end_time}
            })
            total_records = skin_count + env_count
            
            logger.info(f"总记录数: {total_records} (皮肤: {skin_count}, 环境: {env_count})")
            
            # 2. 统计活跃设备数
            skin_devices = self.mongo_db.skin_sensor.distinct('device_id', {
                'timestamp': {'$gte': start_time, '$lte': end_time}
            })
            env_devices = self.mongo_db.environment_sensor.distinct('device_id', {
                'timestamp': {'$gte': start_time, '$lte': end_time}
            })
            active_devices = len(set(skin_devices + env_devices))
            
            logger.info(f"活跃设备数: {active_devices}")
            
            # 3. 计算平均值
            skin_pipeline = [
                {'$match': {'timestamp': {'$gte': start_time, '$lte': end_time}}},
                {'$group': {
                    '_id': None,
                    'avg_moisture': {'$avg': '$moisture'},
                    'avg_oiliness': {'$avg': '$oiliness'},
                    'avg_temperature': {'$avg': '$temperature'}
                }}
            ]
            skin_stats = list(self.mongo_db.skin_sensor.aggregate(skin_pipeline))
            
            env_pipeline = [
                {'$match': {'timestamp': {'$gte': start_time, '$lte': end_time}}},
                {'$group': {
                    '_id': None,
                    'avg_temperature': {'$avg': '$temperature'},
                    'avg_humidity': {'$avg': '$humidity'},
                    'avg_pm25': {'$avg': '$pm25'},
                    'avg_co2': {'$avg': '$co2'}
                }}
            ]
            env_stats = list(self.mongo_db.environment_sensor.aggregate(env_pipeline))
            
            # 提取统计数据
            avg_moisture = skin_stats[0]['avg_moisture'] if skin_stats else None
            avg_oiliness = skin_stats[0]['avg_oiliness'] if skin_stats else None
            avg_skin_temp = skin_stats[0]['avg_temperature'] if skin_stats else None
            avg_env_temp = env_stats[0]['avg_temperature'] if env_stats else None
            avg_humidity = env_stats[0]['avg_humidity'] if env_stats else None
            avg_pm25 = env_stats[0]['avg_pm25'] if env_stats else None
            avg_co2 = env_stats[0]['avg_co2'] if env_stats else None
            
            # 综合温度（皮肤和环境平均）
            temps = [t for t in [avg_skin_temp, avg_env_temp] if t is not None]
            avg_temperature = sum(temps) / len(temps) if temps else None
            
            logger.info(f"平均水分: {avg_moisture}, 平均油脂度: {avg_oiliness}")
            logger.info(f"平均温度: {avg_temperature}, 平均湿度: {avg_humidity}")
            
            # 4. 查找记录最多和最少的设备
            device_counts = {}
            for device_id in set(skin_devices + env_devices):
                count = self.mongo_db.skin_sensor.count_documents({
                    'device_id': device_id,
                    'timestamp': {'$gte': start_time, '$lte': end_time}
                })
                count += self.mongo_db.environment_sensor.count_documents({
                    'device_id': device_id,
                    'timestamp': {'$gte': start_time, '$lte': end_time}
                })
                device_counts[device_id] = count
            
            max_device = max(device_counts, key=device_counts.get) if device_counts else None
            min_device = min(device_counts, key=device_counts.get) if device_counts else None
            
            logger.info(f"记录最多的设备: {max_device}, 最少的设备: {min_device}")
            
            # 5. 写入MySQL
            sql = """
            INSERT INTO daily_statistics 
            (stat_date, total_records, active_devices, avg_moisture, avg_oiliness, 
             avg_temperature, avg_humidity, avg_pm25, avg_co2, 
             max_records_device, min_records_device, calculated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE
                total_records = VALUES(total_records),
                active_devices = VALUES(active_devices),
                avg_moisture = VALUES(avg_moisture),
                avg_oiliness = VALUES(avg_oiliness),
                avg_temperature = VALUES(avg_temperature),
                avg_humidity = VALUES(avg_humidity),
                avg_pm25 = VALUES(avg_pm25),
                avg_co2 = VALUES(avg_co2),
                max_records_device = VALUES(max_records_device),
                min_records_device = VALUES(min_records_device),
                calculated_at = NOW()
            """
            
            self.mysql_cursor.execute(sql, (
                target_date, total_records, active_devices,
                avg_moisture, avg_oiliness, avg_temperature,
                avg_humidity, avg_pm25, avg_co2,
                max_device, min_device
            ))
            self.mysql_conn.commit()
            
            logger.info(f"✅ {target_date} 统计数据已成功写入MySQL")
            return True
            
        except Exception as e:
            logger.error(f"❌ 计算统计数据失败: {str(e)}", exc_info=True)
            self.mysql_conn.rollback()
            return False
    
    def cleanup_old_data(self, days=365):
        """清理旧统计数据（保留最近N天）"""
        try:
            cutoff_date = datetime.now().date() - timedelta(days=days)
            sql = "DELETE FROM daily_statistics WHERE stat_date < %s"
            self.mysql_cursor.execute(sql, (cutoff_date,))
            deleted = self.mysql_cursor.rowcount
            self.mysql_conn.commit()
            logger.info(f"清理了 {deleted} 条旧统计数据")
        except Exception as e:
            logger.error(f"清理旧数据失败: {str(e)}")
    
    def close(self):
        """关闭数据库连接"""
        self.mysql_cursor.close()
        self.mysql_conn.close()
        self.mongo_client.close()
        logger.info("数据库连接已关闭")


def main():
    """主函数：启动定时任务调度器"""
    task = DailyStatisticsTask()
    
    # 创建调度器
    scheduler = BackgroundScheduler()
    
    # 添加每日凌晨2点执行的任务
    scheduler.add_job(
        func=task.calculate_daily_statistics,
        trigger=CronTrigger(hour=2, minute=0),
        id='daily_statistics',
        name='每日统计数据计算',
        replace_existing=True
    )
    
    # 添加每周日凌晨3点的清理任务
    scheduler.add_job(
        func=task.cleanup_old_data,
        trigger=CronTrigger(day_of_week='sun', hour=3, minute=0),
        id='cleanup_old_data',
        name='清理旧统计数据',
        kwargs={'days': 365},
        replace_existing=True
    )
    
    # 启动调度器
    scheduler.start()
    logger.info("✅ 定时任务调度器已启动")
    logger.info("📅 每日凌晨2点自动计算统计数据")
    logger.info("🧹 每周日凌晨3点清理旧数据")
    
    try:
        # 保持程序运行
        while True:
            import time
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        task.close()
        logger.info("定时任务已停止")


if __name__ == '__main__':
    main()
