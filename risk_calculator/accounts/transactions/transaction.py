import accounts.transactions.transfer_item as tran_item

class Transaction():
    def __init__(self, item):
        self.activityId = item['activityId']
        self.time = item['time']
        try:
            self.description = item['description']
        except:
            self.description = None

        self.accountNumber = item['accountNumber']
        self.type = item['type']
        self.status = item['status']
        self.subAccount = item['subAccount']
        self.tradeDate = item['tradeDate']
        try:
            self.settlementDate = item['settlementDate']
        except:
            self.settlementDate = None
        try:
            self.positionId = item['positionId']
        except:
            self.positionId = None
            # print(str.format("{0} has no position.", self.activityId))
        try:
            self.orderId = item['orderId']
        except:
            self.orderId = None
            # print(str.format("{0} has no order.", self.activityId))
        self.netAmount = item['netAmount']
        
        self.transferItems = [tran_item.TransferItem(transfer_item) for transfer_item in item['transferItems']]

        # if self.type == 'TRADE':
            # to trade type details
