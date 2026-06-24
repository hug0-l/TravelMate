from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.travelmate.models.base import Base, TimestampMixin, uuid_pk


class Day(Base, TimestampMixin):
    __tablename__ = "days"

    id: Mapped[str] = uuid_pk()
    trip_id: Mapped[str] = mapped_column(ForeignKey("trips.id", ondelete="CASCADE"))
    date: Mapped[date] = mapped_column(Date)
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    # relationships
    trip = relationship("Trip", back_populates="days")
    activities = relationship(
        "Activity", back_populates="day", lazy="selectin",
        cascade="all, delete-orphan", order_by="Activity.order_index",
    )
