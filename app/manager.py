"""Expense manager - core business logic (unchanged from original)."""

from .models import User, Expense


class ExpenseManager:
    """Manages users and expenses. Core logic preserved from original."""

    def __init__(self):
        self.users = {}
        self.expenses = []
        self.expense_count = 0

    def add_user(self, userid: int, name: str):
        if userid in self.users:
            raise ValueError("User already exists")

        user = User(userid, name)
        self.users[userid] = user
        return user

    def get_user(self, userid: int):
        return self.users.get(userid)

    def get_all_users(self):
        return list(self.users.values())

    def add_expense(self, payer_id: int, amount: float, splits: dict):
        """Add an expense.

        splits: dict {userid: amount}
        Core validation logic preserved from original.
        """
        if payer_id not in self.users:
            raise ValueError("Payer does not exist")

        if len(splits) == 0:
            raise ValueError("Splits cannot be empty")

        if abs(sum(splits.values()) - amount) > 1e-6:
            raise ValueError("Splits do not sum to total amount")

        payer = self.users[payer_id]

        for userid in splits.keys():
            if userid not in self.users:
                raise ValueError(f"User {userid} does not exist")

        splits_objects = {}
        for userid, amt in splits.items():
            user = self.users[userid]
            splits_objects[user] = amt

        self.expense_count += 1

        expense = Expense(
            self.expense_count,
            payer,
            amount,
            splits_objects,
        )

        self.expenses.append(expense)
        return expense

    def list_expenses(self):
        return self.expenses

    def list_users(self):
        return list(self.users.values())
