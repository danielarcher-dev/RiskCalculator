#import accounts
# import httpx
import json
import accounts.accounts as accounts
import datetime
import time
import schwab
import cufflinks as cf
import pandas as pd
import numpy as np
# setattr(plotly.offline, "__PLOTLY_OFFLINE_INITIALIZED", True)

def main():
    #these are for live:
    acct = accounts.AccountsLauncher()
    acct.run()

    client = acct.client

    #these are for file
    # securities_account_file = './data/output_2025-05-02.json'
    # transactions_file = './data/transactions_file_2025-05-02.json'
    # acct = load_account_file(securities_account_file=securities_account_file, transactions_file=transactions_file)
    
    
    securities_account = acct.SecuritiesAccount
    transaction = acct.Transactions

    

    # high level reporting
    print_welcome(securities_account)
    # acct.client.get
    # r2 = acct.client.get_instruments('MSFT',acct.client.Instrument.Projection.FUNDAMENTAL)
    # response = json.dumps(r2.json())
    # print(response)

    price_history = client.get_price_history_every_minute('MSFT').json()

    # print(json.dumps(price_history.json()))

    # print(price_history)
    # for price in price_history['candles']:
    #     #  print(price['open'])
    #     print(price)
    # print("Cufflinks Version: {}".format(cf.__version__))

    # cf.set_config_file(sharing='private', offline=True)

    # df=pd.DataFrame(np.random.randn(100,5),index=pd.date_range('1/1/15',periods=100),
    #             columns=['IBM','MSFT','GOOG','VERZ','APPL'])
    # df=df.cumsum()
    # df.iplot(filename='Tutorial 1', color='rgba(255, 153, 51)')
    cf.go_offline()
    # print(cf.get_config_file())
    # cf.datagen.box(20, color='rgb(255, 153, 51)').iplot(kind='box',legend=False)

# def msft_dataframe(price_history):
    df = pd.DataFrame(price_history['candles'], columns=['open', 'high', 'low', 'close', 'volume', 'datetime'])
    df['datetime'] = df['datetime'].apply(date_transform)
    df = df.set_index('datetime')
    dt_range = pd.date_range(start="2025-05-01", end="2025-05-16")

    
    msft_df = df[df.index.isin(dt_range)]
    msft_df.iplot()
    # msft_df.iplot(kind="candle",
    #               keys=["open", "high", "low", "close"],
    #               rangeslider=True)


def date_transform(datetime_data):
     timestamp = datetime_data/1000
     return datetime.datetime.fromtimestamp(timestamp)

def market_hours():
    # resp = launcher.client.get_transactions(launcher.hash)
    # resp = launcher.client.get_market_hours(markets=schwab.client.Client.MarketHours.Market.OPTION)
    # print(resp.json())
    return None

def load_account_file(securities_account_file, transactions_file):
    return accounts.AccountsLauncher(securities_account_file=securities_account_file, transactions_file=transactions_file)

def print_welcome(securities_account):
        print(str.format("My net liquidation value is: {0}", securities_account.CurrentBalances.LiquidationValue))
        print(str.format("My total cash is: {0}", securities_account.CurrentBalances.CashBalance))

        print("My stock positions are:")
        for pos in securities_account.Positions:
            # print(pos)
            if(pos.instrument.AssetType == 'EQUITY'):
                line = str.format("{0},{1},{2}", pos.symbol, pos.Quantity, pos.marketValue)
                print(line)

def print_options(securities_account):
        print("My options are:")
        for pos in securities_account.Positions:
            # print(pos)
            if(pos.instrument.AssetType == 'OPTION'):
                line = str.format("{0},{1},{2}", pos.instrument.description, pos.Quantity, pos.marketValue)
                print(line)

def print_transactions(transaction):
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

if __name__ == '__main__':
    # if RUN_ARGS.getboolean('profile'):
    #     import cProfile
    #     cProfile.run('main()', sort='tottime')
    # else:
    #     main()
    main()
