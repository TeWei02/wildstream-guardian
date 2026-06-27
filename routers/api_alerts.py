"""警報 API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database.models import Alert, Station
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import get_db

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("")
def list_alerts(
    station_id: int = Query(None),
    alert_type: str = Query(None),
    severity: str = Query(None),
    is_read: bool = Query(None),
    limit: int = Query(50),
    db: Session = Depends(get_db),
):
    q = db.query(Alert)
    if station_id:
        q = q.filter(Alert.station_id == station_id)
    if alert_type:
        q = q.filter(Alert.alert_type == alert_type)
    if severity:
        q = q.filter(Alert.severity == severity)
    if is_read is not None:
        q = q.filter(Alert.is_read == is_read)
    q = q.order_by(desc(Alert.created_at)).limit(limit)
    alerts = q.all()

    result = []
    for a in alerts:
        station = db.query(Station).filter(Station.id == a.station_id).first()
        result.append({
            "id": a.id, "station_id": a.station_id,
            "station_name": station.name if station else "",
            "alert_type": a.alert_type, "severity": a.severity,
            "message": a.message, "sensor_value": a.sensor_value,
            "threshold_value": a.threshold_value, "is_read": a.is_read,
            "created_at": a.created_at.isoformat(),
        })
    return {"alerts": result, "count": len(result)}


@router.put("/{alert_id}/read")
def mark_read(alert_id: int, db: Session = Depends(get_db)):
    a = db.query(Alert).filter(Alert.id == alert_id).first()
    if not a:
        raise HTTPException(404, "警報不存在")
    a.is_read = True
    db.commit()
    return {"ok": True}


@router.put("/read-all")
def mark_all_read(db: Session = Depends(get_db)):
    db.query(Alert).filter(Alert.is_read == False).update({"is_read": True})
    db.commit()
    return {"ok": True}
