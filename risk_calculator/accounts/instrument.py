class Instrument():
    def __init__(self, item):
        self.AssetType = item['assetType']
        self.cusip = item['cusip']
        self.symbol = item['symbol']
        self.netChange = item['netChange']

        if self.AssetType == "OPTION":
            self.description = item['description']
            self.type = item['type']
            self.putCall = item['putCall']
            self.underlyingSymbol = item['underlyingSymbol']