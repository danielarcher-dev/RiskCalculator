import accounts.current_balances as current_balances
import accounts.initial_balances as initial_balances
import accounts.position as pos

class SecuritiesAccount():

    def __init__(self, dataframe):
    # self.parse_args()
    # self.read_config()
    # self.get_client()
        self.securitiesAccount = dataframe
        self.AccountType = self.securitiesAccount['type'] 
        self.AccountNumber = self.securitiesAccount['accountNumber']
        self.RoundTrips = self.securitiesAccount['roundTrips']
        self.isDayTrader = self.securitiesAccount['isDayTrader']
        self.isClosingOnlyRestricted = self.securitiesAccount['isClosingOnlyRestricted']
        self.pfcbFlag = self.securitiesAccount['pfcbFlag']

        self.Positions = [pos.Position(position) for position in self.securitiesAccount['positions']]

        self.CurrentBalances = current_balances.CurrentBalances(self.securitiesAccount['currentBalances'])
        self.InitialBalances = initial_balances.InitialBalances(self.securitiesAccount['initialBalances'])