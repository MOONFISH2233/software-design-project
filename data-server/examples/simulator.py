import threading
import time
import random
import csv
from datetime import datetime
from local_to_cloud import DataUploader   # 确保 local_to_cloud.py 在同一目录

# ================= 配置区 =================
CSV_FILE_NAME = "mirror_sensor_data.csv"
TXT_FILE_NAME = "mirror_sensor_log.txt"
CLOUD_URL = "http://47.103.108.47:5000"   # 你的云服务器地址

# 创建一个停止事件（线程安全标志）
stop_event = threading.Event()

# 创建线程锁，防止多线程同时写入文件时数据错乱
file_lock = threading.Lock()

# 创建云端上传器（全局共享，所有线程共用）
uploader = DataUploader(CLOUD_URL)

# ================= 初始化文件 =================
# 初始化 CSV 文件并写入表头
with open(CSV_FILE_NAME, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["时间戳", "传感器来源", "数据项1", "数据项2"])

# 初始化 TXT 文件并写入标题头
with open(TXT_FILE_NAME, mode='w', encoding='utf-8') as file:
    file.write("=== AI宠物美妆镜 - 传感器后台数据日志 ===\n")

# ================= 线程 1：模拟皮肤传感器 =================
def simulate_skin_sensor():
    while not stop_event.is_set():   # 检查停止标志
        # 生成随机数据
        moisture = random.randint(40, 90)      # 水分度 40%-90%
        oiliness = random.randint(10, 60)      # 油亮度 10%-60%
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 写入文件（加锁）
        with file_lock:
            with open(CSV_FILE_NAME, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, "皮肤传感器", f"水分度:{moisture}%", f"油亮度:{oiliness}%"])
            with open(TXT_FILE_NAME, mode='a', encoding='utf-8') as file:
                file.write(f"[{timestamp}] [皮肤检测] 💧 当前水分度: {moisture}%, 当前油亮度: {oiliness}%\n")

        print(f"[{timestamp}] 💧 皮肤传感器已记录 -> 水分度:{moisture}% | 油亮度:{oiliness}%")

        # 发送到云端（不加锁，网络操作单独处理）
        data = {
            "sensor_type": "skin",
            "moisture": moisture,
            "oiliness": oiliness,
            "timestamp": timestamp
        }
        try:
            result = uploader.upload_data(data, description="皮肤传感器数据")
            if result.get("status") == "success":
                print(f"    📡 云端已接收：{result.get('filename')}")
            else:
                print(f"    ⚠️ 上传失败：{result.get('message')}")
        except Exception as e:
            print(f"    ❌ 上传异常：{e}")

        # 模拟采样间隔，但每隔0.5秒检查一次停止标志，以便快速响应退出
        for _ in range(4):   # 2秒 = 4 * 0.5秒
            if stop_event.is_set():
                break
            time.sleep(0.5)

# ================= 线程 2：模拟环境传感器 =================
def simulate_env_sensor():
    while not stop_event.is_set():
        # 生成随机数据
        humidity = random.randint(30, 80)      # 环境湿度 30%-80%
        light_lux = random.randint(200, 1000)  # 环境光照度 200-1000 Lux
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 写入文件（加锁）
        with file_lock:
            with open(CSV_FILE_NAME, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, "环境传感器", f"环境湿度:{humidity}%", f"光照度:{light_lux}Lux"])
            with open(TXT_FILE_NAME, mode='a', encoding='utf-8') as file:
                file.write(f"[{timestamp}] [环境检测] ☀️ 当前环境湿度: {humidity}%, 环境光照度: {light_lux}Lux\n")

        print(f"[{timestamp}] ☀️ 环境传感器已记录 -> 湿度:{humidity}% | 光照度:{light_lux}Lux")

        # 发送到云端
        data = {
            "sensor_type": "environment",
            "humidity": humidity,
            "light_lux": light_lux,
            "timestamp": timestamp
        }
        try:
            result = uploader.upload_data(data, description="环境传感器数据")
            if result.get("status") == "success":
                print(f"    📡 云端已接收：{result.get('filename')}")
            else:
                print(f"    ⚠️ 上传失败：{result.get('message')}")
        except Exception as e:
            print(f"    ❌ 上传异常：{e}")

        # 模拟采样间隔（每 3 秒），但分段睡眠以便快速响应退出
        for _ in range(6):   # 3秒 = 6 * 0.5秒
            if stop_event.is_set():
                break
            time.sleep(0.5)

# ================= 主程序入口 =================
if __name__ == "__main__":
    print("🚀 魔镜 C 端数据模拟器 (Simulator) 已启动...")
    print(f"📡 云端服务器地址：{CLOUD_URL}")
    print("提示：按 Ctrl+C 可以停止运行\n")

    # 创建两个线程
    t1 = threading.Thread(target=simulate_skin_sensor, name="SkinThread")
    t2 = threading.Thread(target=simulate_env_sensor, name="EnvThread")

    # 启动线程
    t1.start()
    t2.start()

    # 等待用户中断
    try:
        while True:
            time.sleep(0.5)
            if not t1.is_alive() and not t2.is_alive():
                break
    except KeyboardInterrupt:
        print("\n🛑 收到中断信号，正在停止模拟器...")
        stop_event.set()   # 通知所有线程停止

    # 等待线程结束
    t1.join()
    t2.join()
    print("✅ 模拟器已安全退出。")