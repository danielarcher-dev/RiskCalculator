#import accounts
# import httpx
import json
import accounts.accounts as accounts
import datetime
import time
import schwab

import pandas as pd
import numpy as np

import mplfinance as fplt


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

    # print_15_mins('NTB', client)

    # print_15_mins('GME', client)

    # price_history = client.get_price_history_every_minute('MSFT', start_datetime=earliest_date).json()

    print_180_daily('GME', client)



def print_15_mins(symbol, client):
    earliest_date = datetime.datetime.now() - datetime.timedelta(days=1)
    price_history = client.get_price_history_every_fifteen_minutes(symbol, start_datetime=earliest_date).json()

    df = price_history_to_dataframe(price_history)

    my_plot_settings(symbol, df)

def print_180_daily(symbol, client):
    earliest_date = datetime.datetime.now() - datetime.timedelta(days=180)
    price_history = client.get_price_history_every_day(symbol, start_datetime=earliest_date).json()

    df = price_history_to_dataframe(price_history)

    my_plot_settings(symbol, df)


def price_history_to_dataframe(price_history):
    df = pd.DataFrame(price_history['candles'], columns=['open', 'high', 'low', 'close', 'volume', 'datetime'])
    df['datetime'] = df['datetime'].apply(date_transform)
    df = df.set_index('datetime')
    # dt_range = pd.date_range(start="2025-05-01", end="2025-05-16")
    # df = df[df.index > (dt_range)]
    # df = df[df.index.]
    return df

def my_plot_settings(symbol, df):
    fplt.plot(
    df,
    type='candle',
    style='charles',
    title='{0}, May - 2025'.format(symbol),
    ylabel='Price ($)',
    figsize=(21,6),
    savefig=dict(fname='{0}_chart.png'.format(symbol), dpi=1200)
    )

    # fig = fplt.figure(figsize=(21, 7))  # Wider chart
    # ax = fig.add_subplot(1, 1, 1)

    # fplt.plot(df,
    #           type='candle',
    #           style='charles',
    #         #   suptitle='{0}, May - 2025'.format(symbol),
    #           ylabel='Price ($)',
    #           ax=ax,
    #           savefig=dict(fname='{0}_chart.png'.format(symbol), dpi=1200))
    # fig.show()


    # fig, ax = fplt.plot(df, type='candle', style='charles', returnfig=True)
    # fig.update_layout(width=1200, height=600)
    # fig.savefig('{0}_chart.png'.format(symbol), dpi=300)
    # fig.show()

    



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

def print_transactions(transaction, acct):
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
