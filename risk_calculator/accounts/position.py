import accounts.instrument as instrument

class Position():
    def __init__(self, item):
        # I'm not a market maker, I'm not allowed to be both long and short on the same position, I can only be one or the other.
        # Therefore, I can safely make the assumption that if I'm short, I'm not long, and if I'm long, I'm not short.
        self.__longQuantity__ = item['longQuantity']
        self.__shortQuantity__ = item['shortQuantity']
        self.averagePrice = item['averagePrice']
        self.currentDayProfitLoss = item['currentDayProfitLoss']
        self.currentDayProfitLossPercentage = item['currentDayProfitLossPercentage']
        
        self.settledLongQuantity = item['settledLongQuantity']
        self.settledShortQuantity = item['settledShortQuantity']
        self.instrument = instrument.Instrument(item['instrument'])
        self.symbol = self.instrument.symbol
        
        self.marketValue = item['marketValue']
        self.maintenanceRequirement = item['maintenanceRequirement']
        self.currentDayCost = item['currentDayCost']

        if self.__shortQuantity__ > 0:
            self.LongOrShort = 'SHORT'
            self.Quantity = self.__shortQuantity__ * -1
            self.averageShortPrice = item['averageShortPrice']
            self.averagePrice = self.averageShortPrice
            self.taxLotAverageShortPrice = item['taxLotAverageShortPrice']
            self.taxLotAveragePrice = self.taxLotAverageShortPrice
            self.shortOpenProfitLoss = item['shortOpenProfitLoss']
            self.openProfitLoss = self.shortOpenProfitLoss

            # TODO: it is possible for a position to swing from long to short and back
            # to be careful when performing analysis on this
            self.previousSessionShortQuantity = item['previousSessionShortQuantity']
            
        elif self.__longQuantity__ > 0:
            self.LongOrShort = 'LONG'
            self.Quantity = self.__longQuantity__
            self.averageLongPrice = item['averageLongPrice']
            self.averagePrice = self.averageLongPrice
            self.taxLotAverageLongPrice = item['taxLotAverageLongPrice']
            self.taxLotAveragePrice = self.taxLotAverageLongPrice
            self.longOpenProfitLoss = item['longOpenProfitLoss']
            self.openProfitLoss = self.longOpenProfitLoss
            self.previousSessionLongQuantity = item['previousSessionLongQuantity']

    #     self.TradedToday()

    # def TradedToday(self):
    #     # perform a simple test to determine if there was a trade today
    #     # this logic fails
    #     # eg. if I bought 5 shares, then sold 5 shares today
    #     # this test would incorrectly return False
    #     if self.__shortQuantity__ != self.previousSessionShortQuantity:
    #         return True
    #     elif self.__longQuantity__ != self.previousSessionLongQuantity:
    #         return True
    #     else:
    #         return False