from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict

from expenses import ExpenseManager
from balances import compute_balances
from simplify_debts import simplify_debts

app = FastAPI()

# CORS (robust dev setup)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

manager = ExpenseManager()


# ---------- REQUEST MODELS ----------
class UserRequest(BaseModel):
    name: str


class ExpenseRequest(BaseModel):
    payer_id: int
    amount: float
    splits: Dict[int, float]
    description: str = ""


# ---------- ROUTES ----------
@app.post("/users")
def add_user(user: UserRequest):
    try:
        new_user = manager.add_user(user.name)
        return {"id": new_user.id, "name": new_user.name}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/expenses")
def add_expense(exp: ExpenseRequest):
    try:
        manager.add_expense(exp.payer_id, exp.amount, exp.splits)
        return {"message": "Expense added"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/balances")
def get_balances():
    try:
        balances = compute_balances(manager.list_expenses())
        return {u.name: round(v, 2) for u, v in balances.items()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/settlements")
def get_settlements():
    try:
        balances = compute_balances(manager.list_expenses())
        tx = simplify_debts(balances)

        return [
            {"from": d.name, "to": c.name, "amount": round(a, 2)}
            for d, c, a in tx
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))