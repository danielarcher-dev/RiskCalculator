import mplfinance as fplt
import pandas as pd
import datetime

import accounts.accounts as accounts

class Charts():
    def __init__(self, account):
        # self.account = accounts(account)

        self.account = account
        self.client = account.client
        self.path = self.account.config['Charting']['charts_path']
        
        
    def print_15_mins(self, symbol):
        # FIXME: there is a bug here, if market is closed when this is run, we will get an error, because the response will have no candles.
        earliest_date = datetime.datetime.now() - datetime.timedelta(days=1)
        price_history = self.client.get_price_history_every_fifteen_minutes(symbol, start_datetime=earliest_date).json()

        df = self.price_history_to_dataframe(price_history)

        self.my_plot_settings(symbol, df)

        return df

    def print_180_daily(self, symbol):
        earliest_date = datetime.datetime.now() - datetime.timedelta(days=180)
        price_history = self.client.get_price_history_every_day(symbol, start_datetime=earliest_date).json()

        df = self.price_history_to_dataframe(price_history)

        self.my_plot_settings(symbol, df)

        return df

    def print_365_weekly(self, symbol):
        earliest_date = datetime.datetime.now() - datetime.timedelta(days=366)
        # price_history = self.client.get_price_history_every_day(symbol, start_datetime=earliest_date).json()
        price_history = self.client.get_price_history_every_week(symbol, start_datetime=earliest_date).json()

        df = self.price_history_to_dataframe(price_history)

        self.my_plot_settings(symbol, df)

        return df

    def price_history_to_dataframe(self, price_history):
        df = pd.DataFrame(price_history['candles'], columns=['open', 'high', 'low', 'close', 'volume', 'datetime'])
        df['datetime'] = df['datetime'].apply(self.date_transform)
        df = df.set_index('datetime')
        df.index.name = 'Date'
        df.shape
        df.head(3)
        df.tail(3)
        # dt_range = pd.date_range(start="2025-05-01", end="2025-05-16")
        # df = df[df.index > (dt_range)]
        # df = df[df.index.]
        return df

    def my_plot_settings(self, symbol, df):
        

        fig = fplt.figure(figsize=(21, 8), style='charles')
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
        axtitle='{0}, May - 2025'.format(symbol),
        ylabel='Price ($)',
        # show_nontrading=True,
        datetime_format=' %Y-%m-%d',
        xrotation=90,
        # tight_layout=True,
        
        )
        fig.savefig('{0}/{1}_chart.png'.format(self.path, symbol), dpi=600, bbox_inches="tight")

        



    def date_transform(self, datetime_data):
        timestamp = datetime_data/1000
        return datetime.datetime.fromtimestamp(timestamp)
