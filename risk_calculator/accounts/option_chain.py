from schwab.client import Client
from datetime import datetime, timedelta
import json
import httpx
from typing import cast
import accounts.accounts as accounts
import accounts.position as position

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
    strategy=Client.Options.Strategy.SINGLE
    include_underlying_quote=True

    option_chain = get_option_chain(acct, underlying_symbol, contract_type, strike, expiration, strategy, include_underlying_quote)
    option_chain.marketValue = round(option_chain.mark * option_chain.multiplier * pos.Quantity, 4)
    return option_chain

def get_option_chain(acct, underlying_symbol, contract_type, strike=None, expiration=None, strategy=Client.Options.Strategy.SINGLE, include_underlying_quote=True):

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

    if contract_type == Client.Options.ContractType.PUT:
        ExpDateMap = "putExpDateMap"
    elif contract_type == Client.Options.ContractType.CALL:
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
                    found_flag = True
                    option_chain = OptionChain(chain_values)

                    return option_chain

    # if we don't find the expiration and strike we're looking for, then save them all
    if found_flag != True:
        chain_list = []
        for dte in chain_json[ExpDateMap]:
            for chain_strike in chain_json[ExpDateMap][dte]:
                chain_values = chain_json[ExpDateMap][dte][chain_strike][0]
                option_chain = OptionChain(chain_values)
                chain_list.append(option_chain)
        return chain_list
          

def get_market_value_of_option(acct, underlying_symbol, contract_type, strike=None, expiration=None, strategy=Client.Options.Strategy.SINGLE, include_underlying_quote=True):
    pos = cast(position.Position, pos)
    underlying_symbol = pos.instrument.underlyingSymbol
    contract_type = pos.instrument.putCall
    strike = pos.instrument.strike
    expiration = pos.instrument.expiration
    strategy=Client.Options.Strategy.SINGLE
    include_underlying_quote=True

    option_chain = get_option_chain(acct, underlying_symbol, contract_type, strike, expiration, strategy, include_underlying_quote)

    return option_chain.premium_bid * pos.Quantity


class OptionChain:
    def __init__(self, item):
        self.chain = item
        if item['putCall'] == 'PUT':
            self.putCall = Client.Options.ContractType.PUT
        elif item['putCall'] == 'CALL':
            self.putCall = Client.Options.ContractType.CALL
        else:
            self.putCall = item['putCall']
        self.option_symbol = item['symbol']
        self.description = item['description']
        self.bid = item['bid']
        self.ask = item['ask']
        self.last = item['last']
        # the returned JSON only has 2 decimal places, but ThinkOrSwim reports up to 4 decimal places. this may lead to discrepencies
        self.mark = item['mark']
        self.bidSize = item['bidSize']
        self.askSize = item['askSize']
        self.bidAskSize = item['bidAskSize']
        self.lastSize = item['lastSize']
        self.highPrice = item['highPrice']
        self.lowPrice = item['lowPrice']
        self.openPrice = item['openPrice']
        self.closePrice = item['closePrice']
        self.totalVolume = item['totalVolume']
        self.tradeTimeInLong = item['tradeTimeInLong']
        self.quoteTimeInLong = item['quoteTimeInLong']
        self.netChange = item['netChange']
        self.volatility = item['volatility']
        self.delta = item['delta']
        self.gamma = item['gamma']
        self.vega = item['vega']
        self.rho = item['rho']
        self.openInterest = item['openInterest']
        self.timeValue = item['timeValue']
        self.theoreticalOptionValue = item['theoreticalOptionValue']
        self.theoreticalVolatility = item['theoreticalVolatility']
        self.optionDeliverablesList = item['optionDeliverablesList']
        self.strikePrice = item['strikePrice']
        self.expirationDate = item['expirationDate']
        self.daysToExpiration = item['daysToExpiration']
        self.expirationType = item['expirationType']
        self.lastTradingDay = item['lastTradingDay']
        self.multiplier = item['multiplier']
        self.settlementType = item['settlementType']
        self.deliverableNote = item['deliverableNote']
        self.percentChange = item['percentChange']
        self.markChange = item['markChange']
        self.markPercentChange = item['markPercentChange']
        self.intrinsicValue = item['intrinsicValue']
        self.extrinsicValue = item['extrinsicValue']
        self.optionRoot = item['optionRoot']
        self.exerciseType = item['exerciseType']
        self.high52Week = item['high52Week']
        self.low52Week = item['low52Week']
        self.nonStandard = item['nonStandard']
        self.pennyPilot = item['pennyPilot']
        self.inTheMoney = item['inTheMoney']
        self.mini = item['mini']

        # for my own analysis, premium collected is not based on bid, but based on option cost
        self.premium_collected = self.bid * self.multiplier
        self.required_capital =  (self.strikePrice - self.bid) * self.multiplier
        self.max_return_on_risk_pct = round(((self.premium_collected / self.required_capital) * 100), 4)
        if self.daysToExpiration == 0:
            # this metric makes no sense if dte is zero, annualizing would imply infinite returns
            self.annualized_return_on_risk_pct = 0
        else:
            self.annualized_return_on_risk_pct = round((self.max_return_on_risk_pct * 365 / self.daysToExpiration), 4)

        self.q_ratio = self.annualized_return_on_risk_pct

        self.marketValue = None


# chain = client.get_option_chain(
            #     symbol=pos.instrument.underlyingSymbol,
            #     contract_type=pos.instrument.putCall,
            #     strategy=client.Options.Strategy.SINGLE,
            #     strike_count=10,
            #     include_underlying_quote=True,
            #     from_date=pos.instrument.expiration,
            #     to_date=pos.instrument.expiration
            # )
            
            # assert chain.status_code == httpx.codes.OK
            # chain_json = chain.json()
            # options_chain_name = acct.options_chain_file.replace("<symbol>", pos.symbol)
            # with open(options_chain_name, 'w') as json_file:
            #     json.dump(chain_json, json_file)