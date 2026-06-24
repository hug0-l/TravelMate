# ✈️ TravelMate

> 旅程規劃夥伴 — 行程編輯器、地圖視覺化、多人協作分帳

## 🏗️ 系統架構

```
TravelMate/
├── src/travelmate/             # FastAPI 後端
│   ├── auth/                   # JWT 認證 + bcrypt 密碼
│   ├── models/                 # SQLAlchemy ORM (9 個模型)
│   ├── schemas/                # Pydantic 請求/回應 schema
│   ├── routers/                # 11 個 REST API 路由
│   └── main.py                 # FastAPI app 工廠
├── frontend/                   # Vue 3 + TypeScript SPA
│   └── src/
│       ├── api/                # Axios API 客戶端
│       ├── components/         # 共用組件 (Skeleton/Empty/Error)
│       ├── stores/             # Pinia 狀態管理
│       ├── router/             # Vue Router (路由守衛)
│       ├── types/              # TypeScript 介面
│       └── views/              # 頁面組件
├── tests/                      # Pytest 非同步測試 (35 個)
├── alembic/                    # 資料庫遷移
└── pyproject.toml              # Python 依賴管理
```

## 🚀 快速開始

### 後端

```bash
# 建立虛擬環境並安裝
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# 設定環境變數（複製 .env.example → .env，填入 SECRET_KEY）
cp .env.example .env

# 執行資料庫遷移
alembic upgrade head

# 啟動 API 伺服器（自動重載）
uvicorn src.travelmate.main:app --reload --port 8000

# 執行測試
pytest tests/ -v
```

### 前端

```bash
cd frontend
npm install
npm run dev   # 啟動於 localhost:5173，代理 /api 到 :8000
```

開啟 **http://localhost:5173** ✈️

## 🗺️ API 一覽

### 認證
| Method | Endpoint | 說明 |
|--------|----------|------|
| POST | `/api/auth/register` | 註冊新用戶 |
| POST | `/api/auth/login` | 登入 |
| POST | `/api/auth/refresh` | 刷新 JWT token |

### 行程
| Method | Endpoint | 說明 |
|--------|----------|------|
| GET/POST | `/api/trips/` | 列出/建立行程 |
| GET/PUT/DELETE | `/api/trips/{id}` | 取得/更新/刪除行程 |
| GET | `/api/trips/share/{code}` | 公開分享頁 |

### 天數
| Method | Endpoint | 說明 |
|--------|----------|------|
| GET/POST | `/api/trips/{id}/days` | 列出/建立天數 |
| PUT/DELETE | `/api/days/{id}` | 更新/刪除天數 |
| PUT | `/api/trips/{id}/days/reorder` | 拖曳排序天數 |

### 活動
| Method | Endpoint | 說明 |
|--------|----------|------|
| GET/POST | `/api/days/{id}/activities` | 列出/建立活動 |
| PUT/DELETE | `/api/activities/{id}` | 更新/刪除活動 |
| PUT | `/api/days/{id}/activities/reorder` | 拖曳排序活動 |

### 預算與分帳
| Method | Endpoint | 說明 |
|--------|----------|------|
| GET/POST | `/api/trips/{id}/expenses` | 列出/建立開銷 |
| PUT/DELETE | `/api/expenses/{id}` | 更新/刪除開銷 |
| GET | `/api/trips/{id}/budget-summary` | 預算總覽（分類+人均） |
| PUT | `/api/splits/{id}/settle` | 標記分帳結清 |

### 其他
| Method | Endpoint | 說明 |
|--------|----------|------|
| GET/POST | `/api/trips/{id}/memories` | 列出/建立回憶 |
| PUT/DELETE | `/api/memories/{id}` | 更新/刪除回憶 |
| GET | `/api/geocode/search` | 地點搜尋（OpenStreetMap） |
| WS | `/ws/trip/{id}` | 即時協作 WebSocket |
| GET/POST/DELETE | `/api/trips/{id}/members` | 成員管理 |

## 🧪 測試狀態

**35/35 測試通過** ✅

```bash
pytest tests/ -v
# TypeScript 檢查
cd frontend && npx vue-tsc --noEmit
```

## 📦 技術棧

| 層級 | 技術 |
|------|------|
| 後端框架 | FastAPI + SQLAlchemy 2.0 (async) |
| 資料庫 | SQLite（開發）/ PostgreSQL（生產） |
| 認證 | JWT（python-jose + bcrypt） |
| 前端 | Vue 3 + Composition API + TypeScript |
| 樣式 | Tailwind CSS v4 |
| 地圖 | Leaflet + OpenStreetMap |
| 狀態管理 | Pinia |
| HTTP | Axios |
| 拖曳 | vue-draggable-plus |

## 🔒 資安措施

- 密碼 bcrypt 雜湊儲存
- JWT access token 1 小時有效期 + refresh token 30 天
- WebSocket 認證透過首條訊息（非 query string）
- CORS 可透過環境變數設定
- SQLAlchemy ORM 參數化查詢（無 SQL injection）
- 輸入驗證：EmailStr、密碼最小 8 字元
- 所有 CRUD API 需 JWT 驗證

## 🆕 Guest 加入（免註冊）

行程建立者在分享 Modal 可看到 **6 位數加入碼**，訪客到 `/join` 輸入：
1. 行程 ID（從分享 Modal 複製）
2. 6 位數加入碼
3. 暱稱

即可獲得 24 小時有效的 Guest Token，無需註冊。

## ⚙️ 管理後台

路徑 `/admin`，僅 `is_admin=true` 的用戶可存取：
- 📊 系統統計（用戶/行程/活動/開銷/回憶數量）
- 👥 用戶管理（列表、切換管理員權限）
- 📅 近期行程列表

## 🔐 資安防護

| 機制 | 說明 |
|------|------|
| 密碼儲存 | bcrypt 雜湊 |
| JWT | access token 1h + refresh token 30d |
| Guest token | 24h 有效期，僅可存取特定行程 |
| WebSocket | 首條訊息認證（非 query string） |
| CORS | 可透過 `CORS_ORIGINS` 環境變數設定 |
| SQL 注入 | SQLAlchemy ORM 參數化查詢 |
| 輸入驗證 | EmailStr、密碼 8 字元、形狀驗證 |

## 📋 MVP 路線圖

- **Phase 1** ✅ 核心行程編輯器 + 地圖 + 分享 + 預算分帳 + POI + Guest 加入 + 管理後台
- **Phase 2** 🔲 PWA 離線支援 + 改善即時協作
- **Phase 3** 🔲 旅程回憶與照片時間軸 + AI 行程推薦

## 🌐 UI 語言
即可獲得 24 小時有效的 Guest Token，無需註冊。

## ⚙️ 管理後台

路徑 `/admin`，僅 `is_admin=true` 的用戶可存取：
- 📊 系統統計（用戶/行程/活動/開銷/回憶數量）
- 👥 用戶管理（列表、切換管理員權限）
- 📅 近期行程列表

## 🔐 資安防護

| 機制 | 說明 |
|------|------|
| 密碼儲存 | bcrypt 雜湊 |
| JWT | access token 1h + refresh token 30d |
| Guest token | 24h 有效期，僅可存取特定行程 |
| WebSocket | 首條訊息認證（非 query string） |
| CORS | 可透過 `CORS_ORIGINS` 環境變數設定 |
| SQL 注入 | SQLAlchemy ORM 參數化查詢 |
| 輸入驗證 | EmailStr、密碼 8 字元、形狀驗證 |

## 📋 MVP 路線圖## 🌐 UI 語言

繁體中文（Traditional Chinese）

## 📄 授權

MIT License
