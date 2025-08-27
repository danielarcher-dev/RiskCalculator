from schwab import auth
from schwab.client import Client
import json
import csv
import conf
import json_to_csv
import pandas as pd
from io import StringIO
import httpx
import accounts.securities_account as sa
import accounts.transactions.transaction_data as ta
import accounts.orders as o
import accounts.position as Position
import accounts.option_chain as Options
import accounts.fundamentals as Fundamentals
import datetime
from typing import cast
import requests

class AccountsLauncher():
    def __init__(self, securities_account_file=None, transactions_file=None):
        # self.parse_args()
        
        if (securities_account_file == None) and (transactions_file == None):
            self.read_config()
            self.get_client()
            self.target_account = self.config['RuntimeSecrets']['target_account']
            self.account_numbers = self.get_account_numbers()
            self.hash = self.get_account_hash(self.target_account)
            # this is a potential failure point. there are other responses than securitiesAccount, which I haven't implemented
            self.SecuritiesAccount = sa.SecuritiesAccount(self.get_account_details(self.hash)['securitiesAccount'])
            self.Transactions = ta.TransactionData(self.get_account_transactions())
            self.Orders = o.Orders(self.get_account_orders())
            self.__save__()

        if(securities_account_file != None):
            # we can instantiate this by passing a dated file, but it should really be implemented at Securities account level
            self.read_config()
            with open (securities_account_file) as securities_account_file:
                data = json.load(securities_account_file)
            self.SecuritiesAccount = sa.SecuritiesAccount(data)

        if (transactions_file != None):
            with open (transactions_file) as transactions_file:
                data = json.load(transactions_file)
            self.Transactions = ta.TransactionData(data)

        # else:

        # these attributes should be the same whether the data is live from client or from passed json
        # transactions is a live query
        #


    def parse_args(self):
        #todo:
        print("if any arguments, implement this")
    
    def read_config(self):
        self.config = conf.get_config()
        self.securities_account_file = self.config['AppConfig']['securities_account_file'].replace('<date>',str(datetime.date.today()))
        self.transactions_file = self.config['AppConfig']['transactions_file'].replace('<date>',str(datetime.date.today()))
        self.orders_file = self.config['AppConfig']['orders_file'].replace('<date>',str(datetime.date.today()))
        self.charts_file = self.config['Charting']['charts_file'].replace('<date>',str(datetime.date.today()))
        self.charts_path = self.config['Charting']['charts_path']
        self.watchlist_file = self.config['Charting']['watchlist']
        self.watchlist = self.get_watchlist()
        self.options_chain_file = self.config['AppConfig']['options_chain_file'].replace('<date>',str(datetime.date.today()))
        self.risk_calculator_output_file = self.config['AppConfig']['risk_calculator_output_file'].replace('<date>',str(datetime.date.today()))
        self.risk_calculator_charts_file = self.config['AppConfig']['risk_calculator_charts_file'].replace('<date>',str(datetime.date.today()))
        self.quote_output_file = self.config['AppConfig']['quote_output_file'].replace('<date>',str(datetime.date.today()))
        self.price_history_output_file = self.config['AppConfig']['price_history_output_file'].replace('<date>',str(datetime.date.today()))
        
        self.sp500_file = self.config['AppConfig']['index_file'].replace("<index>", "sp500")
        self.nyse_file = self.config['AppConfig']['index_file'].replace("<index>", "nyse")
        self.nasdaq_file = self.config['AppConfig']['index_file'].replace("<index>", "nasdaq")
        self.amex_file = self.config['AppConfig']['index_file'].replace("<index>", "amex")
        self.fundamentals_output_file = self.config['AppConfig']['fundamentals_output_file'].replace('<date>',str(datetime.date.today()))
    
    def get_client(self):
        self.client = conf.get_client()
    
    def get_account_numbers(self):
        resp = self.client.get_account_numbers()
        assert resp.status_code == httpx.codes.OK
        account_numbers = resp.json()[0]
        return account_numbers

    def get_account_hash(self, target_account):
        # The response has the following structure. If you have multiple linked
        # accounts, you'll need to inspect this object to find the hash you want:
        # [
        #    {
        #        "accountNumber": "123456789",
        #        "hashValue":"123ABCXYZ"
        #    }
        #]


        #todo
        # a problem here, is that account_numbers is not guaranteed to only have one account, and I don't know what the response with multiple accounts looks like.
        for item in self.account_numbers:
            account_hash = ""
            
            account_number = self.account_numbers['accountNumber']
            if account_number == target_account:
                account_hash = self.account_numbers['hashValue']
        return account_hash
    
    def get_account_details(self, hash):
        resp = self.client.get_account(hash, fields=self.client.Account.Fields.POSITIONS)
        assert resp.status_code == httpx.codes.OK
        return resp.json()

    def get_account_transactions(self):
        resp = self.client.get_transactions(self.hash)
        assert resp.status_code == httpx.codes.OK
        return resp.json()

    def get_account_orders(self):
        resp = self.client.get_orders_for_account(self.hash)
        assert resp.status_code == httpx.codes.OK
        orders = resp.json()
        return orders

    def get_account_symbols(self):
        sorted_by_symbol = sorted(self.SecuritiesAccount.Positions, key= lambda pos: pos.symbol)

        portfolio_symbols_list = []

        for pos in sorted_by_symbol:
            pos = cast(Position.Position, pos)
            if pos.instrument.AssetType == 'EQUITY':
                portfolio_symbols_list.append(pos.symbol)
            elif pos.instrument.AssetType == 'OPTION':
                portfolio_symbols_list.append(pos.instrument.underlyingSymbol)
        
        return sorted(set(portfolio_symbols_list))

    def get_symbol_quote(self, symbol, quote_type):
        result = self.client.get_quote(symbol).json()
        save_file = self.quote_output_file.replace("<symbol>", symbol)
        with open(save_file, 'w') as json_file:
            json.dump(result, json_file)

        return result[symbol]['quote'][quote_type]

    def get_symbol_stop(self, symbol):
        filter_statuses = ['OPEN', 'PENDING_ACTIVATION', 'WORKING']
        stopPrice = []
        for order in filter(lambda o: o.status in filter_statuses and o.orderType == "STOP", self.Orders.Orders):
            # TODO: figure out how to handle multi leg orders. for now, assume only 1 leg
            for orderLeg in filter(lambda ol: ol.instrument.symbol == symbol and ol.legId == 1,  order.OrderLegs):
                # orderLeg = cast(Orders.OrderLeg, orderLeg)
                result = {"stopPrice": order.stopPrice, "quantity":order.quantity}
                stopPrice.append(result)
        return stopPrice
    
    def get_symbol_limit(self, symbol):
        filter_statuses = ['OPEN', 'PENDING_ACTIVATION', 'WORKING']
        limitPrice = []
        for order in filter(lambda o: o.status in filter_statuses and o.orderType == "LIMIT", self.Orders.Orders):
            # TODO: figure out how to handle multi leg orders. for now, assume only 1 leg
            for orderLeg in filter(lambda ol: ol.instrument.symbol == symbol and ol.legId == 1,  order.OrderLegs):
                # orderLeg = cast(Orders.OrderLeg, orderLeg)
                result = {"limitPrice": order.price, "quantity":order.quantity}
                limitPrice.append(result)
        return limitPrice
    
    def get_symbol_orders(self, symbol):
        # TODO: optimization: download my orders, process them. then index them based on my positions and watchlist
        # I should only have to parse orders.json once, not every single time for every single symbol
        filter_statuses = ['OPEN', 'PENDING_ACTIVATION', 'WORKING']
        symbolOrders = []
        for order in filter(lambda o: o.status in filter_statuses, self.Orders.Orders):
            # TODO: figure out how to handle multi leg orders. for now, assume only 1 leg
            try:
                for orderLeg in filter(lambda ol: ol.instrument.symbol == symbol and ol.legId == 1,  order.OrderLegs):
                    symbolOrders.append(order)
            except:
                print("This order has no legs: {0}".format(order.Order))
        return symbolOrders

    def get_symbol_average_price(self, symbol):
        sorted_by_symbol = sorted(self.SecuritiesAccount.Positions, key= lambda pos: pos.symbol)
        averagePrice = None

        for pos in sorted_by_symbol:
            pos = cast(Position.Position, pos)
            if pos.symbol == symbol:
                averagePrice = pos.averagePrice
                return averagePrice

    def get_symbol_options(self, symbol):
        sorted_by_symbol = sorted(self.SecuritiesAccount.Positions, key= lambda pos: pos.symbol)
        averagePrice = None
        symbolOptions = []
        for pos in sorted_by_symbol:
            pos = cast(Position.Position, pos)
            if pos.instrument.underlyingSymbol == symbol:
                    symbolOptions.append(pos)
        return symbolOptions

    def is_it_naked(self, position, opt):
        pos = cast(Position.Position, position)
        opt = cast(Options.OptionChain, opt)

        shares_required_to_cover = pos.Quantity * opt.multiplier
        shares_owned = self.SecuritiesAccount.get_symbol_quantity(pos.instrument.underlyingSymbol)

        if shares_owned < shares_required_to_cover:
            return True
        else:
            return False

    def get_option_break_even_point(self, opt, averagePrice):
        opt = cast(Options.OptionChain, opt)

        break_even_point = None

        # This calculation doesn't take into account the impact of rolling options for credit or dividends
        # to solve this, we would have to dig through transactions and orders logs and make some inference
        if opt.putCall == Client.Options.ContractType.CALL:
            break_even_point = opt.strikePrice + averagePrice
        elif opt.putCall == Client.Options.ContractType.PUT:
            break_even_point = opt.strikePrice - averagePrice
    
        return break_even_point

    def get_watchlist(self):
        watchlist = []
        with open(self.watchlist_file, "r") as json_file:
                result = json.load(json_file)
                for stock in sorted(result['stocks']):
                    watchlist.append(stock)
        return sorted(set(watchlist))

    def get_sp500_index(self):
        response = requests.get("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies", headers=self.headers)
        response.raise_for_status()  # Raises HTTPError if status is 403

        tables = pd.read_html(response.text)
        sp500 = tables[0]
        
        self.save_result(sp500, self.sp500_file)

    def chunked(self, lst, size):
        for i in range(0, len(lst), size):
            yield lst[i:i + size]

    def get_fundamentals_batched(self, watchlist, batch_size=100):
        self.Fundamentals = Fundamentals.Fundamentals()

        for batch in self.chunked(watchlist, batch_size):
            result = self.client.get_instruments(batch, self.client.Instrument.Projection.FUNDAMENTAL)
            result.raise_for_status()
            instruments = result.json()["instruments"]
            # for item in instruments:
            #     fundamental = Fundamentals.Fundamental(item)
            #     fundamentals.append(fundamental)
            self.Fundamentals.add_fundamentals(instruments)
        
        self.Fundamentals.save_fundamentals_to_file(self.fundamentals_output_file)
        
        return self.Fundamentals

    def market_hours(self):
        resp = self.client.get_transactions(self.hash)
        resp = self.client.get_market_hours(markets=Client.MarketHours.Market.OPTION)
        print(resp.json())
        return None

    def __save__(self):
        # save account data to time_dated file
        with open(self.securities_account_file, 'w') as json_file:
            json.dump(self.SecuritiesAccount.securitiesAccount, json_file)
        
        # save transactions data to time_dated file
        with open(self.transactions_file, 'w') as json_file:
            json.dump(self.Transactions.TransactionData, json_file)

        # save orders data to time_dated file
        with open(self.orders_file, 'w') as json_file:
            json.dump(self.Orders.OrderData, json_file)


# if __name__ == '__main__':
#     # if RUN_ARGS.getboolean('profile'):
#     #     import cProfile
#     #     cProfile.run('main()', sort='tottime')
#     # else:
#     #     main()
#     # main()
#     run()