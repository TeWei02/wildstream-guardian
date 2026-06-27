"""儀表板 KPI 聚合 API"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone, timedelta
from database.models import Station, SensorData, Alert
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import get_db

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("")
def dashboard_kpi(db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)

    # 監測站統計
    total_stations = db.query(func.count(Station.id)).scalar()
    online_stations = db.query(func.count(Station.id)).filter(Station.status == "online").scalar()

    # 最新數據時間
    latest_data = db.query(func.max(SensorData.recorded_at)).scalar()

    # 未讀警報
    unread_alerts = db.query(func.count(Alert.id)).filter(Alert.is_read == False).scalar()

    # 各站最新數據（用於卡片）
    stations = db.query(Station).all()
    station_snapshots = []
    for s in stations:
        latest = db.query(SensorData).filter(
            SensorData.station_id == s.id
        ).order_by(SensorData.recorded_at.desc()).first()
        snapshot = {
            "station_id": s.id, "station_name": s.name,
            "status": s.status, "river_name": s.river_name,
        }
        if latest:
            snapshot.update({
                "temperature": latest.temperature, "ph": latest.ph,
                "turbidity": latest.turbidity, "dissolved_oxygen": latest.dissolved_oxygen,
                "battery": latest.battery,
                "recorded_at": latest.recorded_at.isoformat(),
            })
        else:
            snapshot.update({"temperature": None, "ph": None, "turbidity": None, "dissolved_oxygen": None, "battery": None, "recorded_at": None})
        station_snapshots.append(snapshot)

    # 24 小時警報趨勢
    alert_trend = []
    for h in range(24, -1, -1):
        t = now - timedelta(hours=h)
        t_start = t.replace(minute=0, second=0, microsecond=0)
        t_end = t_start + timedelta(hours=1)
        count = db.query(func.count(Alert.id)).filter(
            Alert.created_at >= t_start, Alert.created_at < t_end
        ).scalar()
        alert_trend.append({"hour": t_start.isoformat(), "count": count})

    return {
        "total_stations": total_stations,
        "online_stations": online_stations,
        "latest_data_at": latest_data.isoformat() if latest_data else None,
        "unread_alerts": unread_alerts,
        "station_snapshots": station_snapshots,
        "alert_trend": alert_trend,
    }
