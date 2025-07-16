#import accounts
# import httpx
import json
import accounts.accounts as accounts
import accounts.position as position
import charts.charts as chart
import time
import schwab
from typing import cast
import pandas as pd
import numpy as np
from io import StringIO
import xlsxwriter




def main():
    #these are for live:
    acct = accounts.AccountsLauncher()

    client = acct.client

    #these are for file
    # securities_account_file = './data/output_2025-05-02.json'
    # transactions_file = './data/transactions_file_2025-05-02.json'
    # acct = load_account_file(securities_account_file=securities_account_file, transactions_file=transactions_file)
    
    
    securities_account = acct.SecuritiesAccount
    transaction = acct.Transactions

    # high level reporting
    # print_welcome(securities_account, client)
    # print_options(acct.SecuritiesAccount)

    # acct.market_hours()


    # my_chart = chart.Charts(acct)

    # my_chart.print_180_daily('MSFT')
    # chart.print_180_daily('MSFT', client)

    # watchlist_file = "./data/watchlist.json"
    # chart_file = "./data/watchlist.xlsx"
    print_my_watchlist(watchlist_file=acct.watchlist)

    chart_my_watchlist(acct, watchlist_file=acct.watchlist, chart_file=acct.charts_file)



def load_account_file(securities_account_file, transactions_file):
    return accounts.AccountsLauncher(securities_account_file=securities_account_file, transactions_file=transactions_file)

def print_welcome(securities_account, client):
        print(str.format("My net liquidation value is: {0}", securities_account.CurrentBalances.LiquidationValue))
        print(str.format("My total cash is: {0}", securities_account.CurrentBalances.CashBalance))

        print("My stock positions are:")
        for pos in securities_account.Positions:
            pos = cast(position.Position, pos)
            if(pos.instrument.AssetType == 'EQUITY'):
                lastPrice = get_last_price(client, pos.symbol)
                line = str.format("{0}, {1}, {2}, {3}", pos.symbol, pos.Quantity, lastPrice, pos.marketValue)
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

def get_last_price(client, symbol):
    client = cast(schwab.client.Client, client)

    response = client.get_quote(symbol)
    response.raise_for_status()

    df = pd.read_json(StringIO(json.dumps(response.json())))
    price = df[symbol]['regular']['regularMarketLastPrice']
    return price

def print_my_watchlist(watchlist_file):
    with open(watchlist_file, "r") as json_file:
        watchlist = json.load(json_file) 
    for item in watchlist:
         print(item)

def chart_my_watchlist(acct, watchlist_file, chart_file):
    my_chart = chart.Charts(acct)

    with open(watchlist_file, "r") as json_file:
        watchlist = json.load(json_file) 


    # due to timeouts with the ExcelWriter, we're grabbing all the charts in one loop
    # and then writing them to Excel in a second loop
    for stock in watchlist['stocks']:
        # we don't actually need the data frames here, we're just interested in the image
        my_chart.print_180_daily(stock)
        my_chart.print_365_weekly(stock)

    with pd.ExcelWriter(chart_file, engine="xlsxwriter") as writer:
        writer.set_size(2000, 950)
        for stock in sorted(watchlist['stocks']):
            # abuse a blank data frame to create worksheet
            df_blank = pd.DataFrame()
            df_blank.to_excel(writer, sheet_name=stock)

            worksheet = writer.sheets[stock]
            worksheet.set_column("A:A", 1360)
            worksheet.set_zoom(120)
            worksheet.insert_image("A1", "{0}/{1}_chart_{2}.png".format(my_chart.path, stock, "180_daily"))
            # # worksheet.insert_rows(28)
            worksheet.insert_image("A30", "{0}/{1}_chart_{2}.png".format(my_chart.path, stock, "365_weekly"))


if __name__ == '__main__':
    # if RUN_ARGS.getboolean('profile'):
    #     import cProfile
    #     cProfile.run('main()', sort='tottime')
    # else:
    #     main()
    main()
