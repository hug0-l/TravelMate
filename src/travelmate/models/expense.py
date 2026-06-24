from datetime import date, datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import Date, Enum, Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.travelmate.models.base import Base, TimestampMixin, uuid_pk


class ExpenseCategory(str, PyEnum):
    FOOD = "food"
    TRANSPORT = "transport"
    ACCOMMODATION = "accommodation"
    ACTIVITY = "activity"
    SHOPPING = "shopping"
    OTHER = "other"


class Expense(Base, TimestampMixin):
    __tablename__ = "expenses"

    id: Mapped[str] = uuid_pk()
    trip_id: Mapped[str] = mapped_column(ForeignKey("trips.id", ondelete="CASCADE"))
    activity_id: Mapped[str | None] = mapped_column(ForeignKey("activities.id", ondelete="SET NULL"), nullable=True)
    paid_by: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200))
    category: Mapped[ExpenseCategory] = mapped_column(
        Enum(ExpenseCategory, name="expense_category"),
        default=ExpenseCategory.OTHER,
    )
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(3), default="TWD")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    date: Mapped[date] = mapped_column(Date, default=lambda: datetime.now(timezone.utc).date())

    # relationships
    trip = relationship("Trip", back_populates="expenses")
    payer = relationship("User", back_populates="paid_expenses")
    splits = relationship("Split", back_populates="expense", lazy="selectin", cascade="all, delete-orphan")


class Split(Base, TimestampMixin):
    __tablename__ = "splits"
    __table_args__ = (UniqueConstraint("expense_id", "user_id", name="uq_expense_split"),)

    id: Mapped[str] = uuid_pk()
    expense_id: Mapped[str] = mapped_column(ForeignKey("expenses.id", ondelete="CASCADE"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    share_amount: Mapped[float] = mapped_column(Float)
    settled: Mapped[bool] = mapped_column(default=False)

    # relationships
    expense = relationship("Expense", back_populates="splits")
    user = relationship("User", back_populates="splits")
