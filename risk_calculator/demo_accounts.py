#import accounts
# import httpx
import json
import accounts.accounts as accounts
import datetime
import time
import schwab

def main():
    #these are for live:
    # acct = accounts.AccountsLauncher()
    # acct.run()

    #these are for file
    securities_account_file = './data/output_2025-05-02.json'
    transactions_file = './data/transactions_file_2025-05-02.json'
    acct = load_account_file(securities_account_file=securities_account_file, transactions_file=transactions_file)
    securities_account = acct.SecuritiesAccount
    transaction = acct.Transactions



    # high level reporting
    lines = []
    print(str.format("My net liquidation value is: {0}", securities_account.CurrentBalances.LiquidationValue))
    print(str.format("My total cash is: {0}", securities_account.CurrentBalances.CashBalance))

    print("My stock positions are:")
    for pos in securities_account.Positions:
        # print(pos)
        if(pos.instrument.AssetType == 'EQUITY'):
            line = str.format("{0},{1},{2}", pos.symbol, pos.Quantity, pos.marketValue)
            print(line)

    print("My options are:")
    for pos in securities_account.Positions:
        # print(pos)
        if(pos.instrument.AssetType == 'OPTION'):
            line = str.format("{0},{1},{2}", pos.instrument.description, pos.Quantity, pos.marketValue)
            print(line)

    # print(acct.Transactions)

    print("My transactions are:")
    for tran in transaction.Transactions:

        earliest_date = datetime.datetime.now

        # date
        # if tran.tradeDate > 

        line = str.format("{0},{1},{2},{3},{4}", tran.activityId, tran.tradeDate, tran.type, tran.subAccount, tran.netAmount)
        
        print(line)
        for transferItem in tran.transferItems:
            line = str.format("{0},{1},{2},{3}", transferItem.assetType,transferItem.symbol,transferItem.description,transferItem.amount)
            print(line)
        


    # valuation_date = datetime.strptime('20221229', '%Y%m%d').date()


def market_hours():
    # resp = launcher.client.get_transactions(launcher.hash)
    # resp = launcher.client.get_market_hours(markets=schwab.client.Client.MarketHours.Market.OPTION)
    # print(resp.json())
    return None

def load_account_file(securities_account_file, transactions_file):
    return accounts.AccountsLauncher(securities_account_file=securities_account_file, transactions_file=transactions_file)



if __name__ == '__main__':
    # if RUN_ARGS.getboolean('profile'):
    #     import cProfile
    #     cProfile.run('main()', sort='tottime')
    # else:
    #     main()
    main()
