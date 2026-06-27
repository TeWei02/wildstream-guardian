"""
異常檢測引擎
"""
from datetime import datetime, timezone
from config import ANOMALY_THRESHOLDS, ALERT_TYPES
from database.models import Alert


def detect_anomalies(station_id: int, data: dict, db_session):
    """
    針對單筆傳感器數據進行異常檢測，自動生成警報。
    data: {temperature, ph, turbidity, dissolved_oxygen, battery, ...}
    返回: list of Alert objects
    """
    alerts = []
    thresholds = ANOMALY_THRESHOLDS

    # 濁度過高 → 污染警報
    turbidity = data.get("turbidity")
    if turbidity is not None and turbidity > thresholds["turbidity_high"]:
        alerts.append(Alert(
            station_id=station_id,
            alert_type="pollution",
            severity="critical",
            message=f"濁度異常升高 ({turbidity:.1f} NTU)，超過閾值 {thresholds['turbidity_high']} NTU，疑似污染事件",
            sensor_value=turbidity,
            threshold_value=thresholds["turbidity_high"],
        ))

    # pH 超出範圍
    ph = data.get("ph")
    if ph is not None:
        if ph < thresholds["ph_low"]:
            alerts.append(Alert(
                station_id=station_id,
                alert_type="abnormal_ph",
                severity="critical",
                message=f"pH 值過低 ({ph:.2f})，低於安全下限 {thresholds['ph_low']}",
                sensor_value=ph,
                threshold_value=thresholds["ph_low"],
            ))
        elif ph > thresholds["ph_high"]:
            alerts.append(Alert(
                station_id=station_id,
                alert_type="abnormal_ph",
                severity="warning",
                message=f"pH 值過高 ({ph:.2f})，超過安全上限 {thresholds['ph_high']}",
                sensor_value=ph,
                threshold_value=thresholds["ph_high"],
            ))

    # 溶氧過低
    do_val = data.get("dissolved_oxygen")
    if do_val is not None and do_val < thresholds["dissolved_oxygen_low"]:
        alerts.append(Alert(
            station_id=station_id,
            alert_type="low_oxygen",
            severity="warning",
            message=f"溶氧量過低 ({do_val:.1f} mg/L)，低於 {thresholds['dissolved_oxygen_low']} mg/L，可能影響水生生物",
            sensor_value=do_val,
            threshold_value=thresholds["dissolved_oxygen_low"],
        ))

    # 電量過低
    battery = data.get("battery")
    if battery is not None and battery < thresholds["battery_low"]:
        alerts.append(Alert(
            station_id=station_id,
            alert_type="low_battery",
            severity="warning",
            message=f"電池電量不足 ({battery:.0f}%)，請安排更換",
            sensor_value=battery,
            threshold_value=thresholds["battery_low"],
        ))

    return alerts
