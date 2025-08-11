import mplfinance as fplt
from schwab.client import Client
import pandas as pd
import datetime
import json

import mplfinance as mpf
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import datetime
import numpy as np

class Charts():
    def __init__(self, account):
        self.account = account
        self.client = account.client
        self.path = self.account.config['Charting']['charts_path']
        
# TODO: abstract away the methods for getting various price histories, and save to file for historical analysis
# TODO: build charts from downloaded files instead of directly from client api (this will make the code more modular)


    def print_15_mins(self, symbol):
        # FIXME: there is a bug here, if market is closed when this is run, we will get an error, because the response will have no candles.
        earliest_date = datetime.datetime.now() - datetime.timedelta(days=1)
        price_history = self.client.get_price_history_every_fifteen_minutes(symbol, start_datetime=earliest_date).json()

        df = self.price_history_to_dataframe(price_history, "15_mins")

        self.my_plot_settings(symbol, df)

    def print_90_day_30_mins(self, symbol):
        earliest_date = datetime.datetime.now() - datetime.timedelta(days=90)
        price_history = self.client.get_price_history_every_thirty_minutes(symbol, start_datetime=earliest_date).json()

        df = self.price_history_to_dataframe(price_history, "90_day_30_min")

        self.my_plot_settings(symbol, df)

    def print_10_day(self, symbol):
        earliest_date = datetime.datetime.now() - datetime.timedelta(days=90)

        period_type = Client.PriceHistory.PeriodType.DAY
        period = Client.PriceHistory.Period.ONE_DAY
        frequency_type = Client.PriceHistory.FrequencyType.MINUTE
        # frequency = Client.PriceHistory.Frequency.EVERY_MINUTE
    
        # price_history = self.client.get_price_history(symbol, period_type=period_type, period=period, frequency_type=frequency_type, frequency=frequency).json()

        # save_file = self.account.price_history_output_file.replace("<symbol>", symbol)
        # with open(save_file, 'w') as json_file:
        #     json.dump(price_history, json_file)

        frequency = Client.PriceHistory.Frequency.EVERY_FIFTEEN_MINUTES
        price_history = self.client.get_price_history(symbol, period_type=period_type, period=period, frequency_type=frequency_type, frequency=frequency).json()

        # 'When periodType=day valid values for period are: [1, 2, 3, 4, 5, 10]'
        # 'When periodType=day valid values for frequencyType are: minute'
        df = self.price_history_to_dataframe(price_history)

        self.daily_plot_settings(symbol, df, "1_day")        
        

    def print_180_daily(self, symbol):
        earliest_date = datetime.datetime.now() - datetime.timedelta(days=180)
        price_history = self.client.get_price_history_every_day(symbol, start_datetime=earliest_date).json()

        df = self.price_history_to_dataframe(price_history)

        self.my_plot_settings(symbol, df, "180_daily")

    def print_365_weekly(self, symbol):
        earliest_date = datetime.datetime.now() - datetime.timedelta(days=366)
        price_history = self.client.get_price_history_every_week(symbol, start_datetime=earliest_date).json()

        df = self.price_history_to_dataframe(price_history)

        self.my_plot_settings(symbol, df, "365_weekly")

        return df

    def price_history_to_dataframe(self, price_history):
        df = pd.DataFrame(price_history['candles'], columns=['open', 'high', 'low', 'close', 'volume', 'datetime'])
        df['datetime'] = df['datetime'].apply(self.date_transform)
        df = df.set_index('datetime')
        df.index.name = 'Date'
        df.shape
        df.head(3)
        df.tail(3)
        return df

    def daily_plot_settings(self, symbol, df, timeframe):


        # Timestamp for title
        now = datetime.datetime.now()
        title_date = f"{now.strftime('%B')} - {now.year}"

        # Compute price range for dynamic vertical grid spacing
        price_min, price_max = df['low'].min(), df['high'].max()
        price_range = price_max - price_min

        # Rule of thumb: aim for ~12 horizontal gridlines
        raw_spacing = np.round(price_range / 12, 1)
        nice_ticks = [0.5, 1, 2, 5, 10, 20]
        tick_spacing = min(nice_ticks, key=lambda x: abs(x - raw_spacing))

        # Generate chart and access figure/axes
        fig, axes = mpf.plot(
            df,
            type='candle',
            style='charles',
            returnfig=True,
            figsize=(21, 8),
            datetime_format=' %Y-%m-%d',
            xrotation=90,
            title=f"{symbol}, {title_date}\n{timeframe}",
            ylabel='Price ($)'
        )

        ax1 = axes[0]  # Main price axis

        # Apply vertical gridlines (price axis)
        ax1.yaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
        ax1.grid(True, which='major', axis='y', linestyle='--', color='gray')

        # Apply horizontal gridlines (time axis)
        ax1.xaxis.set_major_locator(mdates.HourLocator(interval=4))
        # ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        # ax1.xaxis.set_minor_locator(mdates.MinuteLocator(interval=15))
        ax1.grid(True, which='major', axis='x', linestyle=':', color='lightgray', alpha=0.6)

        # Save chart
        fig.savefig(f"{self.path}/{symbol}_chart_{timeframe}.png", dpi=96, bbox_inches="tight")

    def my_plot_settings(self, symbol, df, timeframe):
        import mplfinance as mpf
        import matplotlib.ticker as ticker
        import datetime
        import numpy as np
        right_now = datetime.datetime.now()
        month = right_now.strftime("%B")
        year = right_now.year

        # Compute price range to scale tick spacing
        price_min, price_max = df['low'].min(), df['high'].max()
        price_range = price_max - price_min

        # Rule of thumb: 10–15 gridlines max
        tick_spacing = np.round(price_range / 12, 1)

        # Round tick_spacing to nearest "nice" number
        nice_ticks = [0.5, 1, 2, 5, 10, 20]
        tick_spacing = min(nice_ticks, key=lambda x: abs(x - tick_spacing))

        fig, axes = mpf.plot(
            df,
            type='candle',
            style='charles',
            returnfig=True,
            figsize=(21, 8),
            datetime_format=' %Y-%m-%d',
            xrotation=90,
            title=f"{symbol}, {month} - {year}\n{timeframe}",
            ylabel='Price ($)'
        )

        ax1 = axes[0]

        # Apply scaled horizontal gridlines
        ax1.yaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
        ax1.grid(True, which='major', axis='y', linestyle='--', color='gray')

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
            self.print_10_day(stock)

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

