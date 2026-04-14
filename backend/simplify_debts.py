def simplify_debts(balances):
    creditors = []
    debtors = []

    for user, amt in balances.items():
        if amt > 1e-6:
            creditors.append([user, amt])
        elif amt < -1e-6:
            debtors.append([user, -amt])

    transactions = []

    i = j = 0

    while i < len(debtors) and j < len(creditors):
        debtor, debt = debtors[i]
        creditor, credit = creditors[j]

        settle = min(debt, credit)

        transactions.append((debtor, creditor, settle))

        debtors[i][1] -= settle
        creditors[j][1] -= settle

        if debtors[i][1] <= 1e-6:
            i += 1
        if creditors[j][1] <= 1e-6:
            j += 1

    return transactions