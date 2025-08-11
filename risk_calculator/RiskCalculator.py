from schwab import auth
from schwab.client import Client
import json
import csv
import conf
import json_to_csv
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

            self.write_notes(workbook)
        




        print("done something")



    def write_watchlist(self, acct, workbook):
        acct = cast(accounts.AccountsLauncher, acct)
        # sec_acct = cast(sec.SecuritiesAccount, acct.SecuritiesAccount)

        wbf = self.workbook_formats(workbook)
        accounting_format = wbf['accounting_format']
        pct_format = wbf['pct_format']
        bold_format = wbf['bold_format']

        watchlist = acct.get_watchlist()

    def write_portfolio_charts(self, acct, workbook):
        acct = cast(accounts.AccountsLauncher, acct)
        stock_list = acct.get_account_symbols()
        charts_file = acct.risk_calculator_charts_file
        mycharts = Charts.Charts(acct) # charting also needs acct.client
        # mycharts.export_stocklist(portfolio_symbols, charts_file)

        mycharts.generate_charts(stock_list)

        # with pd.ExcelWriter(charts_file, engine="xlsxwriter") as writer:
        #     writer.book.set_size(2620, 1820)
        for stock in stock_list:
            # abuse a blank data frame to create worksheet
            # df_blank = pd.DataFrame()
            # df_blank.to_excel(writer, sheet_name=stock)
            rpt = workbook.add_worksheet(stock)
            # worksheet = writer.sheets[stock]
            rpt.set_zoom(100)

            image1 = "{0}/{1}_chart_{2}.png".format(acct.charts_path, stock, "10_day")
            image2 = "{0}/{1}_chart_{2}.png".format(acct.charts_path, stock, "180_daily")
            image3 = "{0}/{1}_chart_{2}.png".format(acct.charts_path, stock, "365_weekly")
            
            # setting the image to fit inside the column width is really wonky
            # to work around this, I'm setting it just outside my desired width
            scale = (1580 / 1718)

            rpt.insert_image('A1', image1, {'x_scale': scale, 'y_scale': scale})
            rpt.insert_image('A36', image2, {'x_scale': scale, 'y_scale': scale})
            rpt.insert_image('A73', image3, {'x_scale': scale, 'y_scale': scale})

            rpt.set_column("A:A", 198) # width not in pixels
            rpt.set_column("B:B", 1) # width not in pixels


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


        rpt = workbook.add_worksheet("portfolio")
        rpt.set_zoom(135)
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

        rpt.write('D1', "Net Liquidity")
        rpt.write('E1', balances.LiquidationValue, accounting_format)
        rpt.write('D2', "Max Available for Trade")
        rpt.write('E2', balances.AvailableFunds, accounting_format)
        
        row = 6
        # this will make it much easier to maintain columns
        col_symbol                  = 'B'
        col_quantity                = 'C'
        col_mark                    = 'D'
        col_net_liquidity           = 'E'
        col_unrealized_profit_loss  = 'F'
        col_break_even_point        = 'G'
        col_average_price           = 'H'
        col_underlying_price        = 'I'
        col_dte                     = 'J'
        col_max_return_on_risk      = 'K'
        col_q_ratio                 = 'L'
        col_stop                    = 'M'
        col_live_risk_per_share     = 'N'
        col_live_risk               = 'O'
        col_portfolio_pct           = 'P'
        col_maximum_risk            = 'Q'
        # col_qty_times_mark        = 'F'
        
        rpt.write('{0}{1}'.format(col_symbol, row), "Symbol")
        rpt.write('{0}{1}'.format(col_quantity, row), "Quantity")
        rpt.write('{0}{1}'.format(col_mark, row), "Mark")
        rpt.write('{0}{1}'.format(col_net_liquidity, row), "Net Liquidity")
        rpt.write('{0}{1}'.format(col_unrealized_profit_loss, row), "uP&L")
        rpt.write('{0}{1}'.format(col_break_even_point, row), 'Break Even Point')
        # rpt.write('{0}{1}'.format(col_qty_times_mark, row), 'Qty * Mark')
        rpt.write('{0}{1}'.format(col_average_price, row), 'Average Price')
        rpt.write('{0}{1}'.format(col_underlying_price, row), 'Underlying Price')
        rpt.write('{0}{1}'.format(col_dte, row), 'DTE')
        rpt.write('{0}{1}'.format(col_max_return_on_risk, row), 'RoR')
        rpt.write('{0}{1}'.format(col_q_ratio, row), 'Q Ratio')
        rpt.write('{0}{1}'.format(col_stop, row), 'Stop')
        rpt.write('{0}{1}'.format(col_live_risk_per_share, row), 'Live Risk Per Share')
        rpt.write('{0}{1}'.format(col_live_risk, row), 'Live Risk')
        rpt.write('{0}{1}'.format(col_portfolio_pct, row), "% of portfolio")
        
        rpt.write('{0}{1}'.format(col_maximum_risk, row), 'Max Value at Risk')
        
        row = row+1
        

        total_live_risk = 0
        sorted_by_symbol = sorted(sec_acct.Positions, key= lambda pos: pos.symbol)
        for pos in sorted_by_symbol:
            pos = cast(position.Position, pos)

            if(pos.instrument.AssetType == 'EQUITY'):
                break_even_point = None
                mark = acct.get_symbol_quote(pos.symbol, 'mark')
                stopPrice = acct.get_symbol_stop(pos.symbol)
                # TODO: live_risk_per_share may give nonsensical values for a short position
                if pos.LongOrShort == "LONG":
                    live_risk_per_share = (mark - stopPrice)
                    # TODO: this doesn't take into account real breakeven point, eg. dividends or premiums reducing real cost
                    unrealized_profit_loss = (mark - pos.averagePrice) * pos.Quantity
                elif pos.LongOrShort == "SHORT":
                    live_risk_per_share = max(0, (stopPrice - mark))
                    unrealized_profit_loss = (pos.averagePrice - mark) * pos.Quantity
                live_risk = live_risk_per_share * abs(pos.Quantity)
                total_live_risk += live_risk
                live_risk_percentage_of_portfolio = live_risk / balances.LiquidationValue * 100
                

                rpt.write('{0}{1}'.format(col_symbol, row), pos.symbol)
                rpt.write('{0}{1}'.format(col_quantity, row), pos.Quantity, accounting_format)
                rpt.write('{0}{1}'.format(col_mark, row), mark, accounting_format)
                rpt.write('{0}{1}'.format(col_net_liquidity, row), pos.marketValue, accounting_format)
                rpt.write('{0}{1}'.format(col_unrealized_profit_loss, row), unrealized_profit_loss, accounting_format)
                rpt.write('{0}{1}'.format(col_break_even_point, row), break_even_point, accounting_format)
                # rpt.write('{0}{1}'.format(col_qty_times_mark, row), "=C{0}*D{0}".format(str(row)), accounting_format)
                rpt.write('{0}{1}'.format(col_average_price, row), pos.averagePrice, accounting_format)
                rpt.write('{0}{1}'.format(col_stop, row), stopPrice, accounting_format)
                rpt.write('{0}{1}'.format(col_live_risk_per_share, row), live_risk_per_share, accounting_format)
                rpt.write('{0}{1}'.format(col_live_risk, row), live_risk, accounting_format)
                rpt.write('{0}{1}'.format(col_portfolio_pct, row), live_risk_percentage_of_portfolio, pct_format)
                
                
                

                row = row+1
            if(pos.instrument.AssetType == 'OPTION'):
                opt = Options.position_option_chain(acct, pos)
                break_even_point = None
                # underlying_mark = acct.client.get_quote(pos.instrument.underlyingSymbol).json()[pos.instrument.underlyingSymbol]['quote']['mark']
                underlying_mark = acct.get_symbol_quote(pos.instrument.underlyingSymbol, 'mark')
                underlying_ask =  acct.get_symbol_quote(pos.instrument.underlyingSymbol, 'askPrice')
                mark = opt.mark # * opt.multiplier

                stopPrice = acct.get_symbol_stop(pos.symbol)
                # TODO: live_risk_per_share may give nonsensical values for a short position

                    # cash secured put, live_risk is we have to buy at strike,  
                if pos.LongOrShort == "LONG":
                    # if long call or long put, live risk is the same
                    live_risk_per_share = mark - stopPrice
                    unrealized_profit_loss = (mark - pos.averagePrice) * pos.Quantity * opt.multiplier
                
                elif pos.LongOrShort == "SHORT":
                    unrealized_profit_loss = (pos.averagePrice - mark) * abs(pos.Quantity) * opt.multiplier
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
                break_even_point = acct.get_break_even_point(opt, pos.averagePrice)


                live_risk = live_risk_per_share * abs(pos.Quantity) * opt.multiplier
                total_live_risk += live_risk
                live_risk_percentage_of_portfolio = live_risk / balances.LiquidationValue * 100
                
                # capital_at_risk_per_share = (opt.strikePrice - stopPrice)


                rpt.write('{0}{1}'.format(col_symbol, row), pos.symbol)
                rpt.write('{0}{1}'.format(col_quantity, row), pos.Quantity, accounting_format)
                rpt.write('{0}{1}'.format(col_mark, row), mark, accounting_format)
                rpt.write('{0}{1}'.format(col_net_liquidity, row), opt.marketValue, accounting_format)
                rpt.write('{0}{1}'.format(col_unrealized_profit_loss, row), unrealized_profit_loss, accounting_format)
                rpt.write('{0}{1}'.format(col_break_even_point, row), break_even_point, accounting_format)
                # rpt.write('{0}{1}'.format(col_qty_times_mark, row), "=C{0}*D{0}".format(str(row)), accounting_format)
                rpt.write('{0}{1}'.format(col_average_price, row), pos.averagePrice, accounting_format)
                # option columns
                rpt.write('{0}{1}'.format(col_underlying_price, row), underlying_mark, accounting_format)
                rpt.write('{0}{1}'.format(col_dte, row), opt.daysToExpiration)
                # Q Ratio
                # TODO: I want a measure of whether the remaining premium is worth waiting for
                rpt.write('{0}{1}'.format(col_max_return_on_risk, row), opt.max_return_on_risk_pct, pct_format)
                rpt.write('{0}{1}'.format(col_q_ratio, row), opt.annualized_return_on_risk_pct, pct_format)
                # TODO: I want to show the rate of return for the original contract sale
                # TODO: I want to show the rate of return for a roll.
                #   first, find the next available option to roll for
                #   second, find the bid price for that, and the ask price for the current dte
                #   third, calculate the difference in premium minus fees
                #   fourth, calculate the difference in dte
                #   lastly, we can now calculate the max rate of return

                # Stop
                rpt.write('{0}{1}'.format(col_stop, row), stopPrice, accounting_format)
                rpt.write('{0}{1}'.format(col_live_risk_per_share, row), live_risk_per_share, accounting_format)
                rpt.write('{0}{1}'.format(col_live_risk, row), live_risk, accounting_format)
                # %% of portfolio
                rpt.write('{0}{1}'.format(col_portfolio_pct, row), live_risk_percentage_of_portfolio, pct_format)
                rpt.write('{0}{1}'.format(col_unrealized_profit_loss, row), unrealized_profit_loss, accounting_format)



                row = row+1


        rpt.write('{0}1'.format(col_live_risk), "Total Live Risk", bold_format)
        rpt.write('{0}2'.format(col_live_risk), total_live_risk, accounting_format)

        rpt.autofit()
        rpt.set_column("B:B", 21) # width not in pixels
        rpt.set_column("C:Z", 12) # width not in pixels
        rpt.set_zoom(100)


    def write_notes(self, workbook):
        rpt = workbook.add_worksheet("disclosures")
        rpt.write('A1', "See disclosures in the config, there are some caveats in the reasonability of the calculations.")


    def workbook_formats(self, workbook):
        accounting_format = workbook.add_format({'num_format': '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)'})
        pct_format = workbook.add_format({'num_format': '_(* #,##0.0000_);_(* (#,##0.0000);_(* "-"??_);_(@_)'})
        bold_format = workbook.add_format({'bold': True})

        return {
            'accounting_format': accounting_format,
             'pct_format': pct_format,
             'bold_format': bold_format
             }


    def parse_args(self):
        #todo:
        print("if any arguments, implement this")
    
    # def read_config(self):
    #     self.config = conf.get_config()
    #     self.securities_account_file = self.config['AppConfig']['securities_account_file'].replace('<date>',str(datetime.date.today()))
    #     self.transactions_file = self.config['AppConfig']['transactions_file'].replace('<date>',str(datetime.date.today()))
    




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