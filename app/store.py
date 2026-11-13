"""Storage layer for the expense splitter.

This module is the ONLY place that knows about persistence. It stores data in
Supabase (Postgres) when credentials are configured, and otherwise falls back to
the original in-memory ``ExpenseManager`` so local development works with zero
setup.

The core domain logic is unchanged and still lives in:
  - ``app/models.py``        (User, Expense)
  - ``app/manager.py``       (ExpenseManager validation)
  - ``app/balances.py``      (compute_balances)
  - ``app/simplify_debts.py``(simplify_debts)
"""

import os
from typing import Dict, List

from app.manager import ExpenseManager
from app.models import Expense, User

# Load a local .env file if python-dotenv is available (ignored on Vercel, which
# injects environment variables directly).
try:  # pragma: no cover - convenience only
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover
    pass

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip()
SUPABASE_KEY = (
    os.environ.get("SUPABASE_KEY")
    or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    or os.environ.get("SUPABASE_ANON_KEY")
    or ""
).strip()

USE_SUPABASE = bool(SUPABASE_URL and SUPABASE_KEY)

_client = None

# In-memory fallback (identical to the original behavior).
_memory = ExpenseManager()

if USE_SUPABASE:  # pragma: no cover - environment dependent
    print("[store] Persistence backend: Supabase")
else:  # pragma: no cover
    print("[store] Persistence backend: in-memory (set SUPABASE_URL/SUPABASE_KEY to enable Supabase)")


# ---------------------------------------------------------------------------
# Supabase client (lazy so the app imports without the package installed)
# ---------------------------------------------------------------------------
def _client_instance():
    global _client
    if _client is None:
        from supabase import create_client

        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client


# ---------------------------------------------------------------------------
# Hydrate the unchanged domain objects from Supabase rows
# ---------------------------------------------------------------------------
def _hydrate(users_rows, expenses_rows, splits_rows) -> ExpenseManager:
    manager = ExpenseManager()
    id_to_user: Dict[int, User] = {}

    for row in users_rows:
        user = User(int(row["id"]), row["name"])
        manager.users[user.id] = user
        id_to_user[user.id] = user

    splits_by_expense: Dict[int, list] = {}
    for row in splits_rows:
        splits_by_expense.setdefault(int(row["expense_id"]), []).append(row)

    max_id = 0
    for row in expenses_rows:
        expense_id = int(row["id"])
        max_id = max(max_id, expense_id)
        payer = id_to_user.get(int(row["payer_id"]))
        if payer is None:
            continue
        splits: Dict[User, float] = {}
        for split in splits_by_expense.get(expense_id, []):
            user = id_to_user.get(int(split["user_id"]))
            if user is not None:
                splits[user] = float(split["amount"])
        manager.expenses.append(Expense(expense_id, payer, float(row["amount"]), splits))

    manager.expense_count = max_id
    return manager


def _load_supabase_manager() -> ExpenseManager:
    client = _client_instance()
    users = client.table("users").select("*").order("id").execute().data or []
    expenses = client.table("expenses").select("*").order("id").execute().data or []
    splits = (
        client.table("expense_splits")
        .select("*")
        .order("expense_id")
        .order("user_id")
        .execute()
        .data
        or []
    )
    return _hydrate(users, expenses, splits)


def load_manager() -> ExpenseManager:
    """Return a fully-hydrated ExpenseManager for reads/validation."""
    return _load_supabase_manager() if USE_SUPABASE else _memory


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------
def list_users() -> List[User]:
    if not USE_SUPABASE:
        return _memory.list_users()
    rows = _client_instance().table("users").select("*").order("id").execute().data or []
    return [User(int(row["id"]), row["name"]) for row in rows]


def add_user(user_id: int, name: str) -> User:
    if not USE_SUPABASE:
        _memory.add_user(user_id, name)
        return _memory.get_user(user_id)

    client = _client_instance()
    existing = (
        client.table("users").select("id").eq("id", user_id).limit(1).execute().data
    )
    if existing:
        raise ValueError("User already exists")
    client.table("users").insert({"id": user_id, "name": name}).execute()
    return User(user_id, name)


def delete_user(user_id: int) -> None:
    if not USE_SUPABASE:
        _delete_user_memory(user_id)
        return

    client = _client_instance()
    exists = (
        client.table("users").select("id").eq("id", user_id).limit(1).execute().data
    )
    if not exists:
        raise LookupError("User not found")

    payer_refs = (
        client.table("expenses")
        .select("id")
        .eq("payer_id", user_id)
        .limit(1)
        .execute()
        .data
    )
    split_refs = (
        client.table("expense_splits")
        .select("expense_id")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
        .data
    )
    if payer_refs or split_refs:
        raise ValueError("Cannot delete user with associated expenses")

    client.table("users").delete().eq("id", user_id).execute()


def _delete_user_memory(user_id: int) -> None:
    if user_id not in _memory.users:
        raise LookupError("User not found")
    for expense in _memory.list_expenses():
        if expense.payer.id == user_id or any(u.id == user_id for u in expense.splits):
            raise ValueError("Cannot delete user with associated expenses")
    del _memory.users[user_id]


# ---------------------------------------------------------------------------
# Expenses
# ---------------------------------------------------------------------------
def list_expenses() -> List[Expense]:
    if not USE_SUPABASE:
        return _memory.list_expenses()
    return _load_supabase_manager().list_expenses()


def add_expense(payer_id: int, amount: float, splits: Dict[int, float]) -> Expense:
    if not USE_SUPABASE:
        return _memory.add_expense(payer_id, amount, splits)

    # Validate using the unchanged domain logic, then persist.
    manager = _load_supabase_manager()
    manager.add_expense(payer_id, amount, splits)  # raises ValueError when invalid

    client = _client_instance()
    inserted = (
        client.table("expenses")
        .insert({"payer_id": payer_id, "amount": amount})
        .execute()
        .data
    )
    if not inserted:
        raise RuntimeError("Failed to create expense")
    expense_id = int(inserted[0]["id"])

    split_rows = [
        {"expense_id": expense_id, "user_id": user_id, "amount": amt}
        for user_id, amt in splits.items()
    ]
    if split_rows:
        client.table("expense_splits").insert(split_rows).execute()

    payer = manager.get_user(payer_id)
    splits_objects = {manager.get_user(user_id): amt for user_id, amt in splits.items()}
    return Expense(expense_id, payer, amount, splits_objects)


def delete_expense(expense_id: int) -> None:
    if not USE_SUPABASE:
        for index, expense in enumerate(_memory.expenses):
            if expense.id == expense_id:
                _memory.expenses.pop(index)
                return
        raise LookupError("Expense not found")

    client = _client_instance()
    exists = (
        client.table("expenses")
        .select("id")
        .eq("id", expense_id)
        .limit(1)
        .execute()
        .data
    )
    if not exists:
        raise LookupError("Expense not found")
    # expense_splits has ON DELETE CASCADE, so splits are removed automatically.
    client.table("expenses").delete().eq("id", expense_id).execute()
