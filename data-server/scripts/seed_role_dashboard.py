import json
import random
from datetime import date, datetime, timedelta

import pymysql


DB = dict(host="localhost", user="root", password="admin", database="software_design", charset="utf8mb4")

PROVINCES = [
    ("北京", "北京市", 42, "华北"),
    ("河北", "石家庄市", 45, "华北"),
    ("山东", "济南市", 50, "华东"),
    ("河南", "郑州市", 48, "华中"),
    ("江苏", "南京市", 62, "华东"),
    ("上海", "上海市", 67, "华东"),
    ("浙江", "杭州市", 70, "华东"),
    ("安徽", "合肥市", 61, "华东"),
    ("湖北", "武汉市", 63, "华中"),
    ("湖南", "长沙市", 66, "华中"),
    ("广东", "广州市", 73, "华南"),
    ("广西", "南宁市", 75, "华南"),
    ("福建", "福州市", 72, "华东"),
    ("四川", "成都市", 58, "西南"),
    ("重庆", "重庆市", 67, "西南"),
    ("陕西", "西安市", 44, "西北"),
    ("辽宁", "沈阳市", 45, "东北"),
    ("黑龙江", "哈尔滨市", 40, "东北"),
    ("新疆", "乌鲁木齐市", 32, "西北"),
    ("云南", "昆明市", 69, "西南"),
]

NAMES = [
    "李骏逸", "刘湘渝", "刘卓雅", "陈若溪", "王思远", "张沐阳", "赵嘉宁", "周予安", "吴清越", "郑雨桐",
    "孙亦辰", "马梓涵", "朱星禾", "胡景然", "林知夏", "何以宁", "郭昱辰", "高一诺", "罗子衿", "梁若楠",
    "谢云舟", "宋明轩", "唐语嫣", "许嘉禾", "邓安琪", "韩沐宸", "冯若瑜", "曹雨泽", "程溪月", "彭书瑶",
    "曾皓然", "董芷晴", "袁景行", "潘思齐", "蒋知微", "蔡宇航", "余可欣", "叶星辰", "苏念慈", "杜若安",
    "魏清晗", "沈一鸣", "卢予初", "邹亦凡", "邱嘉悦", "熊浩宇", "姜晚晴", "任泽宇", "尹若曦", "范星野",
    "方以沫", "石若川", "谭嘉树", "廖清欢", "贺知行", "姚安然", "邵云舒", "汪景澄", "毛予希", "孔令仪",
    "白若尘", "龙一诺", "严星河", "金雨眠", "莫子昂", "雷清宁", "夏知远", "汤若初", "黎嘉木", "钟予墨",
    "乔思源", "孟子衿", "秦以航", "温若乔", "章景宁", "陆嘉年", "万诗涵", "钱沐晨", "易知秋", "顾清越",
]

SKIN_TYPES = ["干性", "油性", "混合性", "敏感性", "中性"]
ABNORMAL_PROVINCES = {"广东", "浙江", "新疆", "湖北"}


def execute(cur, sql, params=None):
    cur.execute(sql, params or ())
    return cur


def fetch_one(cur, sql, params=None):
    cur.execute(sql, params or ())
    return cur.fetchone()


def upsert_user(cur, username, nickname, role, phone, email=None):
    row = fetch_one(cur, "select id from users where username=%s", (username,))
    now = datetime.now()
    if row:
        user_id = row[0]
        execute(
            cur,
            "update users set password_hash=%s,nickname=%s,phone=%s,email=%s,role=%s,status='active',updated_at=%s where id=%s",
            ("123456", nickname, phone, email or f"{username}@demo.local", role, now, user_id),
        )
        return user_id
    execute(
        cur,
        """
        insert into users(username,password_hash,nickname,phone,email,role,status,created_at,updated_at)
        values(%s,%s,%s,%s,%s,%s,'active',%s,%s)
        """,
        (username, "123456", nickname, phone, email or f"{username}@demo.local", role, now, now),
    )
    return cur.lastrowid


