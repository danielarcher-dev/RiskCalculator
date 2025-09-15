import httpx
import json
import accounts.accounts as accounts
import accounts.position as position
import accounts.option_chain as Options
# import accounts.transactions #.transaction_data as T
from accounts.transactions import transaction_data, transaction
import accounts.orders as Orders
import accounts.fundamentals as Fundamentals
# import accounts.orders.Order as Orders

import charts.charts as chart
import time
import schwab
from schwab import client as SchwabClient
from typing import cast
import pandas as pd
import numpy as np
from io import StringIO
import xlsxwriter
from datetime import datetime, timedelta
import re



def main():
    #these are for live:
    acct = accounts.AccountsLauncher()

    client = acct.client

    #these are for file
    # securities_account_file = './data/output_2025-05-02.json'
    # transactions_file = './data/transactions_file_2025-05-02.json'
    # acct = load_account_file(securities_account_file=securities_account_file, transactions_file=transactions_file)
    
    # securities_account = acct.SecuritiesAccount
    # transactions = acct.Transactions

    watchlist = acct.watchlist
    for item in acct.Fundamentals.top_30.index:
        watchlist.append(item)
    scored_tickers = []
    for stock in watchlist:
        quality_score = acct.Fundamentals.quality_scores["quality_score"][stock]
        scored_tickers.append((stock, quality_score))
    sorted_tickers = sorted(scored_tickers, key=lambda x: x[1], reverse=True)
    print(sorted_tickers)
    


    # high level reporting
    # print_welcome(securities_account, client)
    # print_options(acct)

    
    # print_my_orders(acct)
    # print_transactions(transactions, acct)
    # print_my_watchlist(watchlist_file=acct.watchlist)



# Usage


    # my_chart = chart.Charts(acct)
    # my_chart.chart_my_watchlist(acct)
    # my_chart.print_1_day_30_minute("GME")
    # my_chart.print_180_daily("MSFT")
    # my_chart.print_15_mins("MST")





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

def print_options(acct):
    print("My options are:")
    for pos in acct.securities_account.Positions:
        if(pos.instrument.AssetType == 'OPTION'):
            opt = Options.position_option_chain(acct, pos)
            line = str.format("{0},{1},dte={2}, bid={3}, mark={4}, q={5}%, mv=${6}", opt.option_symbol, opt.description, opt.daysToExpiration, opt.bid, opt.mark, opt.q_ratio, opt.marketValue)
            print(line)

def print_transactions(transactions, acct):
        print("My transactions are:")
        transactions = cast(transaction_data.TransactionData, transactions)

        default_transaction_history_lookback = int(acct.config['AppConfig']['default_transaction_history_lookback'])
        earliest_date = datetime.now() - timedelta(days=default_transaction_history_lookback)
        

        for tran in transactions.Transactions:
            tran = cast(transaction.Transaction, tran)
            tradeDate = datetime.fromisoformat(tran.tradeDate)    
            
            if  tradeDate.date() > earliest_date.date():
                print(tran.activityId)
                if tran.type == 'TRADE':
                    print(tran.accountNumber, )
                    
                    # print(tran)    
                    # # print(tradeDate.strftime('%Y-%m-%d %H:%M'))
                    # # line = str.format("{0},{1},{2},{3},{4}", tradeDate.strftime('%Y-%m-%d %H:%M'), tran.activityId, tran.description, tran.type, tran.netAmount)
                    # line = str.format("{0},{1},{2},{3},{4},{5}", tradeDate.date(), tradeDate.time(), tran.type, tran.orderId, tran.description,tran.tradeDate)
                
                    # print(line)
                    # for transferItem in tran.transferItems:
                    #     # if(transferItem.
                    #     if(transferItem.assetType == 'CURRENCY'):
                    #         line = transferItem.feeType, transferItem.amount, transferItem.cost
                    #     # line = str.format("{0},{1},{2},{3},{4}", transferItem.assetType,transferItem.symbol,transferItem.description,transferItem.amount,transferItem.feeType)
                    #         print(line)
                    #     effect = ''
                    #     try:
                    #         effect = transferItem.positionEffect
                    #         print(effect)
                    #     except:
                    #         print("no effect")
                # else:
                    print(tran)

def get_last_price(client, symbol):
    client = cast(schwab.client.Client, client)

    response = client.get_quote(symbol)
    response.raise_for_status()

    df = pd.read_json(StringIO(json.dumps(response.json())))
    price = df[symbol]['regular']['regularMarketLastPrice']
    return price

def print_my_watchlist(watchlist_file):
    message = "This is my watchlist:"
    print(message)
    with open(watchlist_file, "r") as json_file:
        watchlist = json.load(json_file) 
    for item in sorted(watchlist["stocks"]):
         print(item)

def print_my_orders(acct):
    acct = cast(accounts.AccountsLauncher, acct)
    filter_statuses = ['OPEN', 'PENDING_ACTIVATION', 'WORKING']

    for pos in acct.SecuritiesAccount.Positions:
        pos = cast(position.Position, pos)

        for order in filter(lambda o: o.status in filter_statuses, acct.Orders.Orders):
        
            for orderLeg in filter(lambda ol: ol.instrument.symbol == pos.symbol,  order.OrderLegs):
                orderLeg = cast(Orders.OrderLeg, orderLeg)
                print("{},{},{},{},{}".format(
                    order.orderId,
                    orderLeg.instrument.symbol,
                    orderLeg.quantity,
                    order.status,
                    order.enteredTime
                ))


if __name__ == '__main__':
    # if RUN_ARGS.getboolean('profile'):
    #     import cProfile
    #     cProfile.run('main()', sort='tottime')
    # else:
    #     main()
    main()
