import mplfinance as fplt
from schwab.client import Client
import pandas as pd
import datetime
import json
from typing import cast
import accounts.accounts as accounts
import accounts.position as position
import mplfinance as mpf
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import datetime
import numpy as np

class Charts():
    def __init__(self, account):
        self.account = cast(accounts.AccountsLauncher, account)
        self.client = account.client
        self.path = self.account.config['Charting']['charts_path']
        
# TODO: abstract away the methods for getting various price histories, and save to file for historical analysis
# TODO: build charts from downloaded files instead of directly from client api (this will make the code more modular)
        # Valid values
        # 'When periodType=day valid values for period are: [1, 2, 3, 4, 5, 10]'
        # 'When periodType=day valid values for frequencyType are: minute'


    # def print_15_mins(self, symbol):
    #     # FIXME: there is a bug here, if market is closed when this is run, we will get an error, because the response will have no candles.
    #     earliest_date = datetime.datetime.now() - datetime.timedelta(days=1)
    #     price_history = self.client.get_price_history_every_fifteen_minutes(symbol, start_datetime=earliest_date).json()

    #     df = self.price_history_to_dataframe(price_history, "15_mins")

    #     self.my_plot_settings(symbol, df)

    # def print_90_day_30_mins(self, symbol):
    #     earliest_date = datetime.datetime.now() - datetime.timedelta(days=90)
    #     price_history = self.client.get_price_history_every_thirty_minutes(symbol, start_datetime=earliest_date).json()

    #     df = self.price_history_to_dataframe(price_history, "90_day_30_min")

    #     self.my_plot_settings(symbol, df)

    def print_1_day_30_minute(self, symbol):
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(hours=12)
        
        period_type = Client.PriceHistory.PeriodType.DAY
        # period = Client.PriceHistory.Period.ONE_DAY
        frequency_type = Client.PriceHistory.FrequencyType.MINUTE
        frequency = Client.PriceHistory.Frequency.EVERY_THIRTY_MINUTES

        price_history = self.client.get_price_history(
            symbol=symbol,
            period_type=period_type,         # 'day' allows intraday data
            frequency_type=frequency_type,   # minute-level granularity
            frequency=frequency,               # 1-minute intervals
            start_datetime=start_date,
            end_datetime=end_date,
            need_extended_hours_data=False        # Optional: include pre/post-market
        ).json()

        save_file = self.account.price_history_output_file.replace("<symbol>", symbol + "_1_day_30_minute")
        with open(save_file, 'w') as json_file:
            json.dump(price_history, json_file)

        df = self.price_history_to_dataframe(price_history)

        self.plot_settings_30_minute_candles(symbol, df, "1_day_30_minute")
        
    def print_180_daily(self, symbol):
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=180)
        
        period_type = Client.PriceHistory.PeriodType.MONTH
        # period = Client.PriceHistory.Period.ONE_DAY
        frequency_type = Client.PriceHistory.FrequencyType.DAILY
        frequency = Client.PriceHistory.Frequency.DAILY

        price_history = self.client.get_price_history(
            symbol=symbol,
            period_type=period_type,         # 'day' allows intraday data
            frequency_type=frequency_type,   # minute-level granularity
            frequency=frequency,               # 1-minute intervals
            start_datetime=start_date,
            end_datetime=end_date,
            need_extended_hours_data=False        # Optional: include pre/post-market
        ).json()

        save_file = self.account.price_history_output_file.replace("<symbol>", symbol + "_180_daily")
        with open(save_file, 'w') as json_file:
            json.dump(price_history, json_file)

        df = self.price_history_to_dataframe(price_history)

        self.plot_settings_default(symbol, df, "180_daily") 

    def print_365_weekly(self, symbol):
        earliest_date = datetime.datetime.now() - datetime.timedelta(days=366)
        price_history = self.client.get_price_history_every_week(symbol, start_datetime=earliest_date).json()
        save_file = self.account.price_history_output_file.replace("<symbol>", symbol + "_365_week")
        with open(save_file, 'w') as json_file:
            json.dump(price_history, json_file)


        df = self.price_history_to_dataframe(price_history)

        self.plot_settings_default(symbol, df, "365_weekly")

        return df

    def price_history_to_dataframe(self, price_history):
        df = pd.DataFrame(price_history['candles'], columns=['open', 'high', 'low', 'close', 'volume', 'datetime'])
        df['datetime'] = df['datetime'].apply(self.date_transform)
        # df = df.set_index('datetime')
        df.set_index('datetime', inplace=True)
        df.index.name = 'Date'
        df.shape
        df.head(3)
        df.tail(3)
        return df

    def plot_settings_minute_candles(self, symbol, df, timeframe):
        right_now = datetime.datetime.now()
        month = right_now.strftime("%B")
        year = right_now.year

        # Compute price range to scale tick spacing
        price_min, price_max = df['low'].min(), df['high'].max()
        price_range = price_max - price_min

        # Determine tick spacing
        if price_range <= .5:
            # For tight ranges, show granular ticks
            tick_spacing = 0.01  # one cent
        elif price_range <= 1:
            # For tight ranges, show granular ticks
            tick_spacing = 0.02  # two cents
        elif price_range <= 2:
            tick_spacing = 0.05
        else:
            # Rule of thumb: aim for ~12 gridlines
            raw_spacing = np.round(price_range / 12, 2)
            nice_ticks = [0.05, 0.10, 0.25, 0.5, 1, 2, 5, 10, 20]
            tick_spacing = min(nice_ticks, key=lambda x: abs(x - raw_spacing))

        fig, axes = mpf.plot(
            df,
            type='candle',
            style='charles',
            returnfig=True,
            figsize=(21, 8),
            # datetime_format=' %Y-%m-%d',
            datetime_format=' %Y-%m-%d %H:%M',
            xrotation=90,
            title=f"{symbol}, {month} - {year}\n{timeframe}",
            ylabel='Price ($)'
        )

        ax1 = axes[0]
        ax1.yaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))

        # these values work ok for minute ticks
        ax1.xaxis.set_major_locator(ticker.IndexLocator(60,1))
        ax1.xaxis.set_minor_locator(ticker.IndexLocator(15,1))

        ax1.grid(True, which='both', axis='y', linestyle='--', color='gray')
        ax1.grid(True, which='both', axis='x', linestyle='--', color='gray')

        fig.savefig(f"{self.path}/{symbol}_chart_{timeframe}.png", dpi=96, bbox_inches="tight")

    def plot_settings_15_minute_candles(self, symbol, df, timeframe):
        right_now = datetime.datetime.now()
        month = right_now.strftime("%B")
        year = right_now.year

        # Compute price range to scale tick spacing
        price_min, price_max = df['low'].min(), df['high'].max()
        price_range = price_max - price_min

        # Determine tick spacing
        if price_range <= .5:
            # For tight ranges, show granular ticks
            tick_spacing = 0.01  # one cent
        elif price_range <= 1:
            # For tight ranges, show granular ticks
            tick_spacing = 0.02  # two cents
        elif price_range <= 2:
            tick_spacing = 0.05
        else:
            # Rule of thumb: aim for ~12 gridlines
            raw_spacing = np.round(price_range / 12, 2)
            nice_ticks = [0.05, 0.10, 0.25, 0.5, 1, 2, 5, 10, 20]
            tick_spacing = min(nice_ticks, key=lambda x: abs(x - raw_spacing))

        fig, axes = mpf.plot(
            df,
            type='candle',
            style='charles',
            returnfig=True,
            figsize=(21, 8),
            # datetime_format=' %Y-%m-%d',
            datetime_format=' %Y-%m-%d %H:%M',
            xrotation=90,
            title=f"{symbol}, {month} - {year}\n{timeframe}",
            ylabel='Price ($)'
        )

        ax1 = axes[0]
        ax1.yaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))

        # these values work ok for 15 minute ticks
        ax1.xaxis.set_major_locator(ticker.IndexLocator(4,1))
        ax1.xaxis.set_minor_locator(ticker.IndexLocator(1,1))

        ax1.grid(True, which='both', axis='y', linestyle='--', color='gray')
        ax1.grid(True, which='both', axis='x', linestyle='--', color='gray')

        fig.savefig(f"{self.path}/{symbol}_chart_{timeframe}.png", dpi=96, bbox_inches="tight")

    def plot_settings_30_minute_candles(self, symbol, df, timeframe):
        right_now = datetime.datetime.now()
        month = right_now.strftime("%B")
        year = right_now.year

        # Compute price range to scale tick spacing
        price_min, price_max = df['low'].min(), df['high'].max()
        price_range = price_max - price_min

        # Compute price range to scale tick spacing
        price_min, price_max = df['low'].min(), df['high'].max()
        price_range = price_max - price_min

        # Determine tick spacing
        if price_range <= .5:
            # For tight ranges, show granular ticks
            tick_spacing = 0.01  # one cent
        elif price_range <= 1:
            # For tight ranges, show granular ticks
            tick_spacing = 0.02  # two cents
        elif price_range <= 2:
            tick_spacing = 0.05
        else:
            # Rule of thumb: aim for ~12 gridlines
            raw_spacing = np.round(price_range / 12, 2)
            nice_ticks = [0.05, 0.10, 0.25, 0.5, 1, 2, 5, 10, 20]
            tick_spacing = min(nice_ticks, key=lambda x: abs(x - raw_spacing))

        fig, axes = mpf.plot(
            df,
            type='candle',
            style='charles',
            returnfig=True,
            figsize=(21, 8),
            # datetime_format=' %Y-%m-%d',
            datetime_format=' %Y-%m-%d %H:%M',
            xrotation=90,
            title=f"{symbol}, {month} - {year}\n{timeframe}",
            ylabel='Price ($)'
        )

        ax1 = axes[0]
        ax1.yaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))

        # these values work ok for 15 minute ticks
        ax1.xaxis.set_major_locator(ticker.IndexLocator(2,1))
        ax1.xaxis.set_minor_locator(ticker.IndexLocator(1,1))

        ax1.grid(True, which='both', axis='y', linestyle='--', color='gray')
        ax1.grid(True, which='both', axis='x', linestyle='--', color='gray')

        fig.savefig(f"{self.path}/{symbol}_chart_{timeframe}.png", dpi=96, bbox_inches="tight")

    def plot_settings_default(self, symbol, df, timeframe):
        right_now = datetime.datetime.now()
        month = right_now.strftime("%B")
        year = right_now.year

        # Compute price range to scale tick spacing
        price_min, price_max = df['low'].min(), df['high'].max()
        price_range = price_max - price_min

        # Determine tick spacing
        if price_range <= .5:
            # For tight ranges, show granular ticks
            tick_spacing = 0.01  # one cent
        elif price_range <= 1:
            # For tight ranges, show granular ticks
            tick_spacing = 0.02  # two cents
        elif price_range <= 2:
            tick_spacing = 0.05
        else:
            # Rule of thumb: aim for ~12 gridlines
            raw_spacing = np.round(price_range / 12, 2)
            nice_ticks = [0.05, 0.10, 0.25, 0.5, 1, 2, 5, 10, 20]
            tick_spacing = min(nice_ticks, key=lambda x: abs(x - raw_spacing))

        fig, axes = mpf.plot(
            df,
            type='candle',
            style='charles',
            returnfig=True,
            figsize=(21, 8),
            datetime_format=' %Y-%m-%d',
            # datetime_format=' %Y-%m-%d %H:%M',
            xrotation=90,
            title=f"{symbol}, {month} - {year}\n{timeframe}",
            ylabel='Price ($)'
        )

        ax1 = axes[0]

        # Apply scaled horizontal gridlines
        ax1.yaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
        ax1.xaxis.set_major_locator(ticker.IndexLocator(5,0))
        ax1.xaxis.set_minor_locator(mdates.DayLocator())

        ax1.grid(True, which='major', axis='y', linestyle='--', color='gray')
        self.plot_stop_price(symbol, ax1)
        self.plot_average_price(symbol, ax1)
        self.plot_option_strike(symbol, ax1)
        fig.savefig(f"{self.path}/{symbol}_chart_{timeframe}.png", dpi=96, bbox_inches="tight")

    def date_transform(self, datetime_data):
        timestamp = datetime_data/1000
        return datetime.datetime.fromtimestamp(timestamp)
    
    def chart_my_watchlist(self, acct, chart_file): 
        watchlist = acct.get_watchlist()
        charts_file = acct.charts_file
        
        self.export_stocklist(self, watchlist, charts_file)

    def generate_charts(self, stock_list):
        for stock in stock_list:
            # we don't actually need the data frames here, we're just interested in the image
            self.print_180_daily(stock)
            self.print_365_weekly(stock)
            self.print_1_day_30_minute(stock)

    def plot_stop_price(self, symbol, ax1):
        stop_price = self.account.get_symbol_stop(symbol)
        if stop_price:
            # Plot horizontal line for stop price
            ax1.axhline(
                y=stop_price,
                color='red',
                linestyle='--',
                linewidth=1.5,
                label=f'Stop @ ${stop_price:.2f}'
            )

            # Optional: show legend
            ax1.legend(loc='lower left')

    def plot_average_price(self, symbol, ax1):
        average_price = self.account.get_symbol_average_price(symbol)
        if average_price:
            # Plot horizontal line for stop price
            ax1.axhline(
                y=average_price,
                color='green',
                linestyle='--',
                linewidth=1.5,
                label=f'Average Price @ ${average_price:.2f}'
            )

            # Optional: show legend
            ax1.legend(loc='lower left')

    def plot_option_strike(self, symbol, ax1):
        # stop_price = self.account.get_symbol_stop(symbol)

        symbolOptions = self.account.get_symbol_options(symbol)
        for pos in symbolOptions:
            pos = cast(position.Position, pos)

            print(pos.symbol, pos.instrument.strike, pos.LongOrShort, pos.instrument.putCall)
            strikePrice = pos.instrument.strike

            label = "{0}{1}".format(strikePrice, pos.instrument.putCall.name)
            # TODO: add some conditions to format the strike lines
            ax1.axhline(
                y=strikePrice,
                color='red',
                linestyle='--',
                linewidth=1.5,
                label=label
            )

            # Optional: show legend
            ax1.legend(loc='lower left')

    def export_stocklist(self, stock_list, charts_file):
        # due to timeouts with the ExcelWriter, we're grabbing all the charts in one loop
        # and then writing them to Excel in a second loop
        self.generate_charts(stock_list)

        with pd.ExcelWriter(charts_file, engine="xlsxwriter") as writer:
            writer.book.set_size(2620, 1820)
            for stock in stock_list:
                # abuse a blank data frame to create worksheet
                df_blank = pd.DataFrame()
                df_blank.to_excel(writer, sheet_name=stock)

                worksheet = writer.sheets[stock]
                worksheet.set_zoom(100)

                image1 = "{0}/{1}_chart_{2}.png".format(self.path, stock, "180_daily")
                image2 = "{0}/{1}_chart_{2}.png".format(self.path, stock, "365_weekly")
                
                # setting the image to fit inside the column width is really wonky
                # to work around this, I'm setting it just outside my desired width
                scale = (1580 / 1718)

                worksheet.insert_image('A1', image1, {'x_scale': scale, 'y_scale': scale})
                worksheet.insert_image('A36', image2, {'x_scale': scale, 'y_scale': scale})

                worksheet.set_column("A:A", 198) # width not in pixels
                worksheet.set_column("B:B", 1) # width not in pixels

