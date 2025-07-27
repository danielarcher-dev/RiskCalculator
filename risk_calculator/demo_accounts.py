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
from datetime import datetime
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



    # Client.Client.Options.Type.




    #chart options
    print("My options are:")
    for pos in securities_account.Positions:
        # print(pos)
        if(pos.instrument.AssetType == 'OPTION'):

            position_option_chain(acct, pos)
            # chain = client.get_option_chain(
            #     symbol=pos.instrument.underlyingSymbol,
            #     contract_type=pos.instrument.putCall,
            #     strategy=client.Options.Strategy.SINGLE,
            #     strike=pos.instrument.strike,
            #     include_underlying_quote=True,
            #     from_date=pos.instrument.expiration,
            #     to_date=pos.instrument.expiration
            # )
            
            # assert chain.status_code == httpx.codes.OK
            # chain_json = chain.json()
            # options_chain_name = acct.options_chain_file.replace("<symbol>", pos.symbol)
            # with open(options_chain_name, 'w') as json_file:
            #     json.dump(chain_json, json_file)
            
            # for dte in chain_json["putExpDateMap"]:
            #     if str(pos.instrument.expiration) == dte.split(":")[0]:
            #         for strike in chain_json["putExpDateMap"][dte]:
            #             if str(pos.instrument.strike) == strike:
            #                 # If I've nested this correctly, there should only be one result matching dte and strike
            #                 chain_values = chain_json["putExpDateMap"][dte][strike][0]

            #                 premium_bid = chain_values["bid"]
            #                 daysToExpiration = chain_values["daysToExpiration"]
            # # premium_bid = chain_json["putExpDateMap"].values()[0].values()[0]["bid"]
            # strike_price = pos.instrument.strike
            # q_ratio = round((premium_bid / (strike_price * 100)) * (365 / daysToExpiration), 4)

            # line = str.format("{0},{1},{2},{3},{4}", pos.instrument.underlyingSymbol, pos.instrument.description, pos.Quantity, pos.marketValue, q_ratio)
            # print(line)
            # print(premium_bid, strike_price, daysToExpiration)            






    
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

def get_option_chain(acct, underlying_symbol, contract_type, strike, expiration, strategy=SchwabClient.Client.Options.Strategy.SINGLE, include_underlying_quote=True):

    chain = acct.client.get_option_chain(
        symbol=underlying_symbol,
        contract_type=contract_type,
        strategy=strategy,
        strike=strike,
        include_underlying_quote=include_underlying_quote,
        from_date=expiration,
        to_date=expiration
    )
    
    assert chain.status_code == httpx.codes.OK
    chain_json = chain.json()


    if contract_type == SchwabClient.Client.Options.ContractType.PUT:
        ExpDateMap = "putExpDateMap"
    elif contract_type == SchwabClient.Client.Options.ContractType.CALL:
        ExpDateMap = "callExpDateMap"
    else:
        raise Exception("invalid contract_type: {0}".format(contract_type))
    
    for dte in chain_json[ExpDateMap]:
        if str(expiration) == dte.split(":")[0]:

            for chain_strike in chain_json[ExpDateMap][dte]:
                if strike == float(chain_strike):
                    # If I've nested this correctly, there should only be one result matching dte and strike
                    chain_values = chain_json[ExpDateMap][dte][chain_strike][0]
                    option_symbol = chain_json["symbol"]
                    premium_bid = chain_values["bid"]
                    daysToExpiration = chain_values["daysToExpiration"]
                    description = chain_values["description"]
    options_chain_name = acct.options_chain_file.replace("<symbol>", option_symbol)
    with open(options_chain_name, 'w') as json_file:
        json.dump(chain_json, json_file)

    q_ratio = round((premium_bid / (strike * 100)) * (365 / daysToExpiration), 4)

    line = str.format("{0},{1},{2}", underlying_symbol, description, q_ratio)
    print(line)
    print(premium_bid, strike, daysToExpiration)  


# def parse_occ_symbol(symbol):
#     match = re.match(r'([A-Z ]{6})(\d{6})([CP])(\d{8})', symbol)
#     if not match:
#         return None

#     # root = match.group(1).strip()
#     date_str = match.group(2)
#     option_type = match.group(3)
#     strike_raw = match.group(4)

#     expiration = datetime.strptime(date_str, '%y%m%d').date()
#     strike = int(strike_raw) / 1000

#     return {
#         # 'root': root,
#         'expiration': expiration,
#         'type': 'Put' if option_type == 'P' else 'Call',
#         'strike': strike
#     }               

if __name__ == '__main__':
    # if RUN_ARGS.getboolean('profile'):
    #     import cProfile
    #     cProfile.run('main()', sort='tottime')
    # else:
    #     main()
    main()