def upsert_profile(cur, user_id, province, city, age, gender, skin_type, frequency, level):
    goals = {
        "province": province,
        "city": city,
        "usage_frequency": frequency,
        "member_level": level,
        "data_source": "role_dashboard_seed",
    }
    row = fetch_one(cur, "select id from user_profiles where user_id=%s", (user_id,))
    now = datetime.now()
    if row:
        execute(
            cur,
            """
            update user_profiles
            set skin_type=%s,skincare_goals=%s,age=%s,gender=%s,last_update=%s
            where user_id=%s
            """,
            (skin_type, json.dumps(goals, ensure_ascii=False), age, gender, now, user_id),
        )
    else:
        execute(
            cur,
            """
            insert into user_profiles(user_id,skin_type,skincare_goals,age,gender,register_date,last_update)
            values(%s,%s,%s,%s,%s,%s,%s)
            """,
            (user_id, skin_type, json.dumps(goals, ensure_ascii=False), age, gender, now, now),
        )


def upsert_device(cur, device_id, device_type, location, install_date):
    row = fetch_one(cur, "select id from devices where device_id=%s", (device_id,))
    now = datetime.now()
    battery = random.randint(62, 98)
    signal = random.randint(-68, -38)
    if row:
        execute(
            cur,
            """
            update devices
            set device_type=%s,firmware_version='v2.1.0',location=%s,status='online',
                battery_level=%s,signal_strength=%s,last_heartbeat=%s,updated_at=%s
            where device_id=%s
            """,
            (device_type, location, battery, signal, now, now, device_id),
        )
    else:
        execute(
            cur,
            """
            insert into devices(device_id,device_type,firmware_version,install_date,location,status,battery_level,signal_strength,last_heartbeat,created_at,updated_at)
            values(%s,%s,'v2.1.0',%s,%s,'online',%s,%s,%s,%s,%s)
            """,
            (device_id, device_type, install_date, location, battery, signal, now, now, now),
        )


def bind_device(cur, user_id, device_id, primary=False):
    now = datetime.now()
    execute(
        cur,
        "update device_bindings set status='unbound',unbind_time=%s where device_id=%s and status='active' and user_id<>%s",
        (now, device_id, user_id),
    )
    row = fetch_one(cur, "select id from device_bindings where user_id=%s and device_id=%s", (user_id, device_id))
    if row:
        execute(
            cur,
            "update device_bindings set status='active',unbind_time=null,bind_time=%s,is_primary=%s,notes='role dashboard seed' where id=%s",
            (now, 1 if primary else 0, row[0]),
        )
    else:
        execute(
            cur,
            """
            insert into device_bindings(user_id,device_id,bind_time,is_primary,status,notes)
            values(%s,%s,%s,%s,'active','role dashboard seed')
            """,
            (user_id, device_id, now, 1 if primary else 0),
        )


def seed_skin_rows(cur, device_id, province, humidity_base, user_index):
    random.seed(f"skin-{device_id}")
    now = datetime.now().replace(microsecond=0)
    expected = max(36, min(58, 28 + 0.35 * humidity_base))
    abnormal_offset = -13 if province in ABNORMAL_PROVINCES else random.uniform(-4, 5)
    base_moisture = expected + abnormal_offset + (user_index % 5 - 2)
    for day in range(14):
        for slot in (9, 15, 21):
            ts = (now - timedelta(days=13 - day)).replace(hour=slot, minute=random.randint(0, 55), second=0)
            moisture = int(max(25, min(72, base_moisture + random.uniform(-3, 3) + day * 0.12)))
            oiliness = int(max(18, min(75, 44 + random.uniform(-12, 12))))
            temp = round(32.0 + random.random() * 3.0, 1)
            request_id = f"seed-skin-{device_id}-{day}-{slot}"
            execute(
                cur,
                """
                insert ignore into skin_sensor_data(device_id,moisture,oiliness,temperature,sensor_time,received_at,client_ip,request_id,validated,quality_score,created_at)
                values(%s,%s,%s,%s,%s,%s,'seed',%s,1,%s,%s)
                """,
                (device_id, moisture, oiliness, temp, ts, ts, request_id, round(random.uniform(0.92, 0.99), 2), ts),
            )


