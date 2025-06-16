from schwab import auth, client
import json
import csv
import conf
import json_to_csv
import pandas as pd
from io import StringIO
import httpx
# import accounts.securities_account as sa
# import accounts.transactions.transaction_data as ta
import accounts.accounts as accounts
import datetime
import xlsxwriter


class RiskCalculator():
    def __init__(self, securities_account_file=None, transactions_file=None):
        # self.parse_args()

        print("do something")


        acct = accounts.AccountsLauncher()
        # acct.run()
        balances = acct.SecuritiesAccount.CurrentBalances
        cash = balances.CashBalance
        # position_balance = 
        
        print("Cash balance: {0}".format(cash))
        print(balances.LongMarketValue)
        print(balances.ShortOptionMarketValue)
        print(balances.LongOptionMarketValue)

        print(cash + balances.LongMarketValue + balances.ShortOptionMarketValue)
        print(balances.BuyingPower)
        print(balances.AvailableFunds)
        print(balances.CashReceipts)

        workbook   = xlsxwriter.Workbook('filename.xlsx')

        rpt = workbook.add_worksheet()
        rpt.set_zoom(135)
        rpt.write('A1', "Cash")
        rpt.write('B1', balances.CashBalance)
        rpt.write('A2', "Short Options")
        rpt.write('B2', balances.ShortOptionMarketValue)
        rpt.write('A3', "Long Options")
        rpt.write('B3', balances.LongOptionMarketValue)

        rpt.write('D1', "Net Liquidity")
        rpt.write('E1', balances.LiquidationValue)
        rpt.write('D2', "Max Available for Trade")
        rpt.write('E2', balances.AvailableFunds)
        
        rpt.write('B5', "Symbol")
        rpt.write('C5', "Quantity")
        rpt.write('D5', "LastPrice")
        rpt.write('E5', "MarketValue")
        rpt.write('F5', 'Qty * Last Price')
        rpt.write('G5', 'Average Price')

        print("My stock positions are:")
        row = 6
        
        for pos in acct.SecuritiesAccount.Positions:
            # print(pos)
            if(pos.instrument.AssetType == 'EQUITY'):
                line = str.format("{0},{1},{2}", pos.symbol, pos.Quantity, pos.marketValue)
                # print(line)
                rpt.write('B{0}'.format(str(row)), pos.symbol)
                rpt.write('C{0}'.format(str(row)), pos.Quantity)
                rpt.write('D{0}'.format(str(row)), acct.client.get_quote(pos.symbol).json()[pos.symbol]['quote']['lastPrice'])
                rpt.write('E{0}'.format(str(row)), pos.marketValue)
                rpt.write('F{0}'.format(str(row)), "=C{0}*D{0}".format(str(row)))
                rpt.write('G{0}'.format(str(row)), pos.averagePrice)

                row = row+1
        
        # symbol = 'NTB'
        # row = '5'
        # rpt.write('B{0}'.format(row), symbol)
        # rpt.write('C{0}'.format(row), acct.client.get_quote(symbol).json()[symbol]['quote']['lastPrice'])

        # # resp = client.Client.get_instrument_by_cusip("NTB")
        # resp = acct.client.get_instruments("NTB", acct.client.Instrument.Projection.FUNDAMENTAL).json()
        # # inst = resp.json()
        # # print(inst)
        # print(resp)

        response = acct.client.get_quote("NTB").json()['NTB']['quote']['lastPrice']
        # ['lastPrice']
        print(response)

        rpt.write

        rpt.autofit()
        workbook.close()


    def parse_args(self):
        #todo:
        print("if any arguments, implement this")
    
    def read_config(self):
        self.config = conf.get_config()
        self.securities_account_file = self.config['AppConfig']['securities_account_file'].replace('<date>',str(datetime.date.today()))
        self.transactions_file = self.config['AppConfig']['transactions_file'].replace('<date>',str(datetime.date.today()))
    




    def run(self):
        print("hello")



def run():
    launcher = RiskCalculator()
    # launcher.start()
    # launcher.run()

if __name__ == '__main__':
    # if RUN_ARGS.getboolean('profile'):
    #     import cProfile
    #     cProfile.run('main()', sort='tottime')
    # else:
    #     main()
    # main()
    run()