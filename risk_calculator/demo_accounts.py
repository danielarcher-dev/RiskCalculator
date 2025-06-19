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

print("My stock positions are:")
for pos in acct.SecuritiesAccount.Positions:
    # print(pos)
    if(pos.instrument.AssetType == 'EQUITY'):
        line = str.format("{0},{1},{2}", pos.symbol, pos.Quantity, pos.marketValue)
        print(line)

print("My options are:")
for pos in acct.SecuritiesAccount.Positions:
    # print(pos)
    if(pos.instrument.AssetType == 'OPTION'):
        line = str.format("{0},{1},{2}", pos.instrument.description, pos.Quantity, pos.marketValue)
        print(line)

# print(acct.Transactions)

print("My transactions are:")
for tran in acct.Transactions.Transactions:
    print(tran.activityId)





def market_hours():
    # resp = launcher.client.get_transactions(launcher.hash)
    # resp = launcher.client.get_market_hours(markets=schwab.client.Client.MarketHours.Market.OPTION)
    # print(resp.json())
    return None

def work_with_old_file():
    # # look at previous files
    # input_file = './data/output.json'
    # older = accounts.AccountsLauncher(input_file)
    # print(older.Account.CurrentBalances.CashBalance)
    return None