def seed_env_rows(cur, device_id, province, city, humidity_base):
    random.seed(f"env-{device_id}")
    now = datetime.now().replace(microsecond=0)
    for day in range(14):
        for slot in (8, 14, 20):
            ts = (now - timedelta(days=13 - day)).replace(hour=slot, minute=random.randint(0, 55), second=0)
            humidity = round(max(24, min(88, humidity_base + random.uniform(-6, 6))), 1)
            temp = round(21 + random.random() * 9, 1)
            pm25 = random.randint(8, 55)
            co2 = random.randint(420, 960)
            request_id = f"seed-env-{device_id}-{day}-{slot}"
            execute(
                cur,
                """
                insert ignore into environment_sensor_data(device_id,temperature,humidity,pm25,co2,location,sensor_time,received_at,client_ip,request_id,validated,quality_score,created_at)
                values(%s,%s,%s,%s,%s,%s,%s,%s,'seed',%s,1,%s,%s)
                """,
                (device_id, temp, humidity, pm25, co2, f"{province}-{city}", ts, ts, request_id, round(random.uniform(0.92, 0.99), 2), ts),
            )


def main():
    random.seed(20260527)
    conn = pymysql.connect(**DB)
    try:
        with conn.cursor() as cur:
            upsert_user(cur, "leader", "领导演示账号", "leader", "18800000001", "leader@demo.local")
            upsert_user(cur, "support", "客服技术账号", "support", "18800000002", "support@demo.local")

            user_ids = []
            for i in range(80):
                province, city, humidity, region = PROVINCES[i % len(PROVINCES)]
                username = f"u{i + 1:03d}"
                nickname = NAMES[i]
                user_id = upsert_user(cur, username, nickname, "user", f"139{10000000 + i:08d}", f"{username}@demo.local")
                user_ids.append((user_id, province, city, humidity, i))
                age = 18 + (i * 7) % 38
                gender = "女" if i % 3 else "男"
                skin_type = SKIN_TYPES[i % len(SKIN_TYPES)]
                frequency = round(2.8 + (i % 7) * 0.7 + random.random(), 1)
                level = ["普通", "银卡", "金卡", "重点跟进"][i % 4]
                upsert_profile(cur, user_id, province, city, age, gender, skin_type, frequency, level)

                skin_id = f"RSKIN{i + 1:03d}"
                location = f"{province}-{city}-皮肤检测终端"
                upsert_device(cur, skin_id, "skin", location, date.today() - timedelta(days=60 - i % 40))
                bind_device(cur, user_id, skin_id, primary=True)
                seed_skin_rows(cur, skin_id, province, humidity, i)

            for i, (user_id, province, city, humidity, user_index) in enumerate(user_ids[:20]):
                env_id = f"RENV{i + 1:03d}"
                location = f"{province}-{city}-环境监测点"
                upsert_device(cur, env_id, "environment", location, date.today() - timedelta(days=45 - i % 20))
                bind_device(cur, user_id, env_id, primary=False)
                seed_env_rows(cur, env_id, province, city, humidity)

            conn.commit()
            execute(cur, "select count(*) from users where role='user'")
            user_count = cur.fetchone()[0]
            execute(cur, "select count(*) from devices")
            device_count = cur.fetchone()[0]
            execute(cur, "select count(*) from device_bindings where status='active'")
            binding_count = cur.fetchone()[0]
            print(json.dumps({
                "success": True,
                "users": user_count,
                "devices": device_count,
                "active_bindings": binding_count,
                "accounts": {"leader": "leader/123456", "support": "support/123456"},
            }, ensure_ascii=False))
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
