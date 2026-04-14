from models import User, Expense



class ExpenseManager:
    def __init__(self):
        self.users = {}
        self.expenses = []
        self.expense_count = 0
        self.next_user_id = 1

    # ---------- USER ----------
    def add_user(self, name: str):
        if not name or not name.strip():
            raise ValueError("User name cannot be empty")

        user_id = self.next_user_id
        self.next_user_id += 1

        user = User(user_id, name.strip())
        self.users[user_id] = user

        return user

    # ---------- EXPENSE ----------
    def add_expense(self, payer_id: int, amount: float, splits: dict, description = ""):

        # --- Validate payer ---
        if payer_id not in self.users:
            raise ValueError("Payer does not exist")

        # --- Validate amount ---
        if amount <= 0:
            raise ValueError("Amount must be positive")

        # --- Validate splits ---
        if not splits:
            raise ValueError("Splits cannot be empty")

        if any(v <= 0 for v in splits.values()):
            raise ValueError("Split amounts must be positive")

        total = sum(splits.values())
        if round(total, 2) != round(amount, 2): 
            raise ValueError("Splits must sum exactly to total amount")

        payer = self.users[payer_id]

        # --- Convert to User objects ---
        split_objects = {}
        for uid, amt in splits.items():
            if uid not in self.users:
                raise ValueError(f"User {uid} does not exist")

            split_objects[self.users[uid]] = amt

        # --- Create expense ---
        self.expense_count += 1

        expense = Expense(
            self.expense_count,
            payer,
            amount,
            split_objects,
            description
        )

        self.expenses.append(expense)

        return expense

    # ---------- READ ----------
    def list_expenses(self):
        return self.expenses