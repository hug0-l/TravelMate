from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.travelmate.models.base import Base, TimestampMixin, uuid_pk


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = uuid_pk()
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_admin: Mapped[bool] = mapped_column(default=False)

    # relationships
    trip_memberships = relationship("TripMember", back_populates="user", lazy="selectin")
    paid_expenses = relationship("Expense", back_populates="payer", lazy="selectin")
    splits = relationship("Split", back_populates="user", lazy="selectin")
    memories = relationship("Memory", back_populates="user", lazy="selectin")
    assigned_activities = relationship("Activity", back_populates="assignee", foreign_keys="Activity.assignee_id")
    activity_comments = relationship("ActivityComment", back_populates="user", lazy="selectin")
    packing_items = relationship("PackingItem", back_populates="user", lazy="selectin")
    created_polls = relationship("Poll", back_populates="creator", lazy="selectin")
    poll_votes = relationship("PollVote", back_populates="user", lazy="selectin")
