class TransferItem():
    def __init__(self, item):
        self.transfer_item = item
        self.instrument = item['instrument']
        self.assetType = self.instrument['assetType']
        # todo
        self.status = self.instrument['status']
        self.symbol = self.instrument['symbol']
        
        self.instrumentId = self.instrument['instrumentId']
        try:
            # we got this key error on GME WS, brand new warrant issued today, so no closing price yet.
            self.closingPrice = self.instrument['closingPrice']
        except:
            self.closingPrice = None
        self.amount = item['amount']
        self.cost = item['cost']
        if self.assetType == 'CURRENCY':
            try:
                self.feeType = item['feeType']
            except:
                self.feeType = None

        if self.assetType == 'EQUITY':
            try:
                self.positionEffect = item['positionEffect']
            except:
                self.positionEffect = None
        try:
            self.description = self.instrument['description']
        except:
            self.description = None