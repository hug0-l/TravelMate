"""TravelMate — FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from src.travelmate.config import settings
from src.travelmate.database import engine
from src.travelmate.models import Base
from src.travelmate.routers import auth, trips, days, activities, geocode, share, members, ws, expenses, memories, guest, pois, admin, files


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: dispose engine
    await engine.dispose()


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads", check_dir=False), name="uploads")

app.include_router(auth.router)
app.include_router(trips.router)
app.include_router(days.router)
app.include_router(activities.router)
app.include_router(geocode.router)
app.include_router(share.router)
app.include_router(members.router)
app.include_router(ws.router)
app.include_router(expenses.router)
app.include_router(memories.router)
app.include_router(guest.router)
app.include_router(pois.router)
app.include_router(files.router)
app.include_router(admin.router)
