"""頁面路由 — 11 個 HTML 頁面"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(tags=["pages"])

PAGES = [
    ("/", "dashboard.html", "儀表板"),
    ("/stations", "stations.html", "監測站管理"),
    ("/stations/{station_id}", "station_detail.html", "監測站詳情"),
    ("/realtime", "realtime.html", "實時數據"),
    ("/alerts", "alerts.html", "警報系統"),
    ("/export", "export.html", "數據導出"),
    ("/map", "map.html", "地圖顯示"),
    ("/history", "history.html", "歷史趨勢"),
    ("/devices", "devices.html", "設備管理"),
    ("/shop", "shop.html", "守護者商城"),
    ("/feedback", "feedback.html", "用戶反饋"),
]


def _render(request: Request, template_name: str):
    return templates.TemplateResponse(request=request, name=template_name)


def _make_handler(template_name: str):
    async def handler(request: Request):
        return _render(request, template_name)
    return handler


for path, template_name, title in PAGES:
    if "{station_id}" in path:
        # 动态路径需要特殊处理
        async def station_detail_handler(request: Request):
            return _render(request, "station_detail.html")
        router.get(path, response_class=HTMLResponse)(station_detail_handler)
    else:
        handler = _make_handler(template_name)
        router.get(path, response_class=HTMLResponse)(handler)
