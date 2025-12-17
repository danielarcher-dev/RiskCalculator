import pandas as pd
import json
from typing import cast

class Fundamentals():

    def __init__(self):
        self.FundamentalsData = None
        self.Fundamentals = []
        self.quality_scores = None
        self.top_30 = None
        self.top_50 = None
        self.bottom_10 = None
        
        # 
    def add_fundamentals(self, dataframe):
        # for item in dataframe:
        #     fundamental = Fundamental(item)
        #     self.Fundamentals.append(fundamental)
        for item in dataframe:
            new_fundamental = Fundamental(item)
            symbol = new_fundamental.symbol

            # Remove existing fundamental with the same symbol
            self.Fundamentals = [
                f for f in self.Fundamentals if f.symbol != symbol
            ]

            # Add the new one
            self.Fundamentals.append(new_fundamental)

    def calculate_quality_score(self):
        # 1. Load your fundamentals into a DataFrame
        df = self.to_df()

        # 2. Select & clean your metrics
        # using TTM trailing 12 months here, because I care that the company is profitable for more than just one quarter
        metrics = [
            "returnOnEquity", "returnOnAssets", "peRatio", "pcfRatio",
            "grossMarginTTM", "operatingMarginTTM", "netProfitMarginTTM",
            "totalDebtToEquity"
        ]
        # this one is not available from Schwab "fcfYield",
            # 2b. Drop rows with missing values only for selected metrics
            # df_clean = df.dropna(subset=metrics)
            # df = df[metrics].dropna()

        # 3. Compute percentile ranks for each metric
        for m in metrics:
            # For metrics where *higher* is better
            df[f"{m}_rank"] = df[m].rank(pct=True)

        # 4. Invert rank for Debt-to-Equity (lower is better)
        df["totalDebtToEquity_rank"] = (1 - df["totalDebtToEquity_rank"])
        df["peRatio_rank"] = (1 - df["peRatio_rank"])

        # 5. Composite quality score (simple average of ranks)
        rank_cols = [c for c in df.columns if c.endswith("_rank")]
        df["quality_score"] = df[rank_cols].mean(axis=1)

        self.quality_scores = df
        # 6. Sort and pick top/bottom
        self.top_30   = df.sort_values("quality_score", ascending=False).head(30)
        self.top_50   = df.sort_values("quality_score", ascending=False).head(50)
        self.bottom_10 = df.sort_values("quality_score", ascending=True).head(10)

    def get_fundamental(self, symbol):
        for item in self.Fundamentals:
            item = cast(Fundamental, item)
            if item.symbol == symbol:
                return item

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