"""Expense and budget routes."""

from datetime import date
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.travelmate.auth.deps import get_current_user
from src.travelmate.database import get_db
from src.travelmate.models.expense import Expense, Split, ExpenseCategory
from src.travelmate.models.trip import Trip, TripMember
from src.travelmate.models.user import User
from src.travelmate.schemas.expense import (
    BudgetSummary,
    ExpenseCreate,
    ExpenseResponse,
    ExpenseUpdate,
    SplitResponse,
)

router = APIRouter(tags=["expenses"])


async def _verify_trip_access(trip_id: str, user: User, db: AsyncSession):
    result = await db.execute(
        select(Trip).join(TripMember).where(Trip.id == trip_id, TripMember.user_id == user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Trip not found")


@router.get("/api/trips/{trip_id}/expenses", response_model=list[ExpenseResponse])
async def list_expenses(
    trip_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _verify_trip_access(trip_id, user, db)
    result = await db.execute(
        select(Expense)
        .options(selectinload(Expense.splits))
        .where(Expense.trip_id == trip_id)
        .order_by(Expense.date.desc())
    )
    expenses = result.scalars().all()
    return await _enrich_expenses(expenses, db)


@router.post("/api/trips/{trip_id}/expenses", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    trip_id: str,
    body: ExpenseCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _verify_trip_access(trip_id, user, db)
    expense = Expense(
        trip_id=trip_id,
        title=body.title,
        category=body.category,
        amount=body.amount,
        currency=body.currency,
        notes=body.notes,
        date=body.date or date.today(),
        activity_id=body.activity_id,
        paid_by=body.paid_by,
    )
    db.add(expense)
    await db.flush()

    # Create equal splits if requested
    if body.split_with:
        share = round(body.amount / (len(body.split_with) + 1), 2)
        # Payer's share
        payer_split = Split(expense_id=expense.id, user_id=body.paid_by, share_amount=share)
        db.add(payer_split)
        # Others' shares
        for uid in body.split_with:
            db.add(Split(expense_id=expense.id, user_id=uid, share_amount=share))

    await db.commit()
    await db.refresh(expense)
    result = await db.execute(
        select(Expense).options(selectinload(Expense.splits)).where(Expense.id == expense.id)
    )
    enriched = await _enrich_expenses([result.scalar_one()], db)
    return enriched[0]


@router.put("/api/expenses/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: str,
    body: ExpenseUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Expense).options(selectinload(Expense.splits)).where(Expense.id == expense_id)
    )
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    await _verify_trip_access(expense.trip_id, user, db)

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(expense, field, value)
    await db.commit()
    await db.refresh(expense)
    enriched = await _enrich_expenses([expense], db)
    return enriched[0]


@router.delete("/api/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    expense_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Expense).where(Expense.id == expense_id))
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    await _verify_trip_access(expense.trip_id, user, db)
    await db.delete(expense)
    await db.commit()


@router.get("/api/trips/{trip_id}/budget-summary", response_model=BudgetSummary)
async def get_budget_summary(
    trip_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _verify_trip_access(trip_id, user, db)
    result = await db.execute(
        select(Expense)
        .options(selectinload(Expense.splits))
        .where(Expense.trip_id == trip_id)
    )
    expenses = result.scalars().all()

    # Get all members
    members_result = await db.execute(
        select(User).join(TripMember).where(TripMember.trip_id == trip_id)
    )
    members = {m.id: m.name for m in members_result.scalars().all()}

    total = sum(e.amount for e in expenses)
    by_cat: dict[str, float] = {}
    paid: dict[str, float] = defaultdict(float)
    share: dict[str, float] = defaultdict(float)

    for e in expenses:
        by_cat[e.category.value] = by_cat.get(e.category.value, 0) + e.amount
        paid[e.paid_by] += e.amount
        for s in e.splits:
            share[s.user_id] += s.share_amount

    all_ids = set(list(paid.keys()) + list(share.keys()))
    per_person = {}
    balances = []
    for uid in all_ids:
        name = members.get(uid, "Unknown")
        p = paid.get(uid, 0)
        s = share.get(uid, 0)
        per_person[name] = round(p - s, 2)
        balances.append({"user_id": uid, "name": name, "paid": round(p, 2), "share": round(s, 2), "balance": round(p - s, 2)})

    return BudgetSummary(
        total_expenses=round(total, 2),
        by_category={k: round(v, 2) for k, v in by_cat.items()},
        per_person=per_person,
        balances=balances,
    )


@router.put("/api/splits/{split_id}/settle", status_code=status.HTTP_200_OK)
async def settle_split(
    split_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Split).where(Split.id == split_id))
    split = result.scalar_one_or_none()
    if not split:
        raise HTTPException(status_code=404, detail="Split not found")
    split.settled = not split.settled
    await db.commit()
    return {"settled": split.settled}


async def _enrich_expenses(expenses: list[Expense], db: AsyncSession) -> list[ExpenseResponse]:
    """Attach user names to expense responses."""
    user_ids = set()
    for e in expenses:
        user_ids.add(e.paid_by)
        for s in e.splits:
            user_ids.add(s.user_id)

    users = {}
    if user_ids:
        result = await db.execute(select(User).where(User.id.in_(user_ids)))
        users = {u.id: u.name for u in result.scalars().all()}

    responses = []
    for e in expenses:
        responses.append(ExpenseResponse(
            id=e.id,
            trip_id=e.trip_id,
            activity_id=e.activity_id,
            paid_by=e.paid_by,
            paid_by_name=users.get(e.paid_by, "Unknown"),
            title=e.title,
            category=e.category,
            amount=e.amount,
            currency=e.currency,
            notes=e.notes,
            date=e.date,
            splits=[
                SplitResponse(
                    id=s.id,
                    user_id=s.user_id,
                    user_name=users.get(s.user_id, "Unknown"),
                    share_amount=s.share_amount,
                    settled=s.settled,
                )
                for s in (e.splits or [])
            ],
            created_at=e.created_at,
        ))
    return responses
