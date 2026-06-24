# TravelMate — 完整設定指南

## 前置需求

- Python **≥ 3.13**
- Node.js **≥ 18**
- 在專案根目錄 `TravelMate/` 執行指令

---

## 1. 後端設定

```bash
# 建立虛擬環境
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 安裝依賴（包含 dev 工具）
pip install -e ".[dev]"
```

### 環境變數

```bash
# 複製範例設定檔
cp .env.example .env

# 編輯 .env，填入安全性金鑰
# 產生金鑰: python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

`.env` 內容範例：
```env
SECRET_KEY=your-generated-secret-key-here
DEBUG=False
DATABASE_URL=sqlite+aiosqlite:///./travelmate.db
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 資料庫遷移

```bash
alembic upgrade head
```

### 啟動 API 伺服器

```bash
uvicorn src.travelmate.main:app --reload --port 8000
# 或: python main.py
```

API 位於 **http://localhost:8000**，自動 API 文件在 **http://localhost:8000/docs**

---

## 2. 前端設定

```bash
cd frontend
npm install
```

### 開發模式

```bash
npm run dev
```

前端位於 **http://localhost:5173**（Vite 反向代理 API 到 :8000）

### 生產建置

```bash
npm run build
```

---

## 3. 同時執行（開發用）

開啟 **兩個終端機**：

| 終端機 | 指令 |
|---------|------|
| 後端 | `source .venv/bin/activate && uvicorn src.travelmate.main:app --reload --port 8000` |
| 前端 | `cd frontend && npm run dev` |

---

## 4. 測試

```bash
# 後端測試（從專案根目錄）
pytest tests/ -v

# TypeScript 型別檢查
cd frontend && npx vue-tsc --noEmit

# 前端建置檢查
cd frontend && npm run build
```

---

## 5. 專案結構

```
TravelMate/
├── src/travelmate/             # FastAPI 後端
│   ├── auth/                   # JWT + bcrypt 認證
│   ├── models/                 # SQLAlchemy ORM 模型
│   ├── schemas/                # Pydantic schema
│   ├── routers/                # REST API 路由
│   ├── ws.py                   # WebSocket 連線管理
│   ├── config.py               # 設定（支援 .env）
│   ├── database.py             # 資料庫引擎與 session
│   └── main.py                 # FastAPI app 入口
├── frontend/                   # Vue 3 + TypeScript 前端
│   └── src/
│       ├── api/                # Axios API 客戶端
│       ├── components/         # 共用 UI 組件
│       ├── stores/             # Pinia 狀態儲存
│       ├── router/             # Vue Router 路由
│       ├── types/              # TypeScript 型別定義
│       └── views/              # 頁面組件
├── tests/                      # Pytest 測試 (35 個)
├── alembic/                    # 資料庫遷移腳本
├── .env.example                # 環境變數範例
├── .gitignore
├── pyproject.toml              # Python 專案設定
└── README.md
```

---

## 6. 資料庫遷移指令

```bash
# 建立新的遷移
alembic revision --autogenerate -m "description"

# 套用遷移
alembic upgrade head

# 回退一步
alembic downgrade -1

# 查看狀態
alembic current
```

---

## 7. 常見問題

### SQLite 與 PostgreSQL

開發環境預設使用 SQLite。要切換到 PostgreSQL：

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/travelmate
```

並安裝 asyncpg：
```bash
pip install asyncpg
```

### 前端代理設定

前端 `vite.config.ts` 已設定 `/api` 代理到 `http://localhost:8000`，開發時不需要手動設定 CORS。
