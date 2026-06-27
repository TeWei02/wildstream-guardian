"""
野溪守護者 (Wildstream Guardian) — 設定檔
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'wildstream.db')}"

BRAND_COLORS = {
    "river_green": "#1A6B5A",
    "stream_blue": "#3A9BD5",
    "eco_green": "#5DAD65",
    "alert_orange": "#E8833A",
    "dark_bg": "#0F1923",
    "card_bg": "#1A2332",
    "text_primary": "#E4E8EC",
    "text_secondary": "#8B95A5",
    "border": "#2A3A4A",
}

ANOMALY_THRESHOLDS = {
    "turbidity_high": 100.0,
    "ph_low": 6.0,
    "ph_high": 9.0,
    "battery_low": 15.0,
    "dissolved_oxygen_low": 4.0,
}

ALERT_TYPES = {
    "pollution": "污染警報",
    "abnormal_ph": "pH 異常",
    "low_battery": "低電量",
    "low_oxygen": "溶氧過低",
}

PARAM_TYPES = [
    "temperature", "ph", "turbidity", "dissolved_oxygen",
    "conductivity", "ammonia_nitrogen", "total_phosphorus",
    "battery", "signal_strength",
]

PARAM_LABELS = {
    "temperature": "水溫 (°C)",
    "ph": "pH 值",
    "turbidity": "濁度 (NTU)",
    "dissolved_oxygen": "溶氧 (mg/L)",
    "conductivity": "導電度 (µS/cm)",
    "ammonia_nitrogen": "氨氮 (mg/L)",
    "total_phosphorus": "總磷 (mg/L)",
    "battery": "電量 (%)",
    "signal_strength": "訊號強度 (dBm)",
}
