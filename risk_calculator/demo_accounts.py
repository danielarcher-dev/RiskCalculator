#import accounts
# import httpx
import json
import accounts.accounts as accounts
import datetime
import time
import schwab

def main():
    #these are for live:
    acct = accounts.AccountsLauncher()
    acct.run()

    #these are for file
    # securities_account_file = './data/output_2025-05-02.json'
    # transactions_file = './data/transactions_file_2025-05-02.json'
    # acct = load_account_file(securities_account_file=securities_account_file, transactions_file=transactions_file)
    
    
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
        default_transaction_history_lookback = int(acct.config['AppConfig']['default_transaction_history_lookback'])
        earliest_date = datetime.datetime.now() - datetime.timedelta(days=default_transaction_history_lookback)
        
        tradeDate = datetime.datetime.fromisoformat(tran.tradeDate)
        # date
        if  tradeDate.date() > earliest_date.date():

            if tran.type == 'TRADE':
                    
                # print(tradeDate.strftime('%Y-%m-%d %H:%M'))
                # line = str.format("{0},{1},{2},{3},{4}", tradeDate.strftime('%Y-%m-%d %H:%M'), tran.activityId, tran.description, tran.type, tran.netAmount)
                line = str.format("{0},{1},{2},{3},{4},{5}", tradeDate.date(), tradeDate.time(), tran.type, tran.orderId, tran.description,tran.tradeDate)
            
                print(line)
                for transferItem in tran.transferItems:
                    # if(transferItem.
                    if(transferItem.assetType == 'CURRENCY'):
                        line = transferItem.feeType, transferItem.amount, transferItem.cost
                    # line = str.format("{0},{1},{2},{3},{4}", transferItem.assetType,transferItem.symbol,transferItem.description,transferItem.amount,transferItem.feeType)
                        print(line)
                    effect = ''
                    try:
                        effect = transferItem.positionEffect
                        print(effect)
                    except:
                        print("no effect")
            else:
                print(tran)

    

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
