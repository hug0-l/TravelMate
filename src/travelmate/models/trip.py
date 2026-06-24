import uuid
from datetime import date
from enum import Enum as PyEnum

from sqlalchemy import Date, Enum, Integer, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.travelmate.models.base import Base, TimestampMixin, uuid_pk


class TripVisibility(str, PyEnum):
    PRIVATE = "private"
    SHARED = "shared"
    PUBLIC = "public"


class Trip(Base, TimestampMixin):
    __tablename__ = "trips"

    id: Mapped[str] = uuid_pk()
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    cover_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    share_code: Mapped[str] = mapped_column(
        String(36), unique=True, index=True, default=lambda: str(uuid.uuid4())[:8]
    )
    visibility: Mapped[TripVisibility] = mapped_column(
        Enum(TripVisibility, name="trip_visibility"),
        default=TripVisibility.PRIVATE,
    )
    # Country & timezone
    origin_country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    destination_country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    destination_tz_offset: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="Hours from UTC, e.g. +9 for Japan")

    # relationships
    members = relationship("TripMember", back_populates="trip", lazy="selectin", cascade="all, delete-orphan")
    days = relationship("Day", back_populates="trip", lazy="selectin", cascade="all, delete-orphan", order_by="Day.order_index")
    expenses = relationship("Expense", back_populates="trip", lazy="selectin", cascade="all, delete-orphan")
    memories = relationship("Memory", back_populates="trip", lazy="selectin", cascade="all, delete-orphan")


class TripMember(Base, TimestampMixin):
    __tablename__ = "trip_members"
    __table_args__ = (UniqueConstraint("trip_id", "user_id", name="uq_trip_member"),)

    id: Mapped[str] = uuid_pk()
    trip_id: Mapped[str] = mapped_column(ForeignKey("trips.id", ondelete="CASCADE"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(20), default="owner")  # owner | editor | viewer

    # relationships
    trip = relationship("Trip", back_populates="members")
    user = relationship("User", back_populates="trip_memberships")
