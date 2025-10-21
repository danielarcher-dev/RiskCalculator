from schwab import auth
from schwab.client import Client
import json
import csv
import conf
import pandas as pd
from io import StringIO
import httpx
# import accounts.securities_account as sa
# import accounts.transactions.transaction_data as ta
import accounts.accounts as accounts
import accounts.securities_account as sec
import accounts.position as position
import accounts.option_chain as Options
import accounts.orders as Orders
import charts.charts as Charts
# import accounts.workbook_formats as workbook_formats
import datetime
import xlsxwriter
from typing import cast


class RiskCalculator():
    def __init__(self, securities_account_file=None, transactions_file=None):
        # self.parse_args()
        

        print("doing something")


        acct = accounts.AccountsLauncher()

        balances = acct.SecuritiesAccount.CurrentBalances

        with(xlsxwriter.Workbook(acct.risk_calculator_output_file) as workbook):
            workbook.set_size(2620, 1820)
            self.write_portfolio(acct, balances, workbook)
            self.write_portfolio_charts(acct, workbook)
            self.write_watchlist(acct, workbook)


            # r2 = c.get_instruments('AAPL,MSFT,GME,NTB',c.Instrument.Projection.FUNDAMENTAL)
            # # r2 = c.get_instruments('MSFT',c.Instrument.Projection.FUNDAMENTAL)
            # r2.raise_for_status()
            # df = pd.read_json(json.dumps(r2.json()))
            # print(df)
            # print(df['instruments'][0]['fundamental']['symbol'])
            
            # save_file = "fundamentals.json"
            # with open(save_file, 'w') as json_file:
            #     json.dump(r2.json(), json_file)




            self.write_notes(workbook)
        




        print("done something")



    def write_watchlist(self, acct, workbook):
        acct = cast(accounts.AccountsLauncher, acct)
        # sec_acct = cast(sec.SecuritiesAccount, acct.SecuritiesAccount)

        wbf = self.workbook_formats(workbook)
        accounting_format = wbf['accounting_format']
        pct_format = wbf['pct_format']
        bold_format = wbf['bold_format']
        date_format = wbf['date_format']

        watchlist = acct.watchlist

        # I want to prioritize my charting review by quality of stock
        # I want to view the top 30 and bottom 10
        for item in acct.Fundamentals.top_30.index:
            watchlist.append(item)
        for item in acct.Fundamentals.bottom_10.index:
            watchlist.append(item)
        scored_tickers = []
        for stock in watchlist:
            quality_score = acct.Fundamentals.quality_scores["quality_score"][stock]
            scored_tickers.append((stock, quality_score))
        sorted_tickers = sorted(scored_tickers, key=lambda x: x[1], reverse=True)
        watchlist = [ticker for ticker, score in sorted_tickers]

        mycharts = Charts.Charts(acct) # charting also needs acct.client
        # mycharts.export_stocklist(portfolio_symbols, charts_file)

        mycharts.generate_charts(watchlist)
        # self.generate_charts(watchlist)

        for stock in watchlist:
            try:
                rpt = workbook.add_worksheet(stock)

                rpt.set_zoom(100)

                # TODO: I don't like hardcoding the file names here, come back an fix it
                image1 = "{0}/{1}_chart_{2}.png".format(acct.charts_path, stock, "1_day_30_minute")
                image2 = "{0}/{1}_chart_{2}.png".format(acct.charts_path, stock, "180_daily")
                image3 = "{0}/{1}_chart_{2}.png".format(acct.charts_path, stock, "365_weekly")
                
                # setting the image to fit inside the column width is really wonky
                # to work around this, I'm setting it just outside my desired width
                scale = (1580 / 1718)

                rpt.insert_image('A1', image1, {'x_scale': scale, 'y_scale': scale})
                rpt.insert_image('A38', image2, {'x_scale': scale, 'y_scale': scale})
                rpt.insert_image('A73', image3, {'x_scale': scale, 'y_scale': scale})

                rpt.set_column("A:A", 198) # width not in pixels
                rpt.set_column("B:B", 4) # width not in pixels

                row = 1
                rpt.write('C{0}'.format(row), "Quality Score:")
                quality_score = acct.Fundamentals.quality_scores["quality_score"][stock]
                rpt.write('D{0}'.format(row), quality_score)

                row = row + 2
                rpt.write('C{0}'.format(row), "Shares Outstanding:")
                shares_outstanding = acct.Fundamentals.get_fundamental(stock).sharesOutstanding
                rpt.write('D{0}'.format(row), shares_outstanding, accounting_format)

                row = row+2
                rpt.write('C{0}'.format(row), "Average Daily Volume:")
                
                average_daily_volume = self.average_daily_volume(mycharts, stock)
                for date, record in average_daily_volume.tail(1).iterrows():
                    rpt.write('D{0}'.format(row),record['volume_1d_avg'], accounting_format)
                row = row+1
                for date, record in average_daily_volume.iterrows():
                    rpt.write('C{0}'.format(row),date.date(), date_format)
                    rpt.write('D{0}'.format(row),record['volume_20d_avg'], accounting_format)
                    row = row+1

                # TODO: I want to put, starting on column C1, print out of recent orders, transactions, and stops, as well as key ratios
                # TODO: I want to put in, if we have a file a notes akin to a journal.

                rpt.autofit()
                rpt.set_column("A:A", 198) # width not in pixels
                rpt.set_column("B:B", 4) # width not in pixels
                rpt.set_column("H:H", 17) # width not in pixels

            except xlsxwriter.exceptions.DuplicateWorksheetName as e:
                if "Sheetname" in str(e) and "is already in use" in str(e):
                    print(f"Worksheet '{stock}' already exists — skipping.")
                else:
                    raise  # re-raise if it's a different kind of error
            except xlsxwriter.exceptions.XlsxWriterException as e:
                if "Worksheet name" in str(e) and "is already in use" in str(e):
                    print(f"Worksheet '{stock}' already exists — skipping.")
                else:
                    raise  # re-raise if it's a different kind of error

    def write_portfolio_charts(self, acct, workbook):
        acct = cast(accounts.AccountsLauncher, acct)
        stock_list = acct.portfolio_symbols_list
        charts_file = acct.risk_calculator_charts_file
        mycharts = Charts.Charts(acct) # charting also needs acct.client
        # mycharts.export_stocklist(portfolio_symbols, charts_file)

        # GME+ is too young to have chart history, so manually skip it for the time being.
        try:
            stock_list.remove("GME+")
        except:
            print("GME+ not found")
        
        mycharts.generate_charts(stock_list)

        wbf = self.workbook_formats(workbook)
        accounting_format = wbf['accounting_format']
        # pct_format = wbf['pct_format']
        # bold_format = wbf['bold_format']
        # light_green_format = wbf['light_green_format']
        # light_yellow_format = wbf['light_yellow_format']
        plain_format = wbf['plain_format']
        date_format = wbf['date_format']

        for stock in stock_list:

            rpt = workbook.add_worksheet(stock)
            rpt.set_zoom(100)

            # TODO: I don't like hardcoding the file names here, come back an fix it
            image1 = "{0}/{1}_chart_{2}.png".format(acct.charts_path, stock, "1_day_30_minute")
            image2 = "{0}/{1}_chart_{2}.png".format(acct.charts_path, stock, "180_daily")
            image3 = "{0}/{1}_chart_{2}.png".format(acct.charts_path, stock, "365_weekly")
            
            # setting the image to fit inside the column width is really wonky
            # to work around this, I'm setting it just outside my desired width
            scale = (1580 / 1718)

            rpt.insert_image('A1', image1, {'x_scale': scale, 'y_scale': scale})
            rpt.insert_image('A38', image2, {'x_scale': scale, 'y_scale': scale})
            rpt.insert_image('A73', image3, {'x_scale': scale, 'y_scale': scale})


            # rpt.write('C1', balances.ShortOptionMarketValue, accounting_format)
                # acct = cast(accounts.AccountsLauncher, acct)
            
            symbolOrders = acct.get_symbol_orders(stock)
            row = 1
            if symbolOrders:
                filter_statuses = ['OPEN', 'PENDING_ACTIVATION', 'WORKING']
                rpt.write('C{0}'.format(row), "Order Id:")
                rpt.write('D{0}'.format(row), "Order Quantity:")
                rpt.write('E{0}'.format(row), "Price:")
                rpt.write('F{0}'.format(row), "Order Type:")
                rpt.write('G{0}'.format(row), "Status:")
                rpt.write('H{0}'.format(row), "Entered Time:")
                row = row+1
                # for pos in acct.SecuritiesAccount.Positions:
                #     pos = cast(position.Position, pos)

                for order in symbolOrders:
                # for order in filter(lambda o: o.status in filter_statuses, acct.Orders.Orders):
                
                    for orderLeg in filter(lambda ol: ol.instrument.symbol == stock,  order.OrderLegs):
                        orderLeg = cast(Orders.OrderLeg, orderLeg)
                        enteredTime = datetime.datetime.strptime(order.enteredTime, "%Y-%m-%dT%H:%M:%S%z").replace(tzinfo=None)

                        rpt.write('C{0}'.format(row), order.orderId, plain_format)
                        rpt.write('D{0}'.format(row), orderLeg.quantity)
                        rpt.write('E{0}'.format(row), order.price or order.stopPrice)
                        rpt.write('F{0}'.format(row), order.orderType)
                        rpt.write('G{0}'.format(row), order.status)
                        rpt.write('H{0}'.format(row), enteredTime, date_format)
                        row = row+1

            row = row+1
            rpt.write('C{0}'.format(row), "Quality Score:")
            quality_score = acct.Fundamentals.quality_scores["quality_score"][stock]
            rpt.write('D{0}'.format(row), quality_score)
            
            row = row + 2
            rpt.write('C{0}'.format(row), "Shares Outstanding:")
            shares_outstanding = acct.Fundamentals.get_fundamental(stock).sharesOutstanding
            rpt.write('D{0}'.format(row), shares_outstanding, accounting_format)

            row = row+2
            rpt.write('C{0}'.format(row), "Average Daily Volume:")
            
            average_daily_volume = self.average_daily_volume(mycharts, stock)
            for date, record in average_daily_volume.tail(1).iterrows():
                rpt.write('D{0}'.format(row),record['volume_1d_avg'], accounting_format)
            row = row+1
            for date, record in average_daily_volume.iterrows():
                rpt.write('C{0}'.format(row),date.date(), date_format)
                rpt.write('D{0}'.format(row),record['volume_20d_avg'], accounting_format)
                row = row+1

            rpt.autofit()
            rpt.set_column("A:A", 198) # width not in pixels
            rpt.set_column("B:B", 4) # width not in pixels
            rpt.set_column("H:H", 17) # width not in pixels


            # TODO: I want to put, starting on column C1, print out of recent orders, transactions, and stops, as well as key ratios
            # TODO: I want to put in, if we have a file a notes akin to a journal.


    def write_portfolio(self, acct, balances, workbook):
        # these castings aren't mandatory, but makes development easier
        acct = cast(accounts.AccountsLauncher, acct)
        sec_acct = cast(sec.SecuritiesAccount, acct.SecuritiesAccount)

        wbf = self.workbook_formats(workbook)
        accounting_format = wbf['accounting_format']
        pct_format = wbf['pct_format']
        bold_format = wbf['bold_format']
        light_green_format = wbf['light_green_format']
        light_yellow_format = wbf['light_yellow_format']


        rpt = workbook.add_worksheet("portfolio")

        # write portfolio headers
        rpt.write('A1', "Cash")
        rpt.write('B1', balances.CashBalance, accounting_format)
        rpt.set_column("B:B", 10.5) # width not in pixels
        rpt.write('A2', "Long Equity")
        rpt.write('B2', balances.LongMarketValue, accounting_format)
        rpt.write('A3', "Short Equity")
        rpt.write('B3', balances.ShortMarketValue, accounting_format)
        rpt.write('A4', "Long Options")
        rpt.write('B4', balances.LongOptionMarketValue, accounting_format)
        rpt.write('A5', "Short Options")
        rpt.write('B5', balances.ShortOptionMarketValue, accounting_format)

        rpt.write('D1', "Max Risk Per Trade")
        rpt.write('E1', balances.LiquidationValue * .01, accounting_format)
        # rpt.write('D2', "Max Available for Trade")
        # rpt.write('E2', balances.AvailableFunds, accounting_format)

        rpt.write('G1', "Net Liquidity")
        rpt.write('H1', balances.LiquidationValue, accounting_format)
        rpt.write('G2', "Max Available for Trade")
        rpt.write('H2', balances.AvailableFunds, accounting_format)
        rpt.write('G3', "Distance from Liquidation")
        rpt.write('H3', balances.LiquidationValue - 25000, accounting_format)
        
        rpt.write('J1', "Time of Report")
        rpt.write('K1', datetime.datetime.now())
        

        row = 6
        # this will make it much easier to maintain columns
        col_symbol                  = 'B'
        col_quantity                = 'C'
        col_mark                    = 'D'
        col_net_liquidity           = 'E'
        col_unrealized_profit_loss  = 'F'
        col_unrealized_profit_loss_pct  = 'G'
        col_break_even_point        = 'H'
        col_average_price           = 'I'
        col_underlying_price        = 'J'
        col_dte                     = 'K'
        col_max_return_on_risk      = 'L'
        col_q_ratio                 = 'M'
        col_csp_remaining_pct       = 'N'
        col_stop                    = 'O'
        col_live_risk_per_share     = 'P'
        col_live_risk               = 'Q'
        col_portfolio_pct           = 'R'
        # col_maximum_risk            = 'Q'
        col_profit_target_1         = 'S'
        col_profit_target_2         = 'T'
        col_profit_target_3         = 'U'
        
        rpt.write('{0}{1}'.format(col_symbol, row), "Symbol")
        rpt.write('{0}{1}'.format(col_quantity, row), "Quantity")
        rpt.write('{0}{1}'.format(col_mark, row), "Mark")
        rpt.write('{0}{1}'.format(col_net_liquidity, row), "Net Liquidity")
        rpt.write('{0}{1}'.format(col_unrealized_profit_loss, row), "uP&L")
        rpt.write('{0}{1}'.format(col_unrealized_profit_loss_pct, row), "uP&L %")
        rpt.write('{0}{1}'.format(col_break_even_point, row), 'Break Even Point')
        # rpt.write('{0}{1}'.format(col_qty_times_mark, row), 'Qty * Mark')
        rpt.write('{0}{1}'.format(col_average_price, row), 'Average Price')
        rpt.write('{0}{1}'.format(col_underlying_price, row), 'Underlying Price')
        rpt.write('{0}{1}'.format(col_dte, row), 'DTE')
        rpt.write('{0}{1}'.format(col_max_return_on_risk, row), 'RoR')
        rpt.write('{0}{1}'.format(col_q_ratio, row), 'Q Ratio')
        rpt.write('{0}{1}'.format(col_csp_remaining_pct, row), 'CSP Remaining Pct')
        rpt.write('{0}{1}'.format(col_stop, row), 'Stop')
        rpt.write('{0}{1}'.format(col_live_risk_per_share, row), 'Live Risk Per Share')
        rpt.write('{0}{1}'.format(col_live_risk, row), 'Live Risk')
        rpt.write('{0}{1}'.format(col_portfolio_pct, row), "% of portfolio")
        
        # rpt.write('{0}{1}'.format(col_maximum_risk, row), 'Max Value at Risk')
        rpt.write('{0}{1}'.format(col_profit_target_1, row), 'Profit Target 1')
        rpt.write('{0}{1}'.format(col_profit_target_2, row), 'Profit Target 2')
        rpt.write('{0}{1}'.format(col_profit_target_3, row), 'Profit Target 3')
        
        row = row+1
        

        total_live_risk = 0
        total_unrealized_profit_loss = 0
        sorted_by_symbol = sorted(sec_acct.Positions, key= lambda pos: pos.symbol)
        for pos in sorted_by_symbol:
            pos = cast(position.Position, pos)

            # This is where common initializers should go:
            break_even_point = None
            remaining_value = 0
            mark = None

            # TODO: this is too simplistic, and forgets that there might be multiple lots at different stops
            # for now, we just grab the first stop (without regard for which order is considered first)
            stopPrice =  self.get_first_stop(acct, pos.symbol)

            if(pos.instrument.AssetType == 'EQUITY' or pos.instrument.AssetType == 'COLLECTIVE_INVESTMENT'):
                
                mark = acct.get_symbol_quote(pos.symbol, 'mark')
                if mark is None:
                    mark = 0
                    live_risk_per_share = 0
                    unrealized_profit_loss = 0
                else:
                    # TODO: live_risk_per_share may give nonsensical values for a short position
                    if pos.LongOrShort == "LONG":
                        live_risk_per_share = (mark - stopPrice)
                        # TODO: this doesn't take into account real breakeven point, eg. dividends or premiums reducing real cost
                        unrealized_profit_loss = (mark - pos.averagePrice) * pos.Quantity
                        
                    elif pos.LongOrShort == "SHORT":
                        live_risk_per_share = max(0, (stopPrice - mark))
                        unrealized_profit_loss = (pos.averagePrice - mark) * pos.Quantity
                        
                    live_risk = live_risk_per_share * abs(pos.Quantity)
                    unrealized_profit_loss_pct = unrealized_profit_loss / (pos.averagePrice * pos.Quantity) * 100

                rpt.write('{0}{1}'.format(col_net_liquidity, row), pos.marketValue, accounting_format)
                
            if(pos.instrument.AssetType == 'OPTION'):
                opt = Options.position_option_chain(acct, pos)

                # underlying_mark = acct.client.get_quote(pos.instrument.underlyingSymbol).json()[pos.instrument.underlyingSymbol]['quote']['mark']
                underlying_mark = acct.get_symbol_quote(pos.instrument.underlyingSymbol, 'mark')
                underlying_ask =  acct.get_symbol_quote(pos.instrument.underlyingSymbol, 'askPrice')
                mark = opt.mark # * opt.multiplier


                # TODO: live_risk_per_share may give nonsensical values for a short position

                    # cash secured put, live_risk is we have to buy at strike,  
                if pos.LongOrShort == "LONG":
                    # if long call or long put, live risk is the same
                    live_risk_per_share = mark - stopPrice
                    unrealized_profit_loss = (mark - pos.averagePrice) * pos.Quantity * opt.multiplier
                    unrealized_profit_loss_pct = unrealized_profit_loss / (pos.averagePrice * pos.Quantity * opt.multiplier) * 100

                elif pos.LongOrShort == "SHORT":
                    unrealized_profit_loss = (pos.averagePrice - mark) * abs(pos.Quantity) * opt.multiplier
                    unrealized_profit_loss_pct = unrealized_profit_loss / (pos.averagePrice * abs(pos.Quantity) * opt.multiplier) * 100
                    if pos.instrument.putCall == Client.Options.ContractType.CALL:
                        if acct.is_it_naked(pos, opt):
                            # on a naked call, I have to buy shares at bid, and sell at strike.
                            # my risk is # shares * (strike - bid)
                            live_risk_per_share = (underlying_ask - opt.strikePrice)
                        else:
                            # on a covered call, I have to give up my shares. my risk is
                            # share price above strike price
                            live_risk_per_share = max(0, (underlying_mark - opt.strikePrice))

                    elif pos.instrument.putCall == Client.Options.ContractType.PUT:
                        live_risk_per_share = opt.strikePrice - stopPrice
                        remaining_value = (mark / pos.averagePrice) * 100
                
                break_even_point = acct.get_option_break_even_point(opt, pos.averagePrice)
                live_risk = live_risk_per_share * abs(pos.Quantity) * opt.multiplier
                
                # capital_at_risk_per_share = (opt.strikePrice - stopPrice)

                

                rpt.write('{0}{1}'.format(col_net_liquidity, row), opt.marketValue, accounting_format)                
                rpt.write('{0}{1}'.format(col_underlying_price, row), underlying_mark, accounting_format)
                rpt.write('{0}{1}'.format(col_dte, row), opt.daysToExpiration)
                # Q Ratio
                # TODO: I want a measure of whether the remaining premium is worth waiting for
                rpt.write('{0}{1}'.format(col_max_return_on_risk, row), opt.max_return_on_risk_pct, pct_format)
                rpt.write('{0}{1}'.format(col_q_ratio, row), opt.annualized_return_on_risk_pct, pct_format)
                rpt.write('{0}{1}'.format(col_csp_remaining_pct, row), remaining_value, pct_format)
                # TODO: I want to show the rate of return for the original contract sale
                # TODO: I want to show the rate of return for a roll.
                #   first, find the next available option to roll for
                #   second, find the bid price for that, and the ask price for the current dte
                #   third, calculate the difference in premium minus fees
                #   fourth, calculate the difference in dte
                #   lastly, we can now calculate the max rate of return

                

            # This is where common outputs for both should go:
            total_live_risk += live_risk
            total_unrealized_profit_loss += unrealized_profit_loss
            live_risk_percentage_of_portfolio = live_risk / balances.LiquidationValue * 100
            

            rpt.write('{0}{1}'.format(col_symbol, row), pos.symbol)
            rpt.write('{0}{1}'.format(col_quantity, row), pos.Quantity, accounting_format)
            rpt.write('{0}{1}'.format(col_mark, row), mark, accounting_format)
            rpt.write('{0}{1}'.format(col_unrealized_profit_loss, row), unrealized_profit_loss, accounting_format)
            rpt.write('{0}{1}'.format(col_unrealized_profit_loss_pct, row), unrealized_profit_loss_pct, pct_format)
            rpt.write('{0}{1}'.format(col_stop, row), stopPrice, accounting_format)
            rpt.write('{0}{1}'.format(col_average_price, row), pos.averagePrice, accounting_format)
            rpt.write('{0}{1}'.format(col_break_even_point, row), break_even_point, accounting_format)
            rpt.write('{0}{1}'.format(col_live_risk_per_share, row), live_risk_per_share, accounting_format)
            rpt.write('{0}{1}'.format(col_live_risk, row), live_risk, accounting_format)
            rpt.write('{0}{1}'.format(col_portfolio_pct, row), live_risk_percentage_of_portfolio, pct_format)
            
            if mark != 0:
                # quote informaiton is not available, so not able to calculate profit targets based off quote
                self.profit_targets(acct, workbook, rpt, pos, row, col_profit_target_1, col_profit_target_2, col_profit_target_3)
            row = row+1
                

        rpt.write('{0}1'.format(col_live_risk), "Total Live Risk", bold_format)
        rpt.write('{0}2'.format(col_live_risk), total_live_risk, accounting_format)
        rpt.write('{0}{1}'.format(col_unrealized_profit_loss, row), total_unrealized_profit_loss, bold_format)

        rpt.autofit()
        rpt.set_column("B:B", 21) # width not in pixels
        rpt.set_column("C:Z", 12) # width not in pixels
        rpt.set_zoom(135)

    def get_first_stop(self, acct, symbol):
        stopPrice =  acct.get_symbol_stop(symbol)
        if stopPrice:
            stopPrice = stopPrice[0]["stopPrice"]
        else:
            stopPrice = 0
        return stopPrice

    def profit_targets(self, acct, workbook, rpt, pos, row, col_profit_target_1, col_profit_target_2, col_profit_target_3):
        # these castings aren't mandatory, but makes development easier
        acct = cast(accounts.AccountsLauncher, acct)
        sec_acct = cast(sec.SecuritiesAccount, acct.SecuritiesAccount)

        wbf = self.workbook_formats(workbook)
        accounting_format = wbf['accounting_format']
        pct_format = wbf['pct_format']
        bold_format = wbf['bold_format']
        light_green_format = wbf['light_green_format']
        light_yellow_format = wbf['light_yellow_format']

        pos = cast(position.Position, pos)
            # This is where common initializers should go:
        break_even_point = None
        stopPrice = self.get_first_stop(acct, pos.symbol)
        

        if(pos.instrument.AssetType == 'EQUITY'):
            mark = acct.get_symbol_quote(pos.symbol, 'mark')
            if pos.LongOrShort == "LONG":
                if (stopPrice > pos.averageLongPrice):
                    profit_target_1 = mark + (mark - stopPrice)
                    profit_target_2 = mark + ((mark - stopPrice) * 2)
                    profit_target_3 = mark + ((mark - stopPrice) * 3)

                else:
                    profit_target_1 = pos.averagePrice + (pos.averagePrice - stopPrice)
                    profit_target_2 = pos.averagePrice + ((pos.averagePrice - stopPrice) * 2)
                    profit_target_3 = pos.averagePrice + ((pos.averagePrice - stopPrice) * 3)

                if(mark > profit_target_1):
                    rpt.write('{0}{1}'.format(col_profit_target_1, row), profit_target_1, light_green_format)
                else:
                    rpt.write('{0}{1}'.format(col_profit_target_1, row), profit_target_1, accounting_format)
                if(mark > profit_target_2):
                    rpt.write('{0}{1}'.format(col_profit_target_2, row), profit_target_2, light_green_format)
                else:
                    rpt.write('{0}{1}'.format(col_profit_target_2, row), profit_target_2, accounting_format)
                if(mark > profit_target_3):
                    rpt.write('{0}{1}'.format(col_profit_target_3, row), profit_target_3, light_green_format)
                else:
                    rpt.write('{0}{1}'.format(col_profit_target_3, row), profit_target_3, accounting_format)
            elif pos.LongOrShort == "SHORT":
                if (stopPrice > pos.averageShortPrice):
                    profit_target_1 = mark - (stopPrice - mark)
                    profit_target_2 = mark - ((stopPrice - mark) * 2)
                    profit_target_3 = mark - ((stopPrice - mark) * 3)

                else:
                    profit_target_1 = pos.averagePrice - (stopPrice - pos.averagePrice)
                    profit_target_2 = pos.averagePrice - ((stopPrice - pos.averagePrice) * 2)
                    profit_target_3 = pos.averagePrice - ((stopPrice - pos.averagePrice) * 3)
                if(mark < profit_target_1):
                    rpt.write('{0}{1}'.format(col_profit_target_1, row), profit_target_1, light_green_format)
                else:
                    rpt.write('{0}{1}'.format(col_profit_target_1, row), profit_target_1, accounting_format)
                if(mark < profit_target_2):
                    rpt.write('{0}{1}'.format(col_profit_target_2, row), profit_target_2, light_green_format)
                else:
                    rpt.write('{0}{1}'.format(col_profit_target_2, row), profit_target_2, accounting_format)
                if(mark < profit_target_3):
                    rpt.write('{0}{1}'.format(col_profit_target_3, row), profit_target_3, light_green_format)
                else:
                    rpt.write('{0}{1}'.format(col_profit_target_3, row), profit_target_3, accounting_format)
        
            if stopPrice == None or stopPrice == 0:
                rpt.write('{0}{1}'.format(col_profit_target_1, row), profit_target_1, light_yellow_format)
                rpt.write('{0}{1}'.format(col_profit_target_2, row), profit_target_2, light_yellow_format)
                rpt.write('{0}{1}'.format(col_profit_target_3, row), profit_target_3, light_yellow_format)
        if(pos.instrument.AssetType == 'OPTION'):
            opt = Options.position_option_chain(acct, pos)
            mark = opt.mark # * opt.multiplier

            if pos.LongOrShort == "LONG":
                profit_target_1 = pos.averagePrice + (pos.averagePrice - stopPrice)
                profit_target_2 = pos.averagePrice + ((pos.averagePrice - stopPrice) * 2)
                profit_target_3 = pos.averagePrice + ((pos.averagePrice - stopPrice) * 3)

                if(mark > profit_target_1):
                    rpt.write('{0}{1}'.format(col_profit_target_1, row), profit_target_1, light_green_format)
                else:
                    rpt.write('{0}{1}'.format(col_profit_target_1, row), profit_target_1, accounting_format)
                if(mark > profit_target_2):
                    rpt.write('{0}{1}'.format(col_profit_target_2, row), profit_target_2, light_green_format)
                else:
                    rpt.write('{0}{1}'.format(col_profit_target_2, row), profit_target_2, accounting_format)
                if(mark > profit_target_3):
                    rpt.write('{0}{1}'.format(col_profit_target_3, row), profit_target_3, light_green_format)
                else:
                    rpt.write('{0}{1}'.format(col_profit_target_3, row), profit_target_3, accounting_format)

            elif pos.LongOrShort == "SHORT":
                # TODO: profit targets on short options needs work
                profit_target_1 = pos.averagePrice - (stopPrice - pos.averagePrice)
                profit_target_2 = pos.averagePrice - ((stopPrice - pos.averagePrice) * 2)
                profit_target_3 = pos.averagePrice - ((stopPrice - pos.averagePrice) * 3)

                if(mark < profit_target_1):
                    rpt.write('{0}{1}'.format(col_profit_target_1, row), profit_target_1, light_green_format)
                else:
                    rpt.write('{0}{1}'.format(col_profit_target_1, row), profit_target_1, accounting_format)
                if(mark < profit_target_2):
                    rpt.write('{0}{1}'.format(col_profit_target_2, row), profit_target_2, light_green_format)
                else:
                    rpt.write('{0}{1}'.format(col_profit_target_2, row), profit_target_2, accounting_format)
                if(mark < profit_target_3):
                    rpt.write('{0}{1}'.format(col_profit_target_3, row), profit_target_3, light_green_format)
                else:
                    rpt.write('{0}{1}'.format(col_profit_target_3, row), profit_target_3, accounting_format)

            # if stopPrice == None or stopPrice == 0:
            #     rpt.write('{0}{1}'.format(col_profit_target_1, row), profit_target_1, light_yellow_format)
            #     rpt.write('{0}{1}'.format(col_profit_target_2, row), profit_target_2, light_yellow_format)
            #     rpt.write('{0}{1}'.format(col_profit_target_3, row), profit_target_3, light_yellow_format)
            # else:

    def write_notes(self, workbook):
        rpt = workbook.add_worksheet("disclosures")
        rpt.write('A1', "See disclosures in the config, there are some caveats in the reasonability of the calculations.")


    def workbook_formats(self, workbook):
        accounting_format = workbook.add_format({'num_format': '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)'})
        pct_format = workbook.add_format({'num_format': '_(* #,##0.0000_);_(* (#,##0.0000);_(* "-"??_);_(@_)'})
        plain_format = workbook.add_format({'num_format': '0'})
        date_format = workbook.add_format({'num_format': 'yyyy-mm-dd hh:mm:ss'})
        bold_format = workbook.add_format({'bold': True, 'num_format': '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)'})
        light_green_format = workbook.add_format({
            'bg_color': '#C6EFCE',  # Light green hex
            'font_color': '#006100', # Optional: dark green text
            'num_format': '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)' # accounting format
        })
        light_yellow_format = workbook.add_format({
            'bg_color': '#FFF2CC',     # Light yellow background
            'font_color': '#7F6000',   # Dark yellow/brownish font
            'num_format': '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)' # accounting format
        })
        return {
            'accounting_format': accounting_format,
             'pct_format': pct_format,
             'bold_format': bold_format,
             'light_green_format': light_green_format,
             'light_yellow_format': light_yellow_format,
             'plain_format': plain_format,
             'date_format': date_format
             }


    def parse_args(self):
        #todo:
        print("if any arguments, implement this")
    
    # def read_config(self):
    #     self.config = conf.get_config()
    #     self.securities_account_file = self.config['AppConfig']['securities_account_file'].replace('<date>',str(datetime.date.today()))
    #     self.transactions_file = self.config['AppConfig']['transactions_file'].replace('<date>',str(datetime.date.today()))
    
    def average_daily_volume(self, mycharts, symbol):
        save_file = './data/price_history/{0}_180_daily_{1}.json'.format(symbol,str(datetime.date.today()))
        df = mycharts.price_history_to_dataframe(save_file)
        # df.to_csv(save_file.replace(".json", ".csv"), index=True)
        return df.tail(20)

    # def daily_volume(self, mycharts, symbol):
    #     save_file = './data/price_history/{0}_180_daily_{1}.json'.format(symbol,str(datetime.date.today()))
    #     df = mycharts.price_history_to_dataframe(save_file)
    #     # df.to_csv(save_file.replace(".json", ".csv"), index=True)
    #     return df.tail(20)


    def run(self):
        print("hello")



def run():
    launcher = RiskCalculator()
    # launcher.start()
    # launcher.run()

if __name__ == '__main__':
    # if RUN_ARGS.getboolean('profile'):
    #     import cProfile
    #     cProfile.run('main()', sort='tottime')
    # else:
    #     main()
    # main()
    run()