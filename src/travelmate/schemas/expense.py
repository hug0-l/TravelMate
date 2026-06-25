from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from src.travelmate.models.expense import ExpenseCategory


class ExpenseCreate(BaseModel):
    title: str
    category: ExpenseCategory = ExpenseCategory.OTHER
    amount: float
    currency: str = "TWD"
    notes: Optional[str] = None
    date: Optional[date] = None
    activity_id: Optional[str] = None
    paid_by: str
    split_with: list[str] = []  # user_ids to split equally


class ExpenseUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[ExpenseCategory] = None
    amount: Optional[float] = None
    notes: Optional[str] = None


class SplitResponse(BaseModel):
    id: str
    user_id: str
    user_name: str = ""
    share_amount: float
    settled: bool

    model_config = ConfigDict(from_attributes=True)


class ExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    trip_id: str
    activity_id: Optional[str] = None
    paid_by: str
    paid_by_name: str = ""
    title: str
    category: ExpenseCategory
    amount: float
    currency: str
    notes: Optional[str] = None
    date: date
    splits: list[SplitResponse] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None


class BudgetSummary(BaseModel):
    total_expenses: float = 0
    by_category: dict[str, float] = {}
    per_person: dict[str, float] = {}
    balances: list[dict] = []  # [{user_id, name, paid, share, balance}]

class SettleUpTransaction(BaseModel):
    from_user_id: str
    from_user_name: str
    to_user_id: str
    to_user_name: str
    amount: float


class SettleUpResponse(BaseModel):
    transactions: list[SettleUpTransaction]
    total_balance: dict[str, float]  # user_id -> net balance
