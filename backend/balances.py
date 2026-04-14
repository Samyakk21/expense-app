# balance.py

def compute_balances(expenses):
    """
    Computes net balance for each user.

    Returns:
        dict {User: net_balance}

    Convention:
        +ve balance → user should receive money
        -ve balance → user owes money
    """

    balances = {}

    for expense in expenses:
        payer = expense.payer
        amount = expense.amount
        splits = expense.splits  # {User: amount_owed}

        # Ensure payer is in balances
        if payer not in balances:
            balances[payer] = 0
    
        # Payer initially paid full amount
        balances[payer] += amount

        # Subtract each user's share
        for user, share in splits.items():
            if user not in balances:
                balances[user] = 0

            balances[user] -= share

    return balances



