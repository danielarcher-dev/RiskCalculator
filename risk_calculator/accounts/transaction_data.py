import accounts.instrument as instrument
import accounts.transaction as tran

class TransactionData():
    def __init__(self, items):
        self.TransactionData = items
        self.Transactions = [tran.Transaction(item) for item in items]
        
        