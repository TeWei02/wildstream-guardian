"""傳感器數據 API + NB-IoT 數據接收"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timezone, timedelta
from database.models import SensorData, Station
from services.anomaly import detect_anomalies
from config import PARAM_LABELS
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import get_db

router = APIRouter(prefix="/api/data", tags=["data"])


@router.get("")
def query_data(
    station_id: int = Query(None),
    param: str = Query(None),
    hours: int = Query(24),
    db: Session = Depends(get_db),
):
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    q = db.query(SensorData).filter(SensorData.recorded_at >= since)
    if station_id:
        q = q.filter(SensorData.station_id == station_id)
    q = q.order_by(SensorData.recorded_at)
    rows = q.all()

    result = []
    for r in rows:
        d = {
            "id": r.id, "station_id": r.station_id,
            "recorded_at": r.recorded_at.isoformat(),
            "temperature": r.temperature, "ph": r.ph,
            "turbidity": r.turbidity, "dissolved_oxygen": r.dissolved_oxygen,
            "conductivity": r.conductivity, "ammonia_nitrogen": r.ammonia_nitrogen,
            "total_phosphorus": r.total_phosphorus, "battery": r.battery,
            "signal_strength": r.signal_strength,
        }
        if param:
            d = {"station_id": d["station_id"], "recorded_at": d["recorded_at"], param: d.get(param)}
        result.append(d)

    return {"data": result, "count": len(result), "hours": hours}


@router.post("/ingest")
def ingest_data(data: dict, db: Session = Depends(get_db)):
    """
    NB-IoT 數據接收端點。
    自動進行異常檢測，若有異常則生成警報。
    """
    station_id = data.get("station_id")
    station = db.query(Station).filter(Station.id == station_id).first()
    if not station:
        raise HTTPException(404, "監測站不存在")

    recorded_at = data.get("recorded_at")
    if recorded_at:
        try:
            recorded_at = datetime.fromisoformat(recorded_at)
        except ValueError:
            recorded_at = datetime.now(timezone.utc)
    else:
        recorded_at = datetime.now(timezone.utc)

    sd = SensorData(
        station_id=station_id,
        temperature=data.get("temperature"),
        ph=data.get("ph"),
        turbidity=data.get("turbidity"),
        dissolved_oxygen=data.get("dissolved_oxygen"),
        conductivity=data.get("conductivity"),
        ammonia_nitrogen=data.get("ammonia_nitrogen"),
        total_phosphorus=data.get("total_phosphorus"),
        battery=data.get("battery"),
        signal_strength=data.get("signal_strength"),
        recorded_at=recorded_at,
    )
    db.add(sd)
    db.flush()

    # 異常檢測
    anomaly_data = {
        "turbidity": sd.turbidity, "ph": sd.ph,
        "dissolved_oxygen": sd.dissolved_oxygen, "battery": sd.battery,
    }
    alerts = detect_anomalies(station_id, anomaly_data, db)
    for alert in alerts:
        db.add(alert)

    db.commit()
    return {
        "ok": True,
        "data_id": sd.id,
        "alerts_generated": len(alerts),
        "alert_types": [a.alert_type for a in alerts],
    }
