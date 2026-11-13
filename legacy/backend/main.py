# main.py

from expenses import ExpenseManager
from balances import compute_balances
from simplify_debts import simplify_debts


def print_balances(balances):
    print("\n=== BALANCES ===")
    for user, amount in balances.items():
        print(f"{user.name}: {round(amount, 2)}")


def print_transactions(transactions):
    print("\n=== SETTLEMENTS ===")
    if not transactions:
        print("No transactions required.")
        return

    for debtor, creditor, amount in transactions:
        print(f"{debtor.name} → {creditor.name}: {round(amount, 2)}")


def main():
    manager = ExpenseManager()

    # --- Create Users ---
    manager.add_user(1, "Alice")
    manager.add_user(2, "Bob")
    manager.add_user(3, "Charlie")
    manager.add_user(4, "David")

    # --- Add Expenses ---

    # Case 1: Equal split including payer
    manager.add_expense(
        payer_id=1,
        amount=900,
        splits={
            1: 300,
            2: 300,
            3: 300
        }
    )

    # Case 2: Payer NOT included (pays for others)
    manager.add_expense(
        payer_id=2,
        amount=400,
        splits={
            3: 200,
            4: 200
        }
    )

    # Case 3: Unequal split
    manager.add_expense(
        payer_id=3,
        amount=500,
        splits={
            1: 200,
            3: 100,
            4: 200
        }
    )

    # --- Compute Balances ---
    balances = compute_balances(manager.list_expenses())

    print_balances(balances)

    # --- Simplify Debts ---
    transactions = simplify_debts(balances)

    print_transactions(transactions)


if __name__ == "__main__":
    main()