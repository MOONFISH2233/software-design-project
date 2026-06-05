"""修复触发器字符集问题"""
import pymysql

conn = pymysql.connect(host="127.0.0.1", port=3306, user="root", password="admin", database="software_design")
cur = conn.cursor()

# 删除
for trigger in ['trg_sync_devices_after_profile_update', 'trg_sync_devices_after_profile_insert']:
    cur.execute(f"DROP TRIGGER IF EXISTS {trigger}")

# 修复：使用 CONVERT() 统一字符集
update_trigger = """
CREATE TRIGGER trg_sync_devices_after_profile_update
AFTER UPDATE ON user_profiles
FOR EACH ROW
BEGIN
    DECLARE user_province VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    DECLARE user_city VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    DECLARE new_location VARCHAR(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

    SET user_province = JSON_UNQUOTE(JSON_EXTRACT(NEW.skincare_goals, '$.province'));
    SET user_city = JSON_UNQUOTE(JSON_EXTRACT(NEW.skincare_goals, '$.city'));

    IF user_province IS NOT NULL AND user_province != '' AND user_province != '未分配' THEN
        SET new_location = CONCAT_WS('-', user_province, user_city, '设备点位');

        UPDATE devices d
        INNER JOIN device_bindings db ON d.device_id = db.device_id
        SET d.location = new_location,
            d.updated_at = NOW()
        WHERE db.user_id = NEW.user_id
          AND (
              d.location IS NULL
              OR d.location = ''
              OR d.location IN ('??', '???', '????', '?????', '??????', '----', '--')
              OR (d.location LIKE '%-%' AND SUBSTRING_INDEX(d.location, '-', 1) COLLATE utf8mb4_unicode_ci != user_province)
          );
    END IF;
END;
"""

cur.execute(update_trigger)
print("Created UPDATE trigger (fixed charset)")

insert_trigger = """
CREATE TRIGGER trg_sync_devices_after_profile_insert
AFTER INSERT ON user_profiles
FOR EACH ROW
BEGIN
    DECLARE user_province VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    DECLARE user_city VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    DECLARE new_location VARCHAR(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

    SET user_province = JSON_UNQUOTE(JSON_EXTRACT(NEW.skincare_goals, '$.province'));
    SET user_city = JSON_UNQUOTE(JSON_EXTRACT(NEW.skincare_goals, '$.city'));

    IF user_province IS NOT NULL AND user_province != '' AND user_province != '未分配' THEN
        SET new_location = CONCAT_WS('-', user_province, user_city, '设备点位');

        UPDATE devices d
        INNER JOIN device_bindings db ON d.device_id = db.device_id
        SET d.location = new_location,
            d.updated_at = NOW()
        WHERE db.user_id = NEW.user_id;
    END IF;
END;
"""

cur.execute(insert_trigger)
print("Created INSERT trigger (fixed charset)")

conn.commit()
conn.close()
print("All triggers created")
