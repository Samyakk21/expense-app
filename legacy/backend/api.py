from fastapi import FastAPI
from expenses import ExpenseManager
from balances import compute_balances
from simplify_debts import simplify_debts
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
manager = ExpenseManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from pydantic import BaseModel
from typing import Dict

class ExpenseRequest(BaseModel):
    payer_id: int
    amount: float
    splits: Dict[int, float]



@app.post("/users")
def add_user(user_id: int, name: str):
    manager.add_user(user_id, name)
    return {"message": "User added"}

@app.post("/expenses")
def add_expense(expense: ExpenseRequest):
    manager.add_expense(
        payer_id=expense.payer_id,
        amount=expense.amount,
        splits=expense.splits
    )
    return {"message": "Expense added"}


@app.get("/balances")
def get_balances():
    balances = compute_balances(manager.list_expenses())

    return {
        user.name: round(amount, 2)
        for user, amount in balances.items()
    }


@app.get("/settlements")
def get_settlements():
    balances = compute_balances(manager.list_expenses())
    transactions = simplify_debts(balances)

    return [
        {
            "from": debtor.name,
            "to": creditor.name,
            "amount": round(amount, 2)
        }
        for debtor, creditor, amount in transactions
    ]