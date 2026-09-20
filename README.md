# 野溪守護者 Wildstream Guardian

[![Python](https://img.shields.io/badge/Python-3.10+-%233776AB?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-%23009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3-%23003B57?logo=sqlite)](https://www.sqlite.org/)
[![Deploy](https://img.shields.io/badge/Deploy-Render-%2346E3B7?logo=render)](https://render.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

全端河川水質監測平台，提供水質資料視覺化、異常警示與回饋功能，支援多語言介面（繁中 / 簡中 / English / 日本語）。

## 功能

| 功能 | 說明 |
|------|------|
| 水質監測儀表板 | 監測站資料視覺化與即時圖表 |
| 地圖檢視 | 以地圖呈現監測站分布 |
| 異常偵測與警示 | 自動偵測異常數值並即時通知 |
| 資料匯出 | 匯出歷史監測資料 |
| 使用者回饋 | 意見回饋與商店頁面 |
| 多語言支援 | zh-Hant / zh-Hans / en / ja |

## 技術棧

| 層級 | 技術 |
|------|------|
| Backend | FastAPI (Python) + SQLite |
| Frontend | Jinja2 Templates + JavaScript + CSS |
| 部署 | Render (render.yaml) |

## 快速開始

```bash
pip install -r requirements.txt
python main.py
```

啟動後開啟 http://localhost:8000 即可瀏覽。

## 專案結構

```
wildstream-guardian/
├── main.py               # 應用程式入口
├── config.py             # 設定
├── database/             # 資料模型與初始化
├── routers/              # API 路由（dashboard / alerts / export / feedback / shop / stations）
├── services/             # 商業邏輯（異常偵測等）
├── templates/            # 頁面模板（含 i18n 多語言）
├── static/               # 前端資源
└── render.yaml           # Render 部署設定
```

## License

MIT
