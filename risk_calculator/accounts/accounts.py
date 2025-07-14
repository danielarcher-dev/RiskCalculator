from schwab import auth, client
import json
import csv
import conf
import json_to_csv
import pandas as pd
from io import StringIO
import httpx
import accounts.securities_account as sa
import accounts.transactions.transaction_data as ta
import datetime

class AccountsLauncher():
    def __init__(self, securities_account_file=None, transactions_file=None):
        # self.parse_args()
        
        if (securities_account_file == None) and (transactions_file == None):
            self.read_config()
            self.get_client()
            self.target_account = self.config['RuntimeSecrets']['target_account']
            self.account_numbers = self.get_account_numbers()
            self.hash = self.get_account_hash(self.target_account)
            # this is a potential failure point. there are other responses than securitiesAccount, which I haven't implemented
            self.SecuritiesAccount = sa.SecuritiesAccount(self.get_account_details(self.hash)['securitiesAccount'])
            self.Transactions = ta.TransactionData(self.get_account_transactions())
            self.__save__()

        if(securities_account_file != None):
            # we can instantiate this by passing a dated file, but it should really be implemented at Securities account level
            self.read_config()
            with open (securities_account_file) as securities_account_file:
                data = json.load(securities_account_file)
            self.SecuritiesAccount = sa.SecuritiesAccount(data)

        if (transactions_file != None):
            with open (transactions_file) as transactions_file:
                data = json.load(transactions_file)
            self.Transactions = ta.TransactionData(data)

        # else:

        # these attributes should be the same whether the data is live from client or from passed json
        # transactions is a live query
        #


    def parse_args(self):
        #todo:
        print("if any arguments, implement this")
    
    def read_config(self):
        self.config = conf.get_config()
        self.securities_account_file = self.config['AppConfig']['securities_account_file'].replace('<date>',str(datetime.date.today()))
        self.transactions_file = self.config['AppConfig']['transactions_file'].replace('<date>',str(datetime.date.today()))
        
    def get_client(self):
        self.client = conf.get_client()
    
    def get_account_numbers(self):
        resp = self.client.get_account_numbers()
        assert resp.status_code == httpx.codes.OK
        account_numbers = resp.json()[0]
        return account_numbers

    def get_account_hash(self, target_account):
        # The response has the following structure. If you have multiple linked
        # accounts, you'll need to inspect this object to find the hash you want:
        # [
        #    {
        #        "accountNumber": "123456789",
        #        "hashValue":"123ABCXYZ"
        #    }
        #]


        #todo
        # a problem here, is that account_numbers is not guaranteed to only have one account, and I don't know what the response with multiple accounts looks like.
        for item in self.account_numbers:
            account_hash = ""
            
            account_number = self.account_numbers['accountNumber']
            if account_number == target_account:
                account_hash = self.account_numbers['hashValue']
        return account_hash
    
    def get_account_details(self, hash):
        resp = self.client.get_account(hash, fields=self.client.Account.Fields.POSITIONS)
        assert resp.status_code == httpx.codes.OK
        return resp.json()

    def get_account_transactions(self):
        resp = self.client.get_transactions(self.hash)
        assert resp.status_code == httpx.codes.OK
        return resp.json()

    def market_hours(self):
        resp = self.client.get_transactions(self.hash)
        resp = self.client.get_market_hours(markets=client.Client.MarketHours.Market.OPTION)
        print(resp.json())
        return None

    def __save__(self):
        # save account data to time_dated file
        with open(self.securities_account_file, 'w') as json_file:
            json.dump(self.SecuritiesAccount.securitiesAccount, json_file)
        
        # save transactions data to time_dated file
        with open(self.transactions_file, 'w') as json_file:
            json.dump(self.Transactions.TransactionData, json_file)


# if __name__ == '__main__':
#     # if RUN_ARGS.getboolean('profile'):
#     #     import cProfile
#     #     cProfile.run('main()', sort='tottime')
#     # else:
#     #     main()
#     # main()
#     run()