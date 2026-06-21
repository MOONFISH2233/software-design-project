import json

import pymysql

DB = dict(host="localhost", user="root", password="admin", database="software_design", charset="utf8mb4")


def is_broken(value):
    text = str(value or "").strip()
    if not text:
        return True
    if "未分配地区" in text:
        return True
    return text.count("?") >= max(2, len(text) // 2) or text in {"?", "??", "???", "????", "?????"}


def meta_from_goals(goals):
    if isinstance(goals, str):
        try:
            goals = json.loads(goals)
        except Exception:
            goals = {}
    if not isinstance(goals, dict):
        goals = {}
    province = goals.get("province") or "北京"
    city = goals.get("city") or province
    return province, city


def main():
    conn = pymysql.connect(**DB)
    changed = 0
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                select d.device_id,d.device_type,d.location,u.id,u.nickname,p.skincare_goals
                from devices d
                left join device_bindings b on b.device_id=d.device_id and b.status='active'
                left join users u on u.id=b.user_id
                left join user_profiles p on p.user_id=u.id
                """
            )
            rows = cur.fetchall()
            for device_id, device_type, location, user_id, nickname, goals in rows:
                if not is_broken(location):
                    continue
                province, city = meta_from_goals(goals)
                is_env = device_type == "environment" or str(device_id).startswith(("ENV", "RENV"))
                suffix = "环境监测点" if is_env else "皮肤检测终端"
                display = f"{province}-{city}-{suffix}"
                cur.execute("update devices set location=%s where device_id=%s", (display, device_id))
                changed += 1
        conn.commit()
        print(json.dumps({"success": True, "changed": changed}, ensure_ascii=False))
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
