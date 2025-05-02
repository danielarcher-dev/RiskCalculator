#import accounts
# import httpx
import json
import accounts.accounts as accounts
# import datetime
import schwab

acct = accounts.AccountsLauncher()
acct.run()



# high level reporting
lines = []
print(str.format("My net liquidation value is: {0}", acct.SecuritiesAccount.CurrentBalances.LiquidationValue))
print(str.format("My total cash is: {0}", acct.SecuritiesAccount.CurrentBalances.CashBalance))

print("My positions are:")
for pos in acct.SecuritiesAccount.Positions:
    # print(pos)
    print(str.format("{0},{1},{2}", pos.symbol, pos.Quantity, pos.marketValue))

print(acct.Transactions)
# resp = launcher.client.get_transactions(launcher.hash)
# resp = launcher.client.get_market_hours(markets=schwab.client.Client.MarketHours.Market.OPTION)
# print(resp.json())

# # look at previous files
# input_file = './data/output.json'
# older = accounts.AccountsLauncher(input_file)
# print(older.Account.CurrentBalances.CashBalance)