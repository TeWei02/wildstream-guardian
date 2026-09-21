# 野溪守護者 Wildstream Guardian

[![Python](https://img.shields.io/badge/Python-3.10+-%233776AB?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-%23009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3-%23003B57?logo=sqlite)](https://www.sqlite.org/)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-%235DAD65?logo=githubpages)](https://tewei02.github.io/wildstream-guardian/)
[![PWA](https://img.shields.io/badge/PWA-offline%20ready-%233A9BD5)](https://tewei02.github.io/wildstream-guardian/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

全端河川水質監測平台，提供水質資料視覺化、異常警示與回饋功能，支援多語言介面（繁中 / 簡中 / English / 日本語）。

> **線上示範版**：<https://tewei02.github.io/wildstream-guardian/>

## 線上示範版

| 項目 | 內容 |
|------|------|
| 網址 | <https://tewei02.github.io/wildstream-guardian/> |
| 型態 | 純靜態前端，部署於 GitHub Pages（`docs/` 目錄），支援 PWA 離線安裝 |
| 資料 | 瀏覽器端即時模擬生成，可完整操作各項功能 |

### 資料聲明

線上示範版的所有監測數值（水溫、pH、濁度、溶氧、導電度、氨氮、總磷）、警報紀錄與設備狀態，皆由前端 JavaScript 依規則隨機生成，僅用於展示介面與互動流程；後端版本的種子資料同屬模擬資料。本專案不含任何真實測站量測結果，請勿作為水質判讀或決策依據。

## 功能

| 功能 | 說明 |
|------|------|
| 水質監測儀表板 | 監測站資料視覺化與即時圖表 |
| 監測站管理 | 測站新增、編輯、刪除與詳情檢視（示範資料） |
| 即時數據 | 多參數監測表格，30 秒週期更新（模擬微調） |
| 異常偵測與警示 | 濁度、pH、電量閾值判斷並產生警示紀錄 |
| 地圖檢視 | 以 Leaflet 地圖呈現監測站分布與最新讀值 |
| 歷史趨勢 | 多參數折線圖與統計摘要（最小 / 最大 / 平均值） |
| 資料匯出 | 依站點與日期區間匯出 CSV |
| NB-IoT 數據接收 | JSON 上行負載解析與異常檢測日誌（模擬通道） |
| 多語言支援 | zh-Hant / zh-Hans / en / ja |
| 離線安裝 | Service Worker 快取，可安裝為桌面 / 行動應用（PWA） |

## 技術棧

| 層級 | 技術 |
|------|------|
| Backend | FastAPI (Python) + SQLAlchemy + SQLite |
| Frontend | Jinja2 Templates + JavaScript + CSS |
| 線上示範版 | 原生 HTML / CSS / JavaScript + Leaflet 1.9.4 + Chart.js 4.4.0 + Service Worker |
| 部署 | GitHub Pages（靜態示範版）/ Render（`render.yaml`，後端完整版） |

## 快速開始

線上瀏覽（無需安裝）：

```
https://tewei02.github.io/wildstream-guardian/
```

本機執行後端完整版：

```bash
pip install -r requirements.txt
python main.py
```

啟動後開啟 <http://localhost:8000> 即可瀏覽。

## 專案結構

```
wildstream-guardian/
├── docs/                     # 靜態示範版（GitHub Pages 來源）
│   ├── index.html            # 單頁應用：儀表板 / 測站 / 即時 / 警報 / 匯出 / 地圖 / 趨勢 / 設備 / NB-IoT
│   ├── manifest.json         # PWA 應用資訊
│   ├── sw.js                 # Service Worker（離線快取）
│   ├── icons/                # PWA 圖示
│   └── vendor/               # 本地化前端依賴（Leaflet / Chart.js）
├── main.py                   # 應用程式入口
├── config.py                 # 設定
├── database/                 # 資料模型與種子資料
├── routers/                  # API 路由（dashboard / alerts / export / feedback / shop / stations）
├── services/                 # 商業邏輯（異常偵測等）
├── templates/                # 頁面模板（含 i18n 多語言）
├── static/                   # 前端資源
└── render.yaml               # Render 部署設定
```

## 授權

MIT License © 2026 Te-Wei Ko
