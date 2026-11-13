# simplify.py

def simplify_debts(balances):
    """
    Input:
        balances: dict {User: net_balance}

    Output:
        list of transactions:
        [(from_user, to_user, amount)]

    Convention:
        +ve balance → user should receive money
        -ve balance → user owes money
    """

    # Separate creditors and debtors
    creditors = []
    debtors = []

    for user, amount in balances.items():
        if amount > 1e-6:
            creditors.append([user, amount])
        elif amount < -1e-6:
            debtors.append([user, -amount])  # store positive debt

    # Sort (optional but improves determinism)
    creditors.sort(key=lambda x: x[1], reverse=True)
    debtors.sort(key=lambda x: x[1], reverse=True)

    transactions = []

    i, j = 0, 0

    # Greedy settlement
    while i < len(debtors) and j < len(creditors):
        debtor, debt = debtors[i]
        creditor, credit = creditors[j]

        settled_amount = min(debt, credit)

        transactions.append((debtor, creditor, settled_amount))

        # Update remaining amounts
        debtors[i][1] -= settled_amount
        creditors[j][1] -= settled_amount

        # Move pointers if settled
        if debtors[i][1] <= 1e-6:
            i += 1

        if creditors[j][1] <= 1e-6:
            j += 1

    return transactions