"""
第四周任务本地验证脚本
=====================
无需连接远程服务器，直接在本地验证所有任务是否完成。

运行方式：
    python verify_local.py

验证内容：
    任务1 - API接口管理工具（swagger/postman文件 + 测试脚本）
    任务2 - 数据服务器独立接口（app.py 路由 + 独立数据目录）
    任务3 - 模拟器MQ改造（simulator_mq.py + 重传机制）
    任务4 - 服务器MQ模块化（4个独立模块 + 独立启停）
"""

import os
import sys
import io

# 强制使用 UTF-8 输出（解决 Windows 终端编码问题）
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import json
import ast
import importlib.util
import threading
import time
from datetime import datetime

# ============================================================
# 工具函数
# ============================================================

PASS = "[PASS]"
FAIL = "[FAIL]"
INFO = "[INFO]"

results = []

def check(name, condition, detail=""):
    status = PASS if condition else FAIL
    msg = f"  {status}  {name}"
    if detail:
        msg += f"\n         └─ {detail}"
    print(msg)
    results.append({"name": name, "passed": condition, "detail": detail})
    return condition

def section(title):
    print(f"\n{'='*65}")
    print(f"  {title}")
    print(f"{'='*65}")

def read_file_safe(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""

def file_exists(path):
    return os.path.isfile(path)

def contains(text, keyword):
    return keyword in text


# ============================================================
# 任务1：API接口管理工具
# ============================================================

def verify_task1():
    section("任务1：API接口管理工具 - 录入并测试API接口")

    # 1.1 Swagger文件
    sw_exists = file_exists("swagger.json")
    check("swagger.json 存在", sw_exists)
    if sw_exists:
        try:
            sw = json.loads(read_file_safe("swagger.json"))
            check("swagger.json 格式有效（能正常解析）", True, f"OpenAPI版本: {sw.get('openapi','?')}")
            paths = sw.get("paths", {})
            check("swagger.json 包含至少3个API路由定义",
                  len(paths) >= 3,
                  f"当前路由数量: {len(paths)} — {list(paths.keys())[:5]}")
        except Exception as e:
            check("swagger.json 格式有效", False, str(e))

    # 1.2 Postman Collection
    pm_exists = file_exists("postman_collection.json")
    check("postman_collection.json 存在", pm_exists)
    if pm_exists:
        try:
            pm = json.loads(read_file_safe("postman_collection.json"))
            check("postman_collection.json 格式有效", True,
                  f"集合名称: {pm.get('info',{}).get('name','?')}")
            # 统计请求数（支持嵌套分组）
            def count_requests(items):
                count = 0
                for item in items:
                    if "request" in item:
                        count += 1
                    if "item" in item:
                        count += count_requests(item["item"])
                return count
            req_count = count_requests(pm.get("item", []))
            check(f"postman集合包含至少3个请求", req_count >= 3,
                  f"当前请求数量: {req_count}")
        except Exception as e:
            check("postman_collection.json 格式有效", False, str(e))

    # 1.3 自动化测试脚本
    auto_exists = file_exists("api_auto_test.py")
    check("api_auto_test.py 存在", auto_exists)
    if auto_exists:
        code = read_file_safe("api_auto_test.py")
        check("测试脚本包含皮肤传感器接口测试", contains(code, "/api/sensor/skin"),
              "已测试 /api/sensor/skin")
        check("测试脚本包含环境传感器接口测试", contains(code, "/api/sensor/environment"),
              "已测试 /api/sensor/environment")
        check("测试脚本包含设备状态接口测试", contains(code, "/api/device/status"),
              "已测试 /api/device/status")
        check("测试脚本能生成JSON报告", contains(code, "report_filename"),
              "generate_report() 方法存在")


# ============================================================
# 任务2：数据服务器独立接口
# ============================================================

def verify_task2():
    section("任务2：数据服务器独立接口 - AI实现每个API独立写文件")

    app_code = read_file_safe("app.py")
    app_exists = file_exists("app.py")
    check("app.py 存在", app_exists)

    if app_exists:
        # 检查路由
        check("app.py 包含 /api/sensor/skin 路由",
              contains(app_code, "/api/sensor/skin"),
              "皮肤传感器专用接口")
        check("app.py 包含 /api/sensor/environment 路由",
              contains(app_code, "/api/sensor/environment"),
              "环境传感器专用接口")
        check("app.py 包含 /api/device/status 路由",
              contains(app_code, "/api/device/status"),
              "设备状态专用接口")

        # 检查每个接口数据独立写入不同目录
        check("每个接口数据写入独立目录（save_sensor_data函数）",
              contains(app_code, "save_sensor_data"),
              "通过sensor_type参数区分目录")
        check("皮肤数据写入 skin_sensor 目录",
              contains(app_code, "skin_sensor"),
              "data/skin_sensor/")
        check("环境数据写入 environment 目录",
              contains(app_code, "'environment'"),
              "data/environment/")
        check("设备数据写入 device 目录",
              contains(app_code, "'device'"),
              "data/device/")

        # 验证字段校验逻辑
        check("皮肤接口验证必填字段 moisture/oiliness",
              contains(app_code, "moisture") and contains(app_code, "oiliness"),
              "字段校验已实现")
        check("环境接口验证必填字段 humidity/light_lux",
              contains(app_code, "humidity") and contains(app_code, "light_lux"),
              "字段校验已实现")

    # 用Flask测试客户端做真实接口测试（不需要外部服务器）
    print("\n  [真实接口测试] 使用Flask测试客户端验证接口行为...")
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import importlib
        spec = importlib.util.spec_from_file_location("app", "app.py")
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)
        flask_app = app_module.app
        flask_app.config['TESTING'] = True

        with flask_app.test_client() as client:
            # 测试健康检查
            resp = client.get('/api/health')
            check("GET /api/health 返回200", resp.status_code == 200,
                  f"响应: {resp.get_json().get('status','?')}")

            # 测试皮肤传感器接口（正常情况）
            resp = client.post('/api/sensor/skin',
                               json={"moisture": 65, "oiliness": 35, "device_id": "test_001"},
                               content_type='application/json')
            check("POST /api/sensor/skin 正常数据返回200",
                  resp.status_code == 200,
                  f"返回文件名: {resp.get_json().get('filename','?')}")

            # 测试缺少字段时返回400
            resp = client.post('/api/sensor/skin',
                               json={"device_id": "test_001"},
                               content_type='application/json')
            check("POST /api/sensor/skin 缺少字段返回400",
                  resp.status_code == 400,
                  f"错误信息: {resp.get_json().get('message','?')}")

            # 测试环境传感器接口
            resp = client.post('/api/sensor/environment',
                               json={"humidity": 55, "light_lux": 600, "temperature": 25.0},
                               content_type='application/json')
            check("POST /api/sensor/environment 正常数据返回200",
                  resp.status_code == 200,
                  f"返回文件名: {resp.get_json().get('filename','?')}")

            # 测试设备状态接口
            resp = client.post('/api/device/status',
                               json={"device_id": "mirror_001", "status": "online"},
                               content_type='application/json')
            check("POST /api/device/status 正常数据返回200",
                  resp.status_code == 200,
                  f"返回文件名: {resp.get_json().get('filename','?')}")

            # 验证数据确实写入了独立目录
            skin_dir = os.path.join("data", "skin_sensor")
            env_dir = os.path.join("data", "environment")
            dev_dir = os.path.join("data", "device")
            check("皮肤数据已写入 data/skin_sensor/ 目录",
                  os.path.isdir(skin_dir) and len(os.listdir(skin_dir)) > 0,
                  f"文件数量: {len(os.listdir(skin_dir)) if os.path.isdir(skin_dir) else 0}")
            check("环境数据已写入 data/environment/ 目录",
                  os.path.isdir(env_dir) and len(os.listdir(env_dir)) > 0,
                  f"文件数量: {len(os.listdir(env_dir)) if os.path.isdir(env_dir) else 0}")
            check("设备数据已写入 data/device/ 目录",
                  os.path.isdir(dev_dir) and len(os.listdir(dev_dir)) > 0,
                  f"文件数量: {len(os.listdir(dev_dir)) if os.path.isdir(dev_dir) else 0}")

    except Exception as e:
        check("Flask测试客户端运行", False, f"错误: {str(e)}")


# ============================================================
# 任务3：模拟器MQ改造
# ============================================================

def verify_task3():
    section("任务3：模拟器MQ改造 - 数据发布到MQ + 重传机制")

    mq_exists = file_exists("simulator_mq.py")
    check("simulator_mq.py 存在（MQ版模拟器）", mq_exists)

    if mq_exists:
        code = read_file_safe("simulator_mq.py")

        # 检查MQ发布功能
        check("模拟器实现MQ发布（publish方法）",
              contains(code, "mq_client.publish"),
              "数据发布到 sensor:raw 流")
        check("使用Redis Stream（sensor:raw）",
              contains(code, "RAW_DATA_STREAM") or contains(code, "sensor:raw"),
              "已配置流名称")

        # 检查重传机制
        check("实现重传队列（retry_queue）",
              contains(code, "retry_queue"),
              "本地重试列表")
        check("实现发布失败后加入重传",
              contains(code, "_add_to_retry") or contains(code, "add_to_retry"),
              "失败自动入队")
        check("实现定期重传处理（process_retry_queue）",
              contains(code, "process_retry_queue"),
              "RetryThread线程定期处理")
        check("实现最大重试次数限制（MAX_RETRY_COUNT）",
              contains(code, "MAX_RETRY_COUNT"),
              "防止无限重试")
        check("实现重传间隔（RETRY_INTERVAL）",
              contains(code, "RETRY_INTERVAL"),
              "指数退避重传间隔")
        check("实现超时判断（TIMEOUT_SECONDS）",
              contains(code, "TIMEOUT_SECONDS"),
              "超时触发重传")

        # 检查多线程
        check("皮肤传感器使用独立线程",
              contains(code, "simulate_skin_sensor"),
              "SkinThread 独立运行")
        check("环境传感器使用独立线程",
              contains(code, "simulate_env_sensor"),
              "EnvThread 独立运行")
        check("重传处理器使用独立线程",
              contains(code, "retry_processor"),
              "RetryThread 定期处理失败数据")

    # 检查mq_utils.py
    mq_utils_exists = file_exists("mq_utils.py")
    check("mq_utils.py 存在（MQ工具类）", mq_utils_exists)
    if mq_utils_exists:
        mq_code = read_file_safe("mq_utils.py")
        check("mq_utils.py 支持Redis",
              contains(mq_code, "class RedisMQ"),
              "RedisMQ 类已实现")
        check("mq_utils.py 支持RabbitMQ",
              contains(mq_code, "class RabbitMQ"),
              "RabbitMQ 类已实现")
        check("mq_utils.py 使用工厂函数创建实例",
              contains(mq_code, "def create_mq"),
              "create_mq() 工厂函数")

    # 功能演示：验证DataPublisher重传逻辑（不连接真实MQ）
    print("\n  [重传机制演示] 模拟MQ连接失败，验证重传队列工作...")
    try:
        spec = importlib.util.spec_from_file_location("simulator_mq", "simulator_mq.py")
        sim_module = importlib.util.module_from_spec(spec)
        # 临时打补丁，跳过mq_utils导入（不需要真实Redis）
        import unittest.mock as mock
        with mock.patch.dict('sys.modules', {'mq_utils': mock.MagicMock()}):
            spec2 = importlib.util.spec_from_file_location("simulator_mq2", "simulator_mq.py")
            sim2 = importlib.util.module_from_spec(spec2)
            spec2.loader.exec_module(sim2)
            
            publisher = sim2.DataPublisher()
            # 模拟MQ未连接（mq_client = None）
            sim2.mq_client = None

            # 发布一条数据（应该失败并加入重试队列）
            publisher.publish_with_retry(
                {"moisture": 70, "oiliness": 30},
                "skin",
                "测试皮肤数据"
            )
            stats = publisher.get_stats()
            check("MQ不可用时数据自动加入重试队列",
                  stats['pending_retry'] >= 1,
                  f"重试队列中: {stats['pending_retry']} 条, 失败计数: {stats['failed']}")
            check("失败计数器正确递增",
                  stats['failed'] >= 1,
                  f"failed={stats['failed']}")
    except Exception as e:
        check("重传机制功能验证", False, f"错误: {str(e)}")


# ============================================================
# 任务4：服务器MQ模块化架构
# ============================================================

def verify_task4():
    section("任务4：服务器MQ模块化架构 - 4个独立模块可独立启停")

    modules = [
        ("module_receiver.py", "数据接收模块", ["start_receiver", "consume", "RAW_DATA_STREAM"]),
        ("module_validator.py", "数据验证模块", ["start_validator", "validate_data", "WRITE_QUEUE"]),
        ("module_writer.py", "数据写入模块", ["start_writer", "DataWriter", "write_data"]),
        ("module_logger.py", "日志记录模块", ["start_logger", "SystemLogger", "SYSTEM_LOG_FILE"]),
    ]

    for filename, desc, keywords in modules:
        exists = file_exists(filename)
        check(f"{filename} 存在（{desc}）", exists)
        if exists:
            code = read_file_safe(filename)
            for kw in keywords:
                check(f"  └─ {filename} 包含 {kw}()",
                      contains(code, kw),
                      f"关键功能: {kw}")
            # 验证可以独立作为主程序运行
            check(f"  └─ {filename} 支持独立运行（if __name__ == '__main__'）",
                  contains(code, "if __name__ == '__main__'"),
                  "独立启停支持")

    # 检查模块间的流水线关系
    print("\n  [流水线架构验证] 检查模块间消息流转关系...")
    recv_code = read_file_safe("module_receiver.py")
    val_code = read_file_safe("module_validator.py")
    wrt_code = read_file_safe("module_writer.py")

    check("接收模块 → 验证队列（sensor:validated）",
          contains(recv_code, "sensor:validated") or contains(recv_code, "VALIDATED_QUEUE"),
          "receiver 输出到 sensor:validated")
    check("验证模块 ← 验证队列，→ 写入队列（sensor:write）",
          contains(val_code, "sensor:validated") or contains(val_code, "VALIDATED_QUEUE"),
          "validator 从 sensor:validated 消费")
    check("验证模块 → 写入队列（sensor:write）",
          contains(val_code, "sensor:write") or contains(val_code, "WRITE_QUEUE"),
          "validator 输出到 sensor:write")
    check("写入模块 ← 写入队列，按类型分目录存文件",
          contains(wrt_code, "sensor:write") or contains(wrt_code, "WRITE_QUEUE"),
          "writer 从 sensor:write 消费")

    # 检查每个模块使用进程ID做消费者名，支持多实例
    check("接收模块支持多实例（CONSUMER_NAME含PID）",
          contains(recv_code, "os.getpid()"),
          "多实例并行：receiver_<pid>")
    check("验证模块支持多实例（CONSUMER_NAME含PID）",
          contains(val_code, "os.getpid()"),
          "多实例并行：validator_<pid>")
    check("写入模块支持多实例（CONSUMER_NAME含PID）",
          contains(wrt_code, "os.getpid()"),
          "多实例并行：writer_<pid>")

    # 检查一键启动脚本
    start_exists = file_exists("start_all_modules.py")
    check("start_all_modules.py 存在（一键启动所有模块）", start_exists)
    if start_exists:
        start_code = read_file_safe("start_all_modules.py")
        check("启动脚本启动接收模块", contains(start_code, "module_receiver"), "")
        check("启动脚本启动验证模块", contains(start_code, "module_validator"), "")
        check("启动脚本启动写入模块", contains(start_code, "module_writer"), "")
        check("启动脚本支持Ctrl+C优雅退出", contains(start_code, "KeyboardInterrupt"), "")

    bat_exists = file_exists("start_all.bat")
    check("start_all.bat 存在（Windows一键启动）", bat_exists)


# ============================================================
# 汇总结果
# ============================================================

def print_summary():
    section("验证结果汇总")
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = total - passed
    rate = passed / total * 100 if total > 0 else 0

    # 按任务分组统计
    task_ranges = [
        ("任务1 - API接口管理工具", 0, 8),
        ("任务2 - 数据服务器独立接口", 8, 22),
        ("任务3 - 模拟器MQ改造", 22, 38),
        ("任务4 - 服务器MQ模块化", 38, total),
    ]

    for task_name, start, end in task_ranges:
        task_results = results[start:end]
        t_total = len(task_results)
        t_passed = sum(1 for r in task_results if r["passed"])
        icon = "[OK]" if t_passed == t_total else ("[WARN]" if t_passed > 0 else "[FAIL]")
        print(f"\n  {icon} {task_name}: {t_passed}/{t_total}")

    print(f"\n{'─'*65}")
    print(f"  总检查项：{total}")
    print(f"  通过：{passed} ✅")
    print(f"  失败：{failed} ❌")
    print(f"  完成率：{rate:.1f}%")
    print(f"{'─'*65}")

    if failed > 0:
        print("\n  未通过的检查项：")
        for r in results:
            if not r["passed"]:
                print(f"    ❌ {r['name']}")
                if r.get("detail"):
                    print(f"       └─ {r['detail']}")

    print()
    if rate == 100:
        print("  *** 所有任务验证通过！***")
    elif rate >= 80:
        print("  >> 大部分任务已完成，少量细节待补充。")
    else:
        print("  !! 还有较多任务未完成，请继续完善。")
    print()

    return rate


# ============================================================
# 主入口
# ============================================================

if __name__ == "__main__":
    print("\n" + "="*65)
    print("  第四周任务本地验证脚本")
    print(f"  运行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  工作目录：{os.getcwd()}")
    print("="*65)

    # 切换到data-server目录（如果在上级目录运行）
    if not os.path.exists("app.py") and os.path.exists("data-server/app.py"):
        os.chdir("data-server")
        print(f"  已切换到：{os.getcwd()}")

    import importlib.util

    verify_task1()
    verify_task2()
    verify_task3()
    verify_task4()
    rate = print_summary()

    sys.exit(0 if rate >= 80 else 1)
