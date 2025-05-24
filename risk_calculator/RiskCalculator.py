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

class RiskCalculator():
    def __init__(self, securities_account_file=None, transactions_file=None):
        # self.parse_args()

        print("do something")


        acct = accounts.AccountsLauncher()
        # acct.run()
        balances = acct.SecuritiesAccount.CurrentBalances
        cash = balances.CashBalance
        position_balance = balances.Equity
        
        print("Cash balance: {0}".format(cash))
        print(position_balance)
        print(balances.ShortOptionMarketValue)
        print(balances.LongOptionMarketValue)



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
    launcher.run()

if __name__ == '__main__':
    # if RUN_ARGS.getboolean('profile'):
    #     import cProfile
    #     cProfile.run('main()', sort='tottime')
    # else:
    #     main()
    # main()
    run()