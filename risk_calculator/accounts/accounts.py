from schwab import auth, client
import json
import csv
import conf
import json_to_csv
import pandas as pd
from io import StringIO
import httpx
import accounts.securities_account as sa

class AccountsLauncher():
    def __init__(self):
        # self.parse_args()
        self.read_config()
        self.get_client()
        self.target_account = self.config['RuntimeSecrets']['target_account']
        self.account_numbers = self.get_account_numbers()
        self.hash = self.get_account_hash(self.target_account)
        self.Account = sa.SecuritiesAccount(self.get_account_details(self.hash))
        
    
    def parse_args(self):
        #todo:
        print("if any arguments, implement this")
    
    def read_config(self):
        self.config = conf.get_config()
        
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


    def run(self):
        print("hello")

def run():
    launcher = AccountsLauncher()
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