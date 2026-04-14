class User:
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
    def __init__(self, expense_id: int, payer: User, amount: float, splits: dict, description:str = ""):
        self.id = expense_id
        self.payer = payer
        self.amount = amount
        self.splits = splits  # {User: amount}
        self.description = description

    def __repr__(self):
        return f"Expense({self.amount} by {self.payer.name})"