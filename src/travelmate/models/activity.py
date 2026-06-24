from datetime import time
from enum import Enum as PyEnum

from sqlalchemy import Enum, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.travelmate.models.base import Base, TimestampMixin, uuid_pk


class ActivityCategory(str, PyEnum):
    TRANSPORT = "transport"
    FOOD = "food"
    ATTRACTION = "attraction"
    SHOPPING = "shopping"
    ACCOMMODATION = "accommodation"
    OTHER = "other"
    FLIGHT = "flight"
    TRAIN = "train"
    BUS = "bus"
    FERRY = "ferry"


class Activity(Base, TimestampMixin):
    __tablename__ = "activities"

    id: Mapped[str] = uuid_pk()
    day_id: Mapped[str] = mapped_column(ForeignKey("days.id", ondelete="CASCADE"))
    location_id: Mapped[str | None] = mapped_column(ForeignKey("locations.id", ondelete="SET NULL"), nullable=True)
    title: Mapped[str] = mapped_column(String(200))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    end_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    transport_mode: Mapped[str | None] = mapped_column(String(50), nullable=True)  # flight/train/bus/ferry/car
    from_location_id: Mapped[str | None] = mapped_column(ForeignKey("locations.id", ondelete="SET NULL"), nullable=True)
    to_location_id: Mapped[str | None] = mapped_column(ForeignKey("locations.id", ondelete="SET NULL"), nullable=True)
    category: Mapped[ActivityCategory] = mapped_column(
        Enum(ActivityCategory, name="activity_category"),
        default=ActivityCategory.OTHER,
    )
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    # relationships
    day = relationship("Day", back_populates="activities")
    location = relationship("Location", back_populates="activities", lazy="selectin")
    from_location = relationship("Location", foreign_keys=[from_location_id], lazy="selectin")
    to_location = relationship("Location", foreign_keys=[to_location_id], lazy="selectin")
