#import accounts
# import httpx
import json
import accounts.accounts as accounts
import accounts.position as position
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
import httpx



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




    #chart options
    print("My options are:")
    for pos in securities_account.Positions:
        # print(pos)
        if(pos.instrument.AssetType == 'OPTION'):

            position_option_chain(acct, pos)
        
    get_option_chain(acct, "MSFT", SchwabClient.Client.Options.ContractType.PUT )
    
    # print_my_watchlist(watchlist_file=acct.watchlist)

    # my_chart = chart.Charts(acct)
    # my_chart.chart_my_watchlist(acct, watchlist_file=acct.watchlist, chart_file=acct.charts_file)



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
    message = "This is my watchlist:"
    print(message)
    with open(watchlist_file, "r") as json_file:
        watchlist = json.load(json_file) 
    for item in sorted(watchlist["stocks"]):
         print(item)

# Step 2: Define your Q calculator
def calculate_q(premium_bid: float, strike_price: float) -> float:
    """
    Calculates the Q metric for evaluating the attractiveness of a 1-week DTE OTM put option.

    Parameters:
        premium_bid (float): Bid price for the nearest 1-week DTE OTM put option
        strike_price (float): Strike price of that option

    Returns:
        float: Q value as a percentage
    """
    if strike_price <= 0:
        raise ValueError("Strike price must be greater than zero.")
    q = (premium_bid / strike_price) * 52 * 100
    return round(q, 2) 

def position_option_chain(acct, pos):
    pos = cast(position.Position, pos)
    underlying_symbol = pos.instrument.underlyingSymbol
    contract_type = pos.instrument.putCall
    strike = pos.instrument.strike
    expiration = pos.instrument.expiration
    strategy=SchwabClient.Client.Options.Strategy.SINGLE
    include_underlying_quote=True

    get_option_chain(acct, underlying_symbol, contract_type, strike, expiration, strategy, include_underlying_quote)

def get_option_chain(acct, underlying_symbol, contract_type, strike=None, expiration=None, strategy=SchwabClient.Client.Options.Strategy.SINGLE, include_underlying_quote=True):

    if expiration == None:
        # This section allows me to re-use the main body while simplifying ad-hoc queries
        target_date = (datetime.now() + timedelta(days=7))
        from_date = (datetime.now())
    else:
         target_date = expiration
         from_date = expiration

    if strike == None:
        chain = acct.client.get_option_chain(
            symbol=underlying_symbol,
            contract_type=contract_type,
            strategy=strategy,
            strike_count=10,
            include_underlying_quote=include_underlying_quote,
            from_date=from_date,
            to_date=target_date
        )
    else:
        chain = acct.client.get_option_chain(
            symbol=underlying_symbol,
            contract_type=contract_type,
            strategy=strategy,
            strike=strike,
            include_underlying_quote=include_underlying_quote,
            from_date=from_date,
            to_date=target_date
        )
    
    assert chain.status_code == httpx.codes.OK
    chain_json = chain.json()

    # TODO: until I'm splitting out the individual dte/strike element, just save this at the underlyingSymbol level
    options_chain_name = acct.options_chain_file.replace("<symbol>", underlying_symbol)
    with open(options_chain_name, 'w') as json_file:
        json.dump(chain_json, json_file)

    if contract_type == SchwabClient.Client.Options.ContractType.PUT:
        ExpDateMap = "putExpDateMap"
    elif contract_type == SchwabClient.Client.Options.ContractType.CALL:
        ExpDateMap = "callExpDateMap"
    else:
        # TODO: currently, if we want both PUTs and CALLs, we need to order each one, or implement logic to handle ContractType.ANY
        raise Exception("invalid contract_type: {0}".format(contract_type))
    
    found_flag = False
    for dte in chain_json[ExpDateMap]:
        # This logic assumes options are traded for this symbol on given expiration date
        if str(expiration) == dte.split(":")[0]:
            for chain_strike in chain_json[ExpDateMap][dte]:
                if strike == float(chain_strike):
                    # If I've nested this correctly, there should only be one result matching dte and strike
                    chain_values = chain_json[ExpDateMap][dte][chain_strike][0]
                    option_symbol = chain_values["symbol"]
                    premium_bid = chain_values["bid"]
                    daysToExpiration = chain_values["daysToExpiration"]
                    description = chain_values["description"]

                    # TODO: add a handler for this
                    required_capital = strike * 100
                    premium_collected = premium_bid * 100
                    max_return_on_risk_pct = round((premium_collected / required_capital * 100), 4)
                    # annualized_return_on_risk_pct = max_return_on_risk_pct * 52
                    annualized_return_on_risk_pct = round((max_return_on_risk_pct / 365 / daysToExpiration), 4)

                    q_ratio = annualized_return_on_risk_pct

                    line = str.format("{0},{1},dte={2}, bid={3}, q={4}%", underlying_symbol, description, daysToExpiration, premium_bid, q_ratio)
                    print(line)

                    # print("Capital = {0}".format(required_capital))
                    # print("Premium = {0}".format(premium_collected))
                    # print("Max profit = {0}%".format(max_return_on_risk_pct))
                    # print("Annualized: {0}%".format(annualized_return_on_risk_pct))
                    # print(premium_bid, strike, daysToExpiration) 

                    found_flag = True

    # if we don't find the expiration and strike we're looking for, then save them all
    if found_flag != True:
        for dte in chain_json[ExpDateMap]:
            # This logic assumes options are traded for this symbol on given expiration date
            # if str(expiration) == dte.split(":")[0]:
                for chain_strike in chain_json[ExpDateMap][dte]:
                    # if strike == float(chain_strike):
                        # If I've nested this correctly, there should only be one result matching dte and strike
                        chain_values = chain_json[ExpDateMap][dte][chain_strike][0]
                        option_symbol = chain_values["symbol"]
                        premium_bid = chain_values["bid"]
                        daysToExpiration = chain_values["daysToExpiration"]
                        description = chain_values["description"]
                        strike = chain_values["strikePrice"]

                        # TODO: add a handler for this
                        required_capital = strike * 100
                        premium_collected = premium_bid * 100
                        max_return_on_risk_pct = round((premium_collected / required_capital * 100), 4)
                        # annualized_return_on_risk_pct = max_return_on_risk_pct * 52
                        annualized_return_on_risk_pct = round((max_return_on_risk_pct * 365 / daysToExpiration), 4)

                        q_ratio = annualized_return_on_risk_pct

                        line = str.format("{0},{1},dte={2}, bid={3}, q={4}%", underlying_symbol, description, daysToExpiration, premium_bid, q_ratio)
                        print(line)

                        # print("Capital = {0}".format(required_capital))
                        # print("Premium = {0}".format(premium_collected))
                        # print("Max profit = {0}%".format(max_return_on_risk_pct))
                        # print("Annualized: {0}%".format(annualized_return_on_risk_pct))
                        # print(premium_bid, strike, daysToExpiration)  
          

if __name__ == '__main__':
    # if RUN_ARGS.getboolean('profile'):
    #     import cProfile
    #     cProfile.run('main()', sort='tottime')
    # else:
    #     main()
    main()
