"""
野溪守護者 (Wildstream Guardian) — FastAPI 入口
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os, sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from config import DATABASE_URL, BRAND_COLORS
from database.models import Base

# ── 數據庫 ──
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ── FastAPI App ──
app = FastAPI(
    title="野溪守護者 Wildstream Guardian",
    description="全端河川水質監測系統",
    version="1.0.0",
)

# 靜態文件
static_dir = os.path.join(BASE_DIR, "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# ── 路由註冊 ──
from routers import api_stations, api_data, api_alerts, api_dashboard, api_export, api_shop, api_feedback, pages

app.include_router(api_stations.router)
app.include_router(api_data.router)
app.include_router(api_alerts.router)
app.include_router(api_dashboard.router)
app.include_router(api_export.router)
app.include_router(api_shop.router)
app.include_router(api_feedback.router)
app.include_router(pages.router)

# ── 歷史統計 API（inline） ──
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from datetime import datetime, timezone, timedelta
from database.models import SensorData, Station

stats_router = APIRouter(prefix="/api/stats", tags=["stats"])

@stats_router.get("")
def get_stats(
    station_id: int = Query(None),
    hours: int = Query(168),
    db: Session = Depends(get_db),
):
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    q = db.query(SensorData).filter(SensorData.recorded_at >= since)
    if station_id:
        q = q.filter(SensorData.station_id == station_id)
    rows = q.order_by(SensorData.recorded_at).all()

    params = ["temperature", "ph", "turbidity", "dissolved_oxygen", "conductivity", "ammonia_nitrogen", "total_phosphorus"]
    stats = {}
    for p in params:
        vals = [getattr(r, p) for r in rows if getattr(r, p) is not None]
        if vals:
            stats[p] = {
                "min": round(min(vals), 2),
                "max": round(max(vals), 2),
                "avg": round(sum(vals) / len(vals), 2),
                "count": len(vals),
            }
        else:
            stats[p] = {"min": None, "max": None, "avg": None, "count": 0}

    # 時間序列
    timeline = []
    for r in rows:
        timeline.append({
            "recorded_at": r.recorded_at.isoformat(),
            "temperature": r.temperature, "ph": r.ph,
            "turbidity": r.turbidity, "dissolved_oxygen": r.dissolved_oxygen,
            "conductivity": r.conductivity, "ammonia_nitrogen": r.ammonia_nitrogen,
            "total_phosphorus": r.total_phosphorus,
        })

    return {"stats": stats, "timeline": timeline, "hours": hours}

app.include_router(stats_router)

# ── 啟動 ──
if __name__ == "__main__":
    import uvicorn
    # 初始化數據庫
    Base.metadata.create_all(bind=engine)
    # 種子數據
    from database.seed import seed
    seed()
    uvicorn.run(app, host="0.0.0.0", port=8000)
