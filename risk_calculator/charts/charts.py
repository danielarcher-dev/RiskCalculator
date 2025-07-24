import mplfinance as fplt
import pandas as pd
import datetime
import json

class Charts():
    def __init__(self, account):
        self.account = account
        self.client = account.client
        self.path = self.account.config['Charting']['charts_path']
        

    def print_15_mins(self, symbol):
        # FIXME: there is a bug here, if market is closed when this is run, we will get an error, because the response will have no candles.
        earliest_date = datetime.datetime.now() - datetime.timedelta(days=1)
        price_history = self.client.get_price_history_every_fifteen_minutes(symbol, start_datetime=earliest_date).json()

        df = self.price_history_to_dataframe(price_history, "15_mins")

        self.my_plot_settings(symbol, df)

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

    def my_plot_settings(self, symbol, df, timeframe):
        right_now = datetime.datetime.now()
        month = right_now.strftime("%B")
        year = right_now.year

        fig = fplt.figure(figsize=(18, 8), style='charles', tight_layout=True)
        ax1 = fig.add_subplot(3, 1, (1, 2))
        # ax2 = fig.add_subplot(3, 1, 3, sharex=ax1)
        fig.subplots_adjust(hspace=0)
        xticks, xticklabels = [], []
        mth = -1
        for i, dt in enumerate(df.index):
            if dt.dayofweek == 0:
                xticks.append(i)
                if dt.month != mth:
                    mth = dt.month
                    xticklabels.append(datetime.datetime.strftime(dt, '%b %d'))
                else:
                    xticklabels.append(datetime.datetime.strftime(dt, '%d'))
                ax1.set_xticks(xticks)
                ax1.set_xticklabels(xticklabels)
        fplt.plot(
        df,
        type='candle',
        ax=ax1,
        # volume=ax2,
        style='charles',
        axtitle='{0}, {1} - {2}\n{3}'.format(symbol, month, year, timeframe),
        ylabel='Price ($)',
        # show_nontrading=True,
        datetime_format=' %Y-%m-%d',
        xrotation=90,
        # tight_layout=True,
        # savefig=dict(fname='{0}/{1}_chart_{2}.png'.format(self.path, symbol, timeframe), dpi=1200, bbox_inches="tight")
        )
        fig.savefig('{0}/{1}_chart_{2}.png'.format(self.path, symbol, timeframe), dpi=96, bbox_inches="tight")
        
        # TODO: matplot gives a runtime warning here about too many figures opened, possibly using too much memory unless they are explicitly closed
        # but this implementation doesn't actually have a close method, and isn't currently having memory problems


    def date_transform(self, datetime_data):
        timestamp = datetime_data/1000
        return datetime.datetime.fromtimestamp(timestamp)
    

    def chart_my_watchlist(self, acct, watchlist_file, chart_file):
        with open(watchlist_file, "r") as json_file:
            watchlist = json.load(json_file) 

        # due to timeouts with the ExcelWriter, we're grabbing all the charts in one loop
        # and then writing them to Excel in a second loop
        for stock in watchlist['stocks']:
            # we don't actually need the data frames here, we're just interested in the image
            self.print_180_daily(stock)
            self.print_365_weekly(stock)

        with pd.ExcelWriter(chart_file, engine="xlsxwriter") as writer:
            writer.book.set_size(2620, 1820)
            for stock in sorted(watchlist['stocks']):
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
                worksheet.insert_image('A31', image2, {'x_scale': scale, 'y_scale': scale})

                worksheet.set_column("A:A", 220) # width not in pixels
                worksheet.set_column("B:B", 5) # width not in pixels

