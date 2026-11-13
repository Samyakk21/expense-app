"""API routes for the expense splitter toolkit (Vercel serverless).

Core business logic is delegated to the same ExpenseManager / balances /
simplify_debts modules used by the legacy code.
"""

from typing import Dict, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.manager import ExpenseManager
from app.balances import compute_balances
from app.simplify_debts import simplify_debts

router = APIRouter()

# Single in-memory manager (same design as original legacy api.py)
manager = ExpenseManager()


# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------
class UserRequest(BaseModel):
    user_id: int
    name: str


class UserResponse(BaseModel):
    id: int
    name: str


class ExpenseRequest(BaseModel):
    payer_id: int
    amount: float
    splits: Dict[int, float]


class ExpenseResponse(BaseModel):
    id: int
    payer_id: int
    payer_name: str
    amount: float
    splits: Dict[int, float]


class BalanceResponse(BaseModel):
    user: str
    balance: float


class SettlementResponse(BaseModel):
    from_user: str
    to_user: str
    amount: float


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------
@router.post("/users", response_model=UserResponse, status_code=201)
def add_user(user: UserRequest):
    try:
        manager.add_user(user.user_id, user.name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"id": user.user_id, "name": user.name}


@router.get("/users", response_model=List[UserResponse])
def list_users():
    return [{"id": u.id, "name": u.name} for u in manager.list_users()]


@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    if user_id not in manager.users:
        raise HTTPException(status_code=404, detail="User not found")
    for exp in manager.list_expenses():
        if exp.payer.id == user_id or any(u.id == user_id for u in exp.splits):
            raise HTTPException(
                status_code=400,
                detail="Cannot delete user with associated expenses",
            )
    del manager.users[user_id]
    return None


# ---------------------------------------------------------------------------
# Expenses
# ---------------------------------------------------------------------------
@router.post("/expenses", response_model=ExpenseResponse, status_code=201)
def add_expense(expense: ExpenseRequest):
    try:
        created = manager.add_expense(
            payer_id=expense.payer_id,
            amount=expense.amount,
            splits=expense.splits,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "id": created.id,
        "payer_id": created.payer.id,
        "payer_name": created.payer.name,
        "amount": created.amount,
        "splits": {str(u.id): amt for u, amt in created.splits.items()},
    }


@router.get("/expenses", response_model=List[ExpenseResponse])
def list_expenses():
    out = []
    for exp in manager.list_expenses():
        out.append(
            {
                "id": exp.id,
                "payer_id": exp.payer.id,
                "payer_name": exp.payer.name,
                "amount": exp.amount,
                "splits": {str(u.id): amt for u, amt in exp.splits.items()},
            }
        )
    return out


@router.delete("/expenses/{expense_id}", status_code=204)
def delete_expense(expense_id: int):
    for idx, exp in enumerate(manager.expenses):
        if exp.id == expense_id:
            manager.expenses.pop(idx)
            return None
    raise HTTPException(status_code=404, detail="Expense not found")


# ---------------------------------------------------------------------------
# Balances & settlements
# ---------------------------------------------------------------------------
@router.get("/balances", response_model=List[BalanceResponse])
def get_balances():
    balances = compute_balances(manager.list_expenses())
    return [
        {"user": user.name, "balance": round(amount, 2)}
        for user, amount in balances.items()
    ]


@router.get("/settlements", response_model=List[SettlementResponse])
def get_settlements():
    balances = compute_balances(manager.list_expenses())
    transactions = simplify_debts(balances)
    return [
        {
            "from_user": debtor.name,
            "to_user": creditor.name,
            "amount": round(amount, 2),
        }
        for debtor, creditor, amount in transactions
    ]
