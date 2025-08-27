import pandas as pd
import json

class Fundamentals():

    def __init__(self):
        self.FundamentalsData = None
        self.Fundamentals = []
        
        # 
    def add_fundamentals(self, dataframe):
        for item in dataframe:
            fundamental = Fundamental(item)
            self.Fundamentals.append(fundamental)

    def to_df(self):
        records = [stock.to_dict() for stock in self.Fundamentals]
        df = pd.DataFrame.from_records(records, index='symbol')
        return df

    def save_fundamentals_to_file(self, save_file):
        with open(save_file, 'w') as json_file:
                json.dump([stock.to_dict() for stock in self.Fundamentals], json_file, indent=2)

        df = self.to_df()
        df.to_csv(save_file.replace(".json", ".csv"), index=True)

class Fundamental():
    def __init__(self, item):
        self.data = item
        fundamental_data = item["fundamental"]
        self.cusip = item["cusip"]
        self.symbol = item["symbol"]
        self.description = item["description"]
        self.exchange = item["exchange"]
        self.assetType = item["assetType"]
        self.symbol = fundamental_data["symbol"]
        self.high52 = fundamental_data["high52"]
        self.low52 = fundamental_data["low52"]
        self.dividendAmount = fundamental_data["dividendAmount"]
        self.dividendYield = fundamental_data["dividendYield"]
        try:
            self.dividendDate = fundamental_data["dividendDate"]
            self.dividendPayDate = fundamental_data["dividendPayDate"]
            self.declarationDate = fundamental_data["declarationDate"]
            self.nextDividendPayDate = fundamental_data["nextDividendPayDate"]
            self.nextDividendDate = fundamental_data["nextDividendDate"]
        except:
            self.dividendDate = None
            self.dividendPayDate = None
            self.declarationDate = None
            self.nextDividendPayDate = None
            self.nextDividendDate = None
        self.peRatio = fundamental_data["peRatio"]
        self.pegRatio = fundamental_data["pegRatio"]
        self.pbRatio = fundamental_data["pbRatio"]
        self.prRatio = fundamental_data["prRatio"]
        self.pcfRatio = fundamental_data["pcfRatio"]
        self.grossMarginTTM = fundamental_data["grossMarginTTM"]
        self.grossMarginMRQ = fundamental_data["grossMarginMRQ"]
        self.netProfitMarginTTM = fundamental_data["netProfitMarginTTM"]
        self.netProfitMarginMRQ = fundamental_data["netProfitMarginMRQ"]
        self.operatingMarginTTM = fundamental_data["operatingMarginTTM"]
        self.operatingMarginMRQ = fundamental_data["operatingMarginMRQ"]
        self.returnOnEquity = fundamental_data["returnOnEquity"]
        self.returnOnAssets = fundamental_data["returnOnAssets"]
        self.returnOnInvestment = fundamental_data["returnOnInvestment"]
        self.quickRatio = fundamental_data["quickRatio"]
        self.currentRatio = fundamental_data["currentRatio"]
        self.interestCoverage = fundamental_data["interestCoverage"]
        self.totalDebtToCapital = fundamental_data["totalDebtToCapital"]
        self.ltDebtToEquity = fundamental_data["ltDebtToEquity"]
        self.totalDebtToEquity = fundamental_data["totalDebtToEquity"]
        self.epsTTM = fundamental_data["epsTTM"]
        self.epsChangePercentTTM = fundamental_data["epsChangePercentTTM"]
        self.epsChangeYear = fundamental_data["epsChangeYear"]
        self.epsChange = fundamental_data["epsChange"]
        self.revChangeYear = fundamental_data["revChangeYear"]
        self.revChangeTTM = fundamental_data["revChangeTTM"]
        self.revChangeIn = fundamental_data["revChangeIn"]
        self.sharesOutstanding = fundamental_data["sharesOutstanding"]
        self.marketCapFloat = fundamental_data["marketCapFloat"]
        self.marketCap = fundamental_data["marketCap"]
        self.bookValuePerShare = fundamental_data["bookValuePerShare"]
        self.shortIntToFloat = fundamental_data["shortIntToFloat"]
        self.shortIntDayToCover = fundamental_data["shortIntDayToCover"]
        self.divGrowthRate3Year = fundamental_data["divGrowthRate3Year"]
        self.dividendPayAmount = fundamental_data["dividendPayAmount"]
        self.beta = fundamental_data["beta"]
        self.vol1DayAvg = fundamental_data["vol1DayAvg"]
        self.vol10DayAvg = fundamental_data["vol10DayAvg"]
        self.vol3MonthAvg = fundamental_data["vol3MonthAvg"]
        self.avg10DaysVolume = fundamental_data["avg10DaysVolume"]
        self.avg1DayVolume = fundamental_data["avg1DayVolume"]
        self.avg3MonthVolume = fundamental_data["avg3MonthVolume"]
        self.dividendFreq = fundamental_data["dividendFreq"]
        self.eps = fundamental_data["eps"]
        self.dtnVolume = fundamental_data["dtnVolume"]
        self.fundLeverageFactor = fundamental_data["fundLeverageFactor"]

    def to_dict(self):
        return {
            "cusip": self.cusip,
            "symbol": self.symbol,
            "description": self.description,
            "exchange": self.exchange,
            "assetType": self.assetType,
            "symbol": self.symbol,
            "high52": self.high52,
            "low52": self.low52,
            "dividendAmount": self.dividendAmount,
            "dividendYield": self.dividendYield,
            "dividendDate": self.dividendDate,
            "dividendPayDate": self.dividendPayDate,
            "declarationDate": self.declarationDate,
            "nextDividendPayDate": self.nextDividendPayDate,
            "nextDividendDate": self.nextDividendDate,
            "peRatio": self.peRatio,
            "pegRatio": self.pegRatio,
            "pbRatio": self.pbRatio,
            "prRatio": self.prRatio,
            "pcfRatio": self.pcfRatio,
            "grossMarginTTM": self.grossMarginTTM,
            "grossMarginMRQ": self.grossMarginMRQ,
            "netProfitMarginTTM": self.netProfitMarginTTM,
            "netProfitMarginMRQ": self.netProfitMarginMRQ,
            "operatingMarginTTM": self.operatingMarginTTM,
            "operatingMarginMRQ": self.operatingMarginMRQ,
            "returnOnEquity": self.returnOnEquity,
            "returnOnAssets": self.returnOnAssets,
            "returnOnInvestment": self.returnOnInvestment,
            "quickRatio": self.quickRatio,
            "currentRatio": self.currentRatio,
            "interestCoverage": self.interestCoverage,
            "totalDebtToCapital": self.totalDebtToCapital,
            "ltDebtToEquity": self.ltDebtToEquity,
            "totalDebtToEquity": self.totalDebtToEquity,
            "epsTTM": self.epsTTM,
            "epsChangePercentTTM": self.epsChangePercentTTM,
            "epsChangeYear": self.epsChangeYear,
            "epsChange": self.epsChange,
            "revChangeYear": self.revChangeYear,
            "revChangeTTM": self.revChangeTTM,
            "revChangeIn": self.revChangeIn,
            "sharesOutstanding": self.sharesOutstanding,
            "marketCapFloat": self.marketCapFloat,
            "marketCap": self.marketCap,
            "bookValuePerShare": self.bookValuePerShare,
            "shortIntToFloat": self.shortIntToFloat,
            "shortIntDayToCover": self.shortIntDayToCover,
            "divGrowthRate3Year": self.divGrowthRate3Year,
            "dividendPayAmount": self.dividendPayAmount,
            "beta": self.beta,
            "vol1DayAvg": self.vol1DayAvg,
            "vol10DayAvg": self.vol10DayAvg,
            "vol3MonthAvg": self.vol3MonthAvg,
            "avg10DaysVolume": self.avg10DaysVolume,
            "avg1DayVolume": self.avg1DayVolume,
            "avg3MonthVolume": self.avg3MonthVolume,
            "dividendFreq": self.dividendFreq,
            "eps": self.eps,
            "dtnVolume": self.dtnVolume,
            "fundLeverageFactor": self.fundLeverageFactor
        }