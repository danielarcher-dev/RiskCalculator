import pandas as pd
import json
import accounts.current_balances as current_balances
import accounts.initial_balances as initial_balances
import accounts.position as pos

class SecuritiesAccount():
    def __init__(self, dataframe):
    # self.parse_args()
    # self.read_config()
    # self.get_client()
        self.securitiesAccount = dataframe['securitiesAccount']
        self.AccountType = self.securitiesAccount['type'] 
        self.AccountNumber = self.securitiesAccount['accountNumber']
        self.RoundTrips = self.securitiesAccount['roundTrips']
        self.isDayTrader = self.securitiesAccount['isDayTrader']
        self.isClosingOnlyRestricted = self.securitiesAccount['isClosingOnlyRestricted']
        self.pfcbFlag = self.securitiesAccount['pfcbFlag']
        self.Positions = self.parse_positions(self.securitiesAccount['positions'])
                
        self.CurrentBalances = current_balances.CurrentBalances(self.securitiesAccount['currentBalances'])
        self.InitialBalances = initial_balances.InitialBalances(self.securitiesAccount['initialBalances'])


    def parse_positions(self, pos_data):
        Positions = []
        for po in range(len(pos_data)):
            # print(po)
            position = pos.Position(pos_data[po])
            Positions.append(position)
        return Positions


