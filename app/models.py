"""Core data models for the expense splitter toolkit.

These models preserve the original core logic exactly.
"""


class User:
    """Represents a user in the expense splitter."""

    def __init__(self, user_id: int, name: str):
        self.id = user_id
        self.name = name

    def __repr__(self):
        return f"User({self.name})"

    def __eq__(self, other):
        return isinstance(other, User) and self.id == other.id

    def __hash__(self):
        return hash(self.id)


class Expense:
    """Represents an expense with splits.

    splits: dict {User: amount_owed}
    """

    def __init__(self, expense_id: int, payer: User, amount: float, splits: dict):
        self.id = expense_id
        self.payer = payer
        self.amount = amount
        self.splits = splits

    def __repr__(self):
        return f"Expense ({self.amount} by {self.payer.name})"
