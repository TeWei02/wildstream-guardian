"""
種子數據 — 5 站 × 28 條/站（每 6 小時 × 7 天）= 140 條傳感器數據，含模擬異常事件
"""
import random
import math
from datetime import datetime, timezone, timedelta
from database.models import (
    Base, Station, SensorData, Alert, Product, Feedback,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL, ANOMALY_THRESHOLDS

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(Station).count() > 0:
        db.close()
        return

    # ── 監測站 ──
    stations_data = [
        {"name": "上游水源站", "code": "WS-UP01", "river_name": "翡翠溪", "lat": 24.95, "lon": 121.35, "device_id": "NB-IoT-001"},
        {"name": "中游監測站", "code": "WS-MD01", "river_name": "翡翠溪", "lat": 24.88, "lon": 121.42, "device_id": "NB-IoT-002"},
        {"name": "下游匯流站", "code": "WS-DN01", "river_name": "翡翠溪", "lat": 24.80, "lon": 121.50, "device_id": "NB-IoT-003"},
        {"name": "工業區監測站", "code": "WS-ID01", "river_name": "工業排水道", "lat": 24.85, "lon": 121.38, "device_id": "NB-IoT-004"},
        {"name": "生態保護站", "code": "WS-ECO1", "river_name": "生態保留區", "lat": 24.92, "lon": 121.33, "device_id": "NB-IoT-005"},
    ]
    stations = []
    for s in stations_data:
        st = Station(**s)
        db.add(st)
        stations.append(st)
    db.flush()

    # ── 傳感器數據 ──
    now = datetime.now(timezone.utc)
    anomaly_station = stations[3]  # 工業區監測站 — 模擬異常
    eco_station = stations[4]       # 生態保護站 — 優良水質

    for i in range(28):
        ts = now - timedelta(hours=(27 - i) * 6)

        for st in stations:
            # 基準值
            temp = round(22.0 + 3 * math.sin(i / 4.0) + random.uniform(-1.5, 1.5), 1)
            ph = round(7.3 + random.uniform(-0.3, 0.3), 2)
            turb = round(random.uniform(10, 40), 1)
            do_val = round(7.0 + random.uniform(-1.0, 1.0), 1)
            cond = round(250 + random.uniform(-30, 30), 1)
            nh3 = round(random.uniform(0.1, 0.5), 2)
            tp = round(random.uniform(0.02, 0.10), 2)
            batt = round(85 + random.uniform(-10, 10), 1)
            sig = round(-75 + random.uniform(-10, 5), 1)

            # 工業區異常事件
            if st.id == anomaly_station.id:
                if i == 8:   # 第 3 天深夜 — 污染
                    turb = 180.0
                    nh3 = 2.5
                    ph = 5.5
                elif i == 16:  # 第 5 天傍晚 — pH 異常
                    ph = 5.2
                elif i == 20:  # 第 6 天凌晨 — 低電量
                    batt = 10.0

            # 生態站優良水質
            if st.id == eco_station.id:
                turb = round(random.uniform(2, 10), 1)
                nh3 = round(random.uniform(0.01, 0.10), 2)
                do_val = round(8.0 + random.uniform(0, 0.5), 1)

            sd = SensorData(
                station_id=st.id,
                temperature=temp, ph=ph, turbidity=turb,
                dissolved_oxygen=do_val, conductivity=cond,
                ammonia_nitrogen=nh3, total_phosphorus=tp,
                battery=batt, signal_strength=sig,
                recorded_at=ts,
            )
            db.add(sd)

    # ── 警報（基於異常事件產生） ──
    alerts_to_seed = [
        {"station_id": anomaly_station.id, "alert_type": "pollution", "severity": "critical",
         "message": "工業區監測站檢測到濁度異常升高 (180 NTU)，疑似非法排放", "sensor_value": 180.0, "threshold_value": ANOMALY_THRESHOLDS["turbidity_high"]},
        {"station_id": anomaly_station.id, "alert_type": "abnormal_ph", "severity": "critical",
         "message": "工業區監測站 pH 值降至 5.2，遠低於安全範圍", "sensor_value": 5.2, "threshold_value": ANOMALY_THRESHOLDS["ph_low"]},
        {"station_id": anomaly_station.id, "alert_type": "low_battery", "severity": "warning",
         "message": "工業區監測站電池電量僅剩 10%，請盡快更換", "sensor_value": 10.0, "threshold_value": ANOMALY_THRESHOLDS["battery_low"]},
        {"station_id": stations[0].id, "alert_type": "low_battery", "severity": "info",
         "message": "上游水源站電池電量偏低 (18%)", "sensor_value": 18.0, "threshold_value": ANOMALY_THRESHOLDS["battery_low"]},
    ]
    for a in alerts_to_seed:
        db.add(Alert(**a))

    # ── 商城商品 ──
    products_data = [
        {"name": "便攜式水質檢測筆", "description": "pH/濁度/TDS 三合一，USB 充電", "price": 1280, "stock": 50, "category": "device"},
        {"name": "NB-IoT 傳感器模組", "description": "低功耗廣域傳輸，適用偏遠河段", "price": 3500, "stock": 20, "category": "device"},
        {"name": "太陽能充電板 (5W)", "description": "專為野溪監測站設計，IP67 防水", "price": 890, "stock": 100, "category": "accessory"},
        {"name": "濁度校準液套組", "description": "0 / 10 / 100 / 800 NTU 四點校準", "price": 450, "stock": 200, "category": "consumable"},
        {"name": "《河川生態守護手冊》", "description": "公民科學家入門指南，全彩印刷", "price": 320, "stock": 500, "category": "book"},
        {"name": "野溪守護者 T-shirt", "description": "純棉短袖，河川藍配色", "price": 590, "stock": 300, "category": "merch"},
    ]
    for p in products_data:
        db.add(Product(**p))

    # ── 用戶反饋 ──
    feedback_data = [
        {"user_name": "陳小華", "email": "chen@example.com", "category": "bug",
         "subject": "地圖頁面標記偏移", "message": "下游匯流站的標記在地圖上偏移約 200 公尺，請修正。"},
        {"user_name": "林大為", "email": "lin@example.com", "category": "feature",
         "subject": "建議新增降雨量顯示", "message": "希望能在儀表板整合中央氣象局雨量資料，便於判斷水質變化原因。"},
    ]
    for f in feedback_data:
        db.add(Feedback(**f))

    db.commit()
    db.close()
    print("✅ 種子數據寫入完成：5 站 × 28 條 = 140 筆傳感器數據 + 警報/商品/反饋")


if __name__ == "__main__":
    seed()
