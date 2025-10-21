class CurrentBalances():
    def __init__(self, dataframe, AccountType):
        self.AccruedInterest = dataframe['accruedInterest']
        self.CashBalance = dataframe['cashBalance']
        self.CashReceipts = dataframe['cashReceipts']
        self.LongOptionMarketValue = dataframe['longOptionMarketValue']
        self.LiquidationValue = dataframe['liquidationValue']
        self.LongMarketValue = dataframe['longMarketValue']
        self.MoneyMarketFund = dataframe['moneyMarketFund']
        self.Savings = dataframe['savings']
        self.ShortMarketValue  = dataframe['shortMarketValue']
        self.PendingDeposits = dataframe['pendingDeposits']
        self.MutualFundValue = dataframe['mutualFundValue']
        self.BondValue = dataframe['bondValue']
        self.ShortOptionMarketValue = dataframe['shortOptionMarketValue']

        if AccountType == 'CASH':
            self.cashAvailableForTrading = dataframe['cashAvailableForTrading']
            self.AvailableFunds = self.cashAvailableForTrading
            
            self.cashAvailableForWithdrawal = dataframe['cashAvailableForWithdrawal']
            self.cashCall = dataframe['cashCall']
            self.longNonMarginableMarketValue = dataframe['longNonMarginableMarketValue']
            self.totalCash = dataframe['totalCash']
            self.cashDebitCallValue = dataframe['cashDebitCallValue']
            self.unsettledCash = dataframe['unsettledCash']

        if AccountType == 'MARGIN':
            self.AvailableFunds = dataframe['availableFunds']
            self.AvailableFundsNonMarginableTrade = dataframe['availableFundsNonMarginableTrade']
            self.BuyingPower = dataframe['buyingPower']
            self.BuyingPowerNonMarginableTrade = dataframe['buyingPowerNonMarginableTrade']
            self.DayTradingBuyingPower = dataframe['dayTradingBuyingPower']
            self.Equity = dataframe['equity']
            self.EquityPercentage = dataframe['equityPercentage']
            self.LongMarginValue = dataframe['longMarginValue']
            self.MaintenanceCall = dataframe['maintenanceCall']
            self.MaintenanceRequirement = dataframe['maintenanceRequirement']
            self.MarginBalance = dataframe['marginBalance']
            self.RegTCall = dataframe['regTCall']
            self.ShortBalance = dataframe['shortBalance']
            self.ShortMarginValue = dataframe['shortMarginValue']
            self.sma = dataframe['sma']