"""數據導出 API (CSV/JSON)"""
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
import csv
import io
from database.models import SensorData, Station
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import get_db

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("")
def export_data(
    station_id: int = Query(None),
    format: str = Query("csv"),
    hours: int = Query(168),
    db: Session = Depends(get_db),
):
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    q = db.query(SensorData).filter(SensorData.recorded_at >= since)
    if station_id:
        q = q.filter(SensorData.station_id == station_id)
    rows = q.order_by(SensorData.recorded_at).all()

    if format == "json":
        data = []
        for r in rows:
            station = db.query(Station).filter(Station.id == r.station_id).first()
            data.append({
                "station_name": station.name if station else "",
                "station_code": station.code if station else "",
                "recorded_at": r.recorded_at.isoformat(),
                "temperature": r.temperature, "ph": r.ph,
                "turbidity": r.turbidity, "dissolved_oxygen": r.dissolved_oxygen,
                "conductivity": r.conductivity, "ammonia_nitrogen": r.ammonia_nitrogen,
                "total_phosphorus": r.total_phosphorus, "battery": r.battery,
                "signal_strength": r.signal_strength,
            })
        return JSONResponse(content={"data": data, "count": len(data)})

    # CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "station_name", "station_code", "recorded_at",
        "temperature", "ph", "turbidity", "dissolved_oxygen",
        "conductivity", "ammonia_nitrogen", "total_phosphorus",
        "battery", "signal_strength",
    ])
    for r in rows:
        station = db.query(Station).filter(Station.id == r.station_id).first()
        writer.writerow([
            station.name if station else "",
            station.code if station else "",
            r.recorded_at.isoformat(),
            r.temperature, r.ph, r.turbidity, r.dissolved_oxygen,
            r.conductivity, r.ammonia_nitrogen, r.total_phosphorus,
            r.battery, r.signal_strength,
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=wildstream_export.csv"},
    )
