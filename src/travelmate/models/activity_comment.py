"""Activity comment model."""

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.travelmate.models.base import Base, TimestampMixin, uuid_pk


class ActivityComment(Base, TimestampMixin):
    __tablename__ = "activity_comments"

    id: Mapped[str] = uuid_pk()
    activity_id: Mapped[str] = mapped_column(ForeignKey("activities.id", ondelete="CASCADE"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    content: Mapped[str] = mapped_column(Text)

    # relationships
    activity = relationship("Activity", back_populates="comments")
    user = relationship("User", back_populates="activity_comments")
