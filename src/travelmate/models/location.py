from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.travelmate.models.base import Base, TimestampMixin, uuid_pk


class Location(Base, TimestampMixin):
    __tablename__ = "locations"

    id: Mapped[str] = uuid_pk()
    name: Mapped[str] = mapped_column(String(255))
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    place_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # relationships
    activities = relationship("Activity", foreign_keys="Activity.location_id", back_populates="location", lazy="selectin")
