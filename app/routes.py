"""API routes for the expense splitter toolkit.

Persistence is delegated to ``app.store`` (Supabase when configured, otherwise
in-memory). The pure domain logic in ``app.balances`` and ``app.simplify_debts``
is used unchanged.
"""

from typing import Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app import store
from app.balances import compute_balances
from app.simplify_debts import simplify_debts

router = APIRouter()


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
        store.add_user(user.user_id, user.name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"id": user.user_id, "name": user.name}


@router.get("/users", response_model=List[UserResponse])
def list_users():
    return [{"id": u.id, "name": u.name} for u in store.list_users()]


@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    try:
        store.delete_user(user_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return None


# ---------------------------------------------------------------------------
# Expenses
# ---------------------------------------------------------------------------
@router.post("/expenses", response_model=ExpenseResponse, status_code=201)
def add_expense(expense: ExpenseRequest):
    try:
        created = store.add_expense(
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
    return [
        {
            "id": exp.id,
            "payer_id": exp.payer.id,
            "payer_name": exp.payer.name,
            "amount": exp.amount,
            "splits": {str(u.id): amt for u, amt in exp.splits.items()},
        }
        for exp in store.list_expenses()
    ]


@router.delete("/expenses/{expense_id}", status_code=204)
def delete_expense(expense_id: int):
    try:
        store.delete_expense(expense_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return None


# ---------------------------------------------------------------------------
# Balances & settlements (core logic unchanged)
# ---------------------------------------------------------------------------
@router.get("/balances", response_model=List[BalanceResponse])
def get_balances():
    balances = compute_balances(store.list_expenses())
    return [
        {"user": user.name, "balance": round(amount, 2)}
        for user, amount in balances.items()
    ]


@router.get("/settlements", response_model=List[SettlementResponse])
def get_settlements():
    balances = compute_balances(store.list_expenses())
    transactions = simplify_debts(balances)
    return [
        {
            "from_user": debtor.name,
            "to_user": creditor.name,
            "amount": round(amount, 2),
        }
        for debtor, creditor, amount in transactions
    ]
