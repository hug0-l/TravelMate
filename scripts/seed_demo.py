"""Seed a demo user with a sample Japan trip."""

import asyncio
from datetime import date, timedelta, time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.travelmate.auth.jwt import hash_password
from src.travelmate.database import async_session, engine
from src.travelmate.models import Base

from src.travelmate.models.user import User
from src.travelmate.models.trip import Trip, TripMember
from src.travelmate.models.day import Day
from src.travelmate.models.activity import Activity, ActivityCategory
from src.travelmate.models.expense import Expense, ExpenseCategory, Split


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as db:
        result = await db.execute(select(User).where(User.email == "demo@japan.com"))
        existing = result.scalar_one_or_none()
        if existing:
            print("Demo account already exists")
            return

        user = User(
            email="demo@japan.com",
            name="旅人小明",
            hashed_password=hash_password("japan123"),
        )
        db.add(user)
        await db.flush()

        trip = Trip(
            title="2025 東京賞楓之旅",
            description="期待已久的東京賞楓行程，包含河口湖一日遊！",
            start_date=date(2025, 11, 10),
            end_date=date(2025, 11, 16),
            destination_country="日本",
            destination_tz_offset=9,
            visibility="shared",
            planned_budget=80000,
        )
        db.add(trip)
        await db.flush()

        member = TripMember(trip_id=trip.id, user_id=user.id, role="owner")
        db.add(member)

        days_data = [
            {"date": date(2025, 11, 10), "title": "Day 1 - 抵達東京", "order_index": 0},
            {"date": date(2025, 11, 11), "title": "Day 2 - 淺草＆晴空塔", "order_index": 1},
            {"date": date(2025, 11, 12), "title": "Day 3 - 河口湖一日遊", "order_index": 2},
            {"date": date(2025, 11, 13), "title": "Day 4 - 澀谷＆原宿", "order_index": 3},
            {"date": date(2025, 11, 14), "title": "Day 5 - 銀座＆六本木", "order_index": 4},
            {"date": date(2025, 11, 15), "title": "Day 6 - 自由活動", "order_index": 5},
            {"date": date(2025, 11, 16), "title": "Day 7 - 返程", "order_index": 6},
        ]
        days = []
        for d in days_data:
            day = Day(trip_id=trip.id, **d)
            db.add(day)
            days.append(day)
        await db.flush()

        activities_data = [
            {"day_idx": 0, "title": "松山機場出發", "category": "transport", "start_time": time(6, 30), "end_time": time(10, 30), "notes": "搭乘虎航 IT 200"},
            {"day_idx": 0, "title": "成田機場 → 上野", "category": "transport", "start_time": time(11, 0), "end_time": time(12, 30), "notes": "Skyliner"},
            {"day_idx": 0, "title": "Check-in 飯店", "category": "accommodation", "start_time": time(14, 0), "end_time": time(15, 0)},
            {"day_idx": 0, "title": "阿美橫町逛街", "category": "shopping", "start_time": time(15, 30), "end_time": time(18, 0)},
            {"day_idx": 0, "title": "一蘭拉麵（上野店）", "category": "food", "start_time": time(18, 30), "end_time": time(19, 30)},
            {"day_idx": 1, "title": "淺草寺參拜", "category": "attraction", "start_time": time(9, 0), "end_time": time(11, 0)},
            {"day_idx": 1, "title": "仲見世通逛街", "category": "shopping", "start_time": time(11, 0), "end_time": time(12, 30)},
            {"day_idx": 1, "title": "晴空塔展望台", "category": "attraction", "start_time": time(14, 0), "end_time": time(16, 0)},
            {"day_idx": 1, "title": "敘敘苑燒肉（晴空塔店）", "category": "food", "start_time": time(18, 0), "end_time": time(20, 0)},
            {"day_idx": 2, "title": "新宿搭高速巴士", "category": "transport", "start_time": time(7, 0), "end_time": time(9, 30), "notes": "前往河口湖"},
            {"day_idx": 2, "title": "河口湖纜車", "category": "attraction", "start_time": time(10, 0), "end_time": time(12, 0)},
            {"day_idx": 2, "title": "ほうとう不動（午餐）", "category": "food", "start_time": time(12, 30), "end_time": time(13, 30)},
            {"day_idx": 2, "title": "河口湖紅葉迴廊", "category": "attraction", "start_time": time(14, 0), "end_time": time(16, 0)},
            {"day_idx": 3, "title": "明治神宮", "category": "attraction", "start_time": time(9, 0), "end_time": time(11, 0)},
            {"day_idx": 3, "title": "原宿竹下通", "category": "shopping", "start_time": time(11, 30), "end_time": time(13, 0)},
            {"day_idx": 3, "title": "Shibuya Sky 展望台", "category": "attraction", "start_time": time(17, 0), "end_time": time(18, 30), "notes": "傍晚時段看夕陽"},
            {"day_idx": 3, "title": "澀谷居酒屋", "category": "food", "start_time": time(19, 0), "end_time": time(21, 0)},
            {"day_idx": 4, "title": "築地市場（早餐）", "category": "food", "start_time": time(8, 0), "end_time": time(10, 0)},
            {"day_idx": 4, "title": "銀座逛街", "category": "shopping", "start_time": time(10, 30), "end_time": time(13, 0)},
            {"day_idx": 4, "title": "TeamLab Borderless", "category": "attraction", "start_time": time(15, 0), "end_time": time(17, 0), "notes": "麻布台 Hills"},
            {"day_idx": 5, "title": "自由活動", "category": "other", "start_time": time(9, 0)},
            {"day_idx": 6, "title": "退房", "category": "other", "start_time": time(10, 0)},
            {"day_idx": 6, "title": "成田機場 → 台灣", "category": "flight", "start_time": time(14, 0), "end_time": time(17, 0)},
        ]
        for a in activities_data:
            day_idx = a.pop("day_idx")
            cat_name = a.pop("category").upper()
            activity = Activity(
                day_id=days[day_idx].id,
                category=getattr(ActivityCategory, cat_name, ActivityCategory.OTHER),
                **a,
            )
            db.add(activity)
        await db.flush()

        # Tokyo
        expense1 = Expense(
            trip_id=trip.id,
            title="虎航 IT200 機票",
            amount=12500,
            category=ExpenseCategory.TRANSPORT,
            paid_by=user.id,
            date=date(2025, 11, 10),
        )
        db.add(expense1)
        await db.flush()

        expense2 = Expense(
            trip_id=trip.id,
            title="上野飯店 6 晚",
            amount=36000,
            category=ExpenseCategory.ACCOMMODATION,
            paid_by=user.id,
            date=date(2025, 11, 10),
        )
        db.add(expense2)
        await db.flush()

        expense3 = Expense(
            trip_id=trip.id,
            title="晴空塔門票 x2",
            amount=4200,
            category=ExpenseCategory.ACTIVITY,
            paid_by=user.id,
            date=date(2025, 11, 11),
        )
        db.add(expense3)

        await db.commit()
        print(f"Seeded: demo@japan.com / japan123")
        print(f"Trip: {trip.title} ({trip.id})")


if __name__ == "__main__":
    asyncio.run(seed())
