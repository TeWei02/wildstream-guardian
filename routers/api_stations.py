"""監測站 CRUD API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database.models import Station
from config import BRAND_COLORS
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import get_db

router = APIRouter(prefix="/api/stations", tags=["stations"])


@router.get("")
def list_stations(
    status: str = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Station)
    if status:
        q = q.filter(Station.status == status)
    stations = q.order_by(Station.name).all()
    return {"stations": [s_to_dict(s) for s in stations]}


@router.get("/{station_id}")
def get_station(station_id: int, db: Session = Depends(get_db)):
    s = db.query(Station).filter(Station.id == station_id).first()
    if not s:
        raise HTTPException(404, "監測站不存在")
    return s_to_dict(s)


@router.post("")
def create_station(data: dict, db: Session = Depends(get_db)):
    s = Station(
        name=data.get("name"),
        code=data.get("code"),
        river_name=data.get("river_name", ""),
        latitude=data.get("latitude", 0.0),
        longitude=data.get("longitude", 0.0),
        device_id=data.get("device_id", ""),
        description=data.get("description", ""),
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return s_to_dict(s)


@router.put("/{station_id}")
def update_station(station_id: int, data: dict, db: Session = Depends(get_db)):
    s = db.query(Station).filter(Station.id == station_id).first()
    if not s:
        raise HTTPException(404, "監測站不存在")
    for field in ["name", "code", "river_name", "latitude", "longitude", "device_id", "status", "description"]:
        if field in data:
            setattr(s, field, data[field])
    db.commit()
    db.refresh(s)
    return s_to_dict(s)


@router.delete("/{station_id}")
def delete_station(station_id: int, db: Session = Depends(get_db)):
    s = db.query(Station).filter(Station.id == station_id).first()
    if not s:
        raise HTTPException(404, "監測站不存在")
    db.delete(s)
    db.commit()
    return {"ok": True}


def s_to_dict(s: Station):
    return {
        "id": s.id, "name": s.name, "code": s.code,
        "river_name": s.river_name, "latitude": s.latitude, "longitude": s.longitude,
        "device_id": s.device_id, "status": s.status, "description": s.description,
        "created_at": s.created_at.isoformat() if s.created_at else None,
        "updated_at": s.updated_at.isoformat() if s.updated_at else None,
    }
