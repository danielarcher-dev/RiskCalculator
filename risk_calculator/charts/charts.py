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

    def print_180_daily(self, symbol):
        earliest_date = datetime.datetime.now() - datetime.timedelta(days=180)
        price_history = self.client.get_price_history_every_day(symbol, start_datetime=earliest_date).json()

        df = self.price_history_to_dataframe(price_history)

        self.my_plot_settings(symbol, df)


    def price_history_to_dataframe(self, price_history):
        df = pd.DataFrame(price_history['candles'], columns=['open', 'high', 'low', 'close', 'volume', 'datetime'])
        df['datetime'] = df['datetime'].apply(self.date_transform)
        df = df.set_index('datetime')
        # dt_range = pd.date_range(start="2025-05-01", end="2025-05-16")
        # df = df[df.index > (dt_range)]
        # df = df[df.index.]
        return df

    def my_plot_settings(self, symbol, df):
        right_now = datetime.datetime.now()
        month = right_now.strftime("%B")
        year = right_now.year
        fplt.plot(
        df,
        type='candle',
        style='charles',
        title='{0}, {1} - {2}'.format(symbol, month, year),
        ylabel='Price ($)',
        figsize=(21,6),
        savefig=dict(fname='{0}/{1}_chart.png'.format(self.path, symbol), dpi=1200)
        )

        # fig = fplt.figure(figsize=(21, 7))  # Wider chart
        # ax = fig.add_subplot(1, 1, 1)

        # fplt.plot(df,
        #           type='candle',
        #           style='charles',
        #         #   suptitle='{0}, May - 2025'.format(symbol),
        #           ylabel='Price ($)',
        #           ax=ax,
        #           savefig=dict(fname='{0}_chart.png'.format(symbol), dpi=1200))
        # fig.show()


        # fig, ax = fplt.plot(df, type='candle', style='charles', returnfig=True)
        # fig.update_layout(width=1200, height=600)
        # fig.savefig('{0}_chart.png'.format(symbol), dpi=300)
        # fig.show()

        



    def date_transform(self, datetime_data):
        timestamp = datetime_data/1000
        return datetime.datetime.fromtimestamp(timestamp)
