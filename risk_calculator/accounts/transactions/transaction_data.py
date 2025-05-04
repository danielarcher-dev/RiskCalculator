import accounts.transactions.transaction as tran

class TransactionData():
    def __init__(self, items):
        self.TransactionData = items
        self.Transactions = [tran.Transaction(item) for item in items]
        
        