# TravelMate — AI Agent Guide

## 專案概述

TravelMate 是一個旅程規劃協作平台：
- **後端**: FastAPI + SQLAlchemy 2.0 (async) + SQLite/PostgreSQL
- **前端**: Vue 3 + Composition API + TypeScript + Vite
- **樣式**: Tailwind CSS v4
- **地圖**: Leaflet + OpenStreetMap
- **狀態**: Pinia
- **HTTP**: Axios
- **拖曳**: vue-draggable-plus

## 目錄結構

```
TravelMate/
├── src/travelmate/             # FastAPI 後端
│   ├── auth/                   # JWT + bcrypt 認證
│   ├── models/                 # SQLAlchemy ORM (9+ 模型)
│   ├── schemas/                # Pydantic schema
│   ├── routers/                # REST API 路由
│   ├── ws.py                   # WebSocket 連線管理
│   ├── config.py               # 設定（支援 .env）
│   ├── database.py             # 資料庫引擎與 session
│   └── main.py                 # FastAPI app 入口
├── frontend/                   # Vue 3 + TypeScript
│   └── src/
│       ├── api/                # Axios API 客戶端
│       ├── components/         # 共用 UI 組件
│       ├── stores/             # Pinia store
│       │   ├── auth.ts         # 認證 store
│       │   ├── trip.ts         # 行程資料 store
│       │   └── ws.ts           # WebSocket store
│       ├── router/             # Vue Router
│       ├── types/              # TypeScript 型別
│       └── views/              # 頁面組件
│           ├── DashboardView.vue
│           ├── TripView.vue
│           ├── LoginView.vue
│           ├── RegisterView.vue
│           ├── SharedTripView.vue
│           ├── AdminView.vue
│           └── GuestJoinView.vue
├── tests/                      # Pytest 測試 (35+ 個)
├── alembic/                    # DB 遷移
└── .env.example
```

## 開發慣例

### 後端

1. **模型定義**: 在 `models/` 使用 SQLAlchemy 2.0 Mapped 語法
   - 所有模型繼承 `Base, TimestampMixin`
   - 主鍵使用 `uuid_pk()` helper
   - 外鍵明確指定 `ondelete`（CASCADE / SET NULL）
   - relationship 使用 `back_populates`（不要用 backref）
   - 多個 FK 指向同一表時，relationship 需指定 `foreign_keys=[...]`

2. **Schema 定義**: 在 `schemas/` 使用 Pydantic v2
   - `*Create`：建立用，全部 Optional 或設預設值
   - `*Update`：更新用，全部 Optional
   - `*Response`：回應用，`model_config = ConfigDict(from_attributes=True)`

3. **路由**: 在 `routers/`
   - 需認證的 endpoint 加 `user: User = Depends(get_current_user)`
   - 管理員 endpoint 加 `admin: User = Depends(require_admin)`
   - 使用 `HTTPException` 回傳錯誤
   - 資源訪問前先 verify trip membership

4. **JWT 認證**:
   - `create_access_token(user_id)` — 1h 有效期，type=access
   - `create_refresh_token(user_id)` — 30d 有效期，type=refresh
   - Guest 使用 `create_guest_token(trip_id, nickname)` — 24h

### 前端

1. **型別定義**: 在 `types/index.ts`
   - 與後端 response schema 一一對應
   - 共用常數（CATEGORY_LABELS / CATEGORY_COLORS）放在型別檔

2. **API 呼叫**: 在 `api/client.ts`
   - 使用 Axios 實例，baseURL 為 `/api`
   - 401 自動清除 token 並跳轉登入頁
   - 分功能區塊：authApi / tripApi / dayApi / activityApi / expenseApi / poiApi 等

3. **狀態管理**: 在 `stores/`
   - 使用 Pinia composition API
   - 異步操作需 try/catch
   - 樂觀更新（如拖曳排序）需實作 rollback

4. **頁面組件**: 在 `views/`
   - 使用 `<script setup lang="ts">`
   - ref 在 template 中自動 unwrap（不要加 .value）
   - 所有 API 呼叫應有載入狀態和錯誤處理
   - 動態 import 優先使用頂層 static import

5. **共用組件**: 在 `components/`
   - `SkeletonLoader` — 骨架屏（lines / hasAvatar / hasImage）
   - `EmptyState` — 空狀態（icon / title / description / actionText + @action）
   - `ErrorState` — 錯誤狀態（message / retryText + @retry）

### 樣式

