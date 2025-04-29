import accounts.instrument as instrument

class Position():
    def __init__(self, item):
        self.shortQuantity = item['shortQuantity']
        self.averagePrice = item['averagePrice']
        self.currentDayProfitLoss = item['currentDayProfitLoss']
        self.currentDayProfitLossPercentage = item['currentDayProfitLossPercentage']
        self.longQuantity = item['longQuantity']
        self.settledLongQuantity = item['settledLongQuantity']
        self.settledShortQuantity = item['settledShortQuantity']
        self.instrument = instrument.Instrument(item['instrument'])
        self.marketValue = item['marketValue']
        self.maintenanceRequirement = item['maintenanceRequirement']
        self.currentDayCost = item['currentDayCost']

        if self.shortQuantity > 0:
            self.LongOrShort = 'SHORT'
            self.averageShortPrice = item['averageShortPrice']
            self.averagePrice = self.averageShortPrice
            self.taxLotAverageShortPrice = item['taxLotAverageShortPrice']
            self.shortOpenProfitLoss = item['shortOpenProfitLoss']
            self.openProfitLoss = self.shortOpenProfitLoss
            self.previousSessionShortQuantity = item['previousSessionShortQuantity']
        elif self.longQuantity > 0:
            self.LongOrShort = 'LONG'
            self.averageLongPrice = item['averageLongPrice']
            self.averagePrice = self.averageLongPrice
            self.taxLotAverageLongPrice = item['taxLotAverageLongPrice']
            self.longOpenProfitLoss = item['longOpenProfitLoss']
            self.openProfitLoss = self.longOpenProfitLoss
            self.previousSessionLongQuantity = item['previousSessionLongQuantity']
