"""Poll model for trip voting."""

from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.travelmate.models.base import Base, TimestampMixin, uuid_pk


class Poll(Base, TimestampMixin):
    __tablename__ = "polls"

    id: Mapped[str] = uuid_pk()
    trip_id: Mapped[str] = mapped_column(ForeignKey("trips.id", ondelete="CASCADE"))
    creator_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    question: Mapped[str] = mapped_column(String(300))
    is_closed: Mapped[bool] = mapped_column(Boolean, default=False)

    # relationships
    trip = relationship("Trip", back_populates="polls")
    creator = relationship("User", back_populates="created_polls")
    options = relationship("PollOption", back_populates="poll", lazy="selectin", cascade="all, delete-orphan")


class PollOption(Base, TimestampMixin):
    __tablename__ = "poll_options"

    id: Mapped[str] = uuid_pk()
    poll_id: Mapped[str] = mapped_column(ForeignKey("polls.id", ondelete="CASCADE"))
    label: Mapped[str] = mapped_column(String(200))

    poll = relationship("Poll", back_populates="options")
    votes = relationship("PollVote", back_populates="option", lazy="selectin", cascade="all, delete-orphan")


class PollVote(Base, TimestampMixin):
    __tablename__ = "poll_votes"
    __table_args__ = (UniqueConstraint("option_id", "user_id", name="uq_poll_vote"),)

    id: Mapped[str] = uuid_pk()
    option_id: Mapped[str] = mapped_column(ForeignKey("poll_options.id", ondelete="CASCADE"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    option = relationship("PollOption", back_populates="votes")
    user = relationship("User", back_populates="poll_votes")
