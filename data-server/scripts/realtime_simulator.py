#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Write live mirror sensor readings into MySQL for the mini program dashboard.

The existing Docker simulator only writes CSV/TXT files. The mini program reads
MySQL through Flask, so this small daemon feeds the same tables the API uses.
"""
import datetime as dt
import logging
import os
import random
import signal
import sys
import time
import uuid

import pymysql

DB_CONFIG = {
    "host": os.getenv("MIRROR_DB_HOST", "127.0.0.1"),
    "user": os.getenv("MIRROR_DB_USER", "root"),
    "password": os.getenv("MIRROR_DB_PASSWORD", "admin"),
    "db": os.getenv("MIRROR_DB_NAME", "software_design"),
    "charset": "utf8mb4",
    "autocommit": False,
}

INTERVAL_SECONDS = int(os.getenv("MIRROR_SIM_INTERVAL", "10"))
RUNNING = True

SKIN_STATES = {
    "DEV_001": {"moisture": 48.0, "oiliness": 39.0, "temperature": 33.1, "battery": 95, "signal": -48},
    "DEV_002": {"moisture": 43.0, "oiliness": 45.0, "temperature": 32.8, "battery": 88, "signal": -53},
}
ENV_STATE = {
    "device_id": "ENV_001",
    "temperature": 25.0,
    "humidity": 54.0,
    "pm25": 22.0,
    "co2": 620.0,
    "battery": 91,
    "signal": -46,
    "location": "??",
}

ENV_STATES = {ENV_STATE["device_id"]: ENV_STATE}


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def stop(_signum, _frame):
    global RUNNING
    RUNNING = False


def clamp(value, low, high):
    return max(low, min(high, value))


def connect():
    return pymysql.connect(**DB_CONFIG)


def ensure_devices(cur, now):
    devices = [
        ("DEV_001", "skin", "v1.0.3", "?????", 95, -48),
        ("DEV_002", "skin", "v1.0.3", "?????", 88, -53),
        ("ENV_001", "environment", "v1.0.1", "??", 91, -46),
    ]
    for device_id, device_type, firmware, location, battery, signal_strength in devices:
        cur.execute(
            """
            INSERT INTO devices
                (device_id, device_type, firmware_version, install_date, location,
                 status, battery_level, signal_strength, last_heartbeat, created_at, updated_at)
            VALUES
                (%s, %s, %s, CURDATE(), %s, 'online', %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                device_type = VALUES(device_type),
                firmware_version = VALUES(firmware_version),
                location = VALUES(location),
                status = 'online',
                battery_level = VALUES(battery_level),
                signal_strength = VALUES(signal_strength),
                last_heartbeat = VALUES(last_heartbeat),
                updated_at = VALUES(updated_at)
            """,
            (device_id, device_type, firmware, location, battery, signal_strength, now, now, now),
        )


def load_devices(cur):
    cur.execute(
        """
        SELECT device_id, device_type, location, battery_level, signal_strength
        FROM devices
        WHERE status = 'online' OR status IS NULL
        ORDER BY device_id
        """
    )
    rows = cur.fetchall()
    devices = []
    for row in rows:
        if isinstance(row, dict):
            devices.append(row)
        else:
            devices.append({
                "device_id": row[0],
                "device_type": row[1],
                "location": row[2],
                "battery_level": row[3],
                "signal_strength": row[4],
            })
    return devices


def skin_state_for(device):
    device_id = device["device_id"]
    if device_id not in SKIN_STATES:
        SKIN_STATES[device_id] = {
            "moisture": random.uniform(38.0, 58.0),
            "oiliness": random.uniform(28.0, 56.0),
            "temperature": random.uniform(32.0, 34.2),
            "battery": int(device.get("battery_level") or random.randint(82, 98)),
            "signal": int(device.get("signal_strength") or random.randint(-62, -38)),
        }
    return SKIN_STATES[device_id]


def env_state_for(device):
    device_id = device["device_id"]
    if device_id not in ENV_STATES:
        ENV_STATES[device_id] = {
            "device_id": device_id,
            "temperature": random.uniform(23.0, 28.0),
            "humidity": random.uniform(42.0, 66.0),
            "pm25": random.uniform(10.0, 36.0),
            "co2": random.uniform(500.0, 850.0),
            "battery": int(device.get("battery_level") or random.randint(82, 98)),
            "signal": int(device.get("signal_strength") or random.randint(-62, -38)),
            "location": device.get("location") or "演示区域",
        }
    else:
        ENV_STATES[device_id]["location"] = device.get("location") or ENV_STATES[device_id].get("location") or "演示区域"
    return ENV_STATES[device_id]


def step_skin_state(state):
    state["moisture"] = clamp(state["moisture"] + random.uniform(-1.2, 1.4), 30.0, 68.0)
    state["oiliness"] = clamp(state["oiliness"] + random.uniform(-1.0, 1.1), 20.0, 72.0)
    state["temperature"] = clamp(state["temperature"] + random.uniform(-0.18, 0.18), 31.5, 35.2)
    if random.random() < 0.04:
        state["battery"] = int(clamp(state["battery"] - 1, 35, 100))
    state["signal"] = int(clamp(state["signal"] + random.randint(-2, 2), -72, -35))


def step_env_state(state):
    hour = dt.datetime.now().hour
    day_wave = 1.2 if 10 <= hour <= 18 else -0.5
    state["temperature"] = clamp(state["temperature"] + random.uniform(-0.15, 0.18) + day_wave * 0.01, 20.0, 31.5)
    state["humidity"] = clamp(state["humidity"] + random.uniform(-0.8, 0.8), 35.0, 75.0)
    state["pm25"] = clamp(state["pm25"] + random.uniform(-2.5, 2.8), 5.0, 75.0)
    state["co2"] = clamp(state["co2"] + random.uniform(-22, 28), 420.0, 1300.0)
    if random.random() < 0.03:
        state["battery"] = int(clamp(state["battery"] - 1, 35, 100))
    state["signal"] = int(clamp(state["signal"] + random.randint(-2, 2), -72, -35))


def write_once(conn):
    now = dt.datetime.now().replace(microsecond=0)
    with conn.cursor() as cur:
        ensure_devices(cur, now)
        devices = load_devices(cur)
        skin_devices = [
            device for device in devices
            if (device.get("device_type") or "").lower() != "environment"
            and not str(device.get("device_id") or "").upper().startswith("ENV")
        ]
        env_devices = [
            device for device in devices
            if (device.get("device_type") or "").lower() == "environment"
            or str(device.get("device_id") or "").upper().startswith("ENV")
        ]

        for device in skin_devices:
            device_id = device["device_id"]
            state = skin_state_for(device)
            step_skin_state(state)
            cur.execute(
                """
                INSERT INTO skin_sensor_data
                    (device_id, moisture, oiliness, temperature, sensor_time, received_at,
                     client_ip, request_id, validated, quality_score, created_at)
                VALUES
                    (%s, %s, %s, %s, %s, %s, 'realtime-simulator', %s, 1, %s, %s)
                """,
                (
                    device_id,
                    int(round(state["moisture"])),
                    int(round(state["oiliness"])),
                    round(state["temperature"], 1),
                    now,
                    now,
                    "sim-{}".format(uuid.uuid4().hex[:16]),
                    round(random.uniform(0.91, 0.99), 2),
                    now,
                ),
            )
            cur.execute(
                """
                UPDATE devices
                SET status = 'online', battery_level = %s, signal_strength = %s,
                    last_heartbeat = %s, updated_at = %s
                WHERE device_id = %s
                """,
                (state["battery"], state["signal"], now, now, device_id),
            )

        for device in env_devices:
            state = env_state_for(device)
            step_env_state(state)
            cur.execute(
                """
                INSERT INTO environment_sensor_data
                    (device_id, temperature, humidity, pm25, co2, location, sensor_time,
                     received_at, client_ip, request_id, validated, quality_score, created_at)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s,
                     'realtime-simulator', %s, 1, %s, %s)
                """,
                (
                    state["device_id"],
                    round(state["temperature"], 1),
                    round(state["humidity"], 1),
                    int(round(state["pm25"])),
                    int(round(state["co2"])),
                    state["location"],
                    now,
                    now,
                    "sim-{}".format(uuid.uuid4().hex[:16]),
                    round(random.uniform(0.91, 0.99), 2),
                    now,
                ),
            )
            cur.execute(
                """
                UPDATE devices
                SET status = 'online', battery_level = %s, signal_strength = %s,
                    last_heartbeat = %s, updated_at = %s
                WHERE device_id = %s
                """,
                (state["battery"], state["signal"], now, now, state["device_id"]),
            )
    conn.commit()
    return now


def main():
    setup_logging()
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    logging.info("starting realtime MySQL simulator, interval=%ss", INTERVAL_SECONDS)

    conn = None
    while RUNNING:
        try:
            if conn is None:
                conn = connect()
            conn.ping(reconnect=True)
            written_at = write_once(conn)
            logging.info("inserted realtime rows at %s", written_at.strftime("%Y-%m-%d %H:%M:%S"))
            sleep_left = INTERVAL_SECONDS
            while RUNNING and sleep_left > 0:
                time.sleep(1)
                sleep_left -= 1
        except Exception:
            logging.exception("realtime simulator loop failed; reconnecting soon")
            try:
                if conn is not None:
                    conn.close()
            except Exception:
                pass
            conn = None
            time.sleep(5)

    try:
        if conn is not None:
            conn.close()
    finally:
        logging.info("stopped realtime MySQL simulator")


if __name__ == "__main__":
    main()
