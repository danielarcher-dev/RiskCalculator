from datetime import datetime
import re
from schwab.client import Client
class Instrument():
    def __init__(self, item):
        self.AssetType = item['assetType']
        self.cusip = item['cusip']
        self.symbol = item['symbol']
        self.netChange = item['netChange']

        if self.AssetType == "OPTION":
            self.description = item['description']
            self.type = item['type']
            if item['putCall'] == 'PUT':
                self.putCall = Client.Options.ContractType.PUT
            elif item['putCall'] == 'CALL':
                self.putCall = Client.Options.ContractType.CALL
            else:
                self.putCall = item['putCall']
            self.underlyingSymbol = item['underlyingSymbol']
            occ = self.parse_occ_symbol()
            self.expiration = occ["expiration"]
            self.strike = float(occ["strike"])


    def parse_occ_symbol(self):
        return self.parse_occ_symbol(self.symbol)
        
    def parse_occ_symbol(symbol):
        match = re.match(r'([A-Z ]{6})(\d{6})([CP])(\d{8})', symbol)
        if not match:
            return None

        # root = match.group(1).strip()
        date_str = match.group(2)
        option_type = match.group(3)
        strike_raw = match.group(4)

        expiration = datetime.strptime(date_str, '%y%m%d').date()
        strike = int(strike_raw) / 1000

        return {
            # 'root': root,
            'expiration': expiration,
            'option_type': Client.Options.ContractType.PUT if option_type == 'P' else Client.Options.ContractType.CALL,
            'strike': strike
        }    