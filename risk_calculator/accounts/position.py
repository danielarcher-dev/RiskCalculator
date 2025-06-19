import accounts.instrument as instrument

class Position():
    def __init__(self, item):
        
        self.__longQuantity__ = item['longQuantity']
        self.__shortQuantity__ = item['shortQuantity']
        self.averagePrice = item['averagePrice']
        self.currentDayProfitLoss = item['currentDayProfitLoss']
        self.currentDayProfitLossPercentage = item['currentDayProfitLossPercentage']
        
        # self.settledLongQuantity = item['settledLongQuantity']
        # self.settledShortQuantity = item['settledShortQuantity']
        self.instrument = instrument.Instrument(item['instrument'])
        self.symbol = self.instrument.symbol
        # self.mark = self.instrument.
        self.marketValue = item['marketValue']
        self.maintenanceRequirement = item['maintenanceRequirement']
        self.currentDayCost = item['currentDayCost']

        if self.__shortQuantity__ > 0:
            self.LongOrShort = 'SHORT'
            self.Quantity = self.__shortQuantity__
            self.averageShortPrice = item['averageShortPrice']
            self.averagePrice = self.averageShortPrice
            self.taxLotAverageShortPrice = item['taxLotAverageShortPrice']
            self.shortOpenProfitLoss = item['shortOpenProfitLoss']
            self.openProfitLoss = self.shortOpenProfitLoss
            self.previousSessionShortQuantity = item['previousSessionShortQuantity']
            
        elif self.__longQuantity__ > 0:
            self.LongOrShort = 'LONG'
            self.Quantity = self.__longQuantity__
            self.averageLongPrice = item['averageLongPrice']
            self.averagePrice = self.averageLongPrice
            self.taxLotAverageLongPrice = item['taxLotAverageLongPrice']
            self.longOpenProfitLoss = item['longOpenProfitLoss']
            self.openProfitLoss = self.longOpenProfitLoss
            self.previousSessionLongQuantity = item['previousSessionLongQuantity']
