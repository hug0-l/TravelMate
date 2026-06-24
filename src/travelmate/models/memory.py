from datetime import date

from sqlalchemy import Date, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.travelmate.models.base import Base, TimestampMixin, uuid_pk


class Memory(Base, TimestampMixin):
    __tablename__ = "memories"

    id: Mapped[str] = uuid_pk()
    trip_id: Mapped[str] = mapped_column(ForeignKey("trips.id", ondelete="CASCADE"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    photo_urls: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array of URLs
    date: Mapped[date] = mapped_column(Date)

    # relationships
    trip = relationship("Trip", back_populates="memories")
    user = relationship("User", back_populates="memories")