- 使用 Tailwind CSS utility classes
- 主色：indigo-600（漸層 from-indigo-600 to-purple-600）
- 卡片 hover：`hover:-translate-y-0.5 hover:shadow-xl`
- 響應式：`md:` breakpoint，手機用底欄導航 `md:hidden`

## 資料庫

- 開發環境 SQLite + aiosqlite
- 所有模型在 `models/__init__.py` export
- `main.py` 的 `lifespan` 自動建立表格
- 修改模型後：刪除 `travelmate.db` 重啟 server

## 測試

```bash
# 後端
pytest tests/ -v

# TS 型別檢查
cd frontend && npx vue-tsc --noEmit

# 前端建置驗證
cd frontend && npm run build
```

## API Endpoints 一覽

### 認證
| Method | Path | Auth | 說明 |
|--------|------|------|------|
| POST | `/api/auth/register` | ❌ | email+name+password → JWT |
| POST | `/api/auth/login` | ❌ | email+password → JWT |
| POST | `/api/auth/refresh` | ❌ | refresh_token → 新 JWT |

### 行程
| Method | Path | Auth | 說明 |
|--------|------|------|------|
| GET/POST | `/api/trips/` | ✅ | 列表/建立 |
| GET/PUT/DELETE | `/api/trips/{id}` | ✅ | 讀取/更新/刪除 |
| GET | `/api/trips/share/{code}` | ❌ | 公開分享 |

### 天數
| Method | Path | Auth | 說明 |
|--------|------|------|------|
| GET/POST | `/api/trips/{id}/days` | ✅ | 列表/建立 |
| PUT/DELETE | `/api/days/{id}` | ✅ | 更新/刪除 |
| PUT | `/api/trips/{id}/days/reorder` | ✅ | 排序 |

### 活動
| Method | Path | Auth | 說明 |
|--------|------|------|------|
| GET/POST | `/api/days/{id}/activities` | ✅ | 列表/建立 |
| PUT/DELETE | `/api/activities/{id}` | ✅ | 更新/刪除 |
| PUT | `/api/days/{id}/activities/reorder` | ✅ | 排序 |

### 預算
| Method | Path | Auth | 說明 |
|--------|------|------|------|
| GET/POST | `/api/trips/{id}/expenses` | ✅ | 列表/建立 |
| PUT/DELETE | `/api/expenses/{id}` | ✅ | 更新/刪除 |
| GET | `/api/trips/{id}/budget-summary` | ✅ | 總覽（含 planned_budget） |
| PUT | `/api/splits/{id}/settle` | ✅ | 結清 split |

### Guest 加入
| Method | Path | Auth | 說明 |
|--------|------|------|------|
| POST | `/api/trips/join` | ❌ | trip_id + join_code + nickname → guest_token |
| GET | `/api/trips/{id}/join-info` | ❌ | 查行程名稱 |

### 管理後台
| Method | Path | Auth | 說明 |
|--------|------|------|------|
| GET | `/api/admin/stats` | Admin | 系統統計 |
| GET | `/api/admin/users` | Admin | 用戶列表 |
| PUT | `/api/admin/users/{id}/toggle-admin` | Admin | 切換管理員 |
| GET | `/api/admin/trips/recent` | Admin | 近期行程 |

### 其他
| Method | Path | Auth | 說明 |
|--------|------|------|------|
| GET/POST | `/api/trips/{id}/memories` | ✅ | 回憶列表/建立 |
| GET/POST | `/api/trips/{id}/pois` | ✅ | POI 列表/建立 |
| PUT/DELETE | `/api/pois/{id}` | ✅ | 更新/刪除 POI |
| GET | `/api/geocode/search?q=` | ❌ | 地點搜尋 |
| WS | `/ws/trip/{id}` | ✅ | 即時協作（首條 auth 訊息） |
| GET/POST/DELETE | `/api/trips/{id}/members` | ✅ | 成員管理 |

## 常見陷阱

1. **`.value` in template**: Vue 3 的 `ref` 在 template 中自動 unwrap，**不要**寫 `trip.value`，只需 `trip`
2. **`&amp;&amp;` in template**: HTML entity 問題，Vue template 要用 `&&`
3. **Activity FK ambiguity**: `Location` 被 Activity 的三個 FK 參考（location_id / from_location_id / to_location_id），所有 relationship 必須指定 `foreign_keys`
4. **重複 import**: 不要用 `const { default: api } = await import(...)`，用頂層 static `import api`
5. **watch on route params**: `const tripId = route.params.id` 需要 `let` + `watch`，因為同個 component 被複用
6. **delete travelmate.db**: 修改 model 後需刪 DB 讓 server 自動重建
