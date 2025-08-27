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


    # high level reporting
    # print_welcome(securities_account, client)
    # print_options(acct)

    
    # print_my_orders(acct)
    # print_transactions(transactions, acct)
    # print_my_watchlist(watchlist_file=acct.watchlist)

    watchlist = acct.watchlist
    with open(acct.sp500_file, "r") as file:
            result = json.load(file)
            for object in result:
                watchlist.append(object["Symbol"])

    watchlist = sorted(set(watchlist))

    acct.get_fundamentals_batched(watchlist)


    # import pandas as pd

    # 1. Load your fundamentals into a DataFrame
    #    Assume `fundamentals` is a dict: { symbol: {roe:…, roa:…, grossMargin:…, …}, … }
    # df = pd.DataFrame.from_dict(acct.Fundamentals.Fundamentals, orient="index")
    df = acct.Fundamentals.to_df()

    print(df)

    # 2. Select & clean your metrics
    # using TTM trailing 12 months here, because I care that the company is profitable for more than just one quarter
    metrics = [
        "returnOnEquity", "returnOnAssets", "peRatio",
        "grossMarginTTM", "operatingMarginTTM", "netProfitMarginTTM",
        "totalDebtToEquity"
    ]
    # this one is not available from Schwab "fcfYield", 
    df = df[metrics].dropna()

    # 3. Compute percentile ranks for each metric
    for m in metrics:
        # For metrics where *higher* is better
        df[f"{m}_rank"] = df[m].rank(pct=True)

    # 4. Invert rank for Debt-to-Equity (lower is better)
    df["totalDebtToEquity_rank"] = (1 - df["totalDebtToEquity_rank"])
    df["peRatio_rank"] = (1 - df["peRatio_rank"])
    

    # 5. Composite quality score (simple average of ranks)
    rank_cols = [c for c in df.columns if c.endswith("_rank")]
    df["quality_score"] = df[rank_cols].mean(axis=1)

    # 6. Sort and pick top/bottom
    top_30   = df.sort_values("quality_score", ascending=False).head(30)
    bottom_10 = df.sort_values("quality_score", ascending=True).head(10)

    # 7. Results
    print("Top 30 Quality Stocks:\n", top_30["quality_score"])
    print("\nBottom 10 Risky Stocks:\n", bottom_10["quality_score"])

    save_file = acct.fundamentals_output_file.replace(".json", "_top30.csv")
    top_30.to_csv(save_file, index=True)

    save_file = acct.fundamentals_output_file.replace(".json", "_bottom30.csv")
    bottom_10.to_csv(save_file, index=True)



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
