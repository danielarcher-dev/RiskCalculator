import mplfinance as fplt
import pandas as pd
import datetime



def print_15_mins(symbol, client):
    # FIXME: there is a bug here, if market is closed when this is run, we will get an error, because the response will have no candles.
    earliest_date = datetime.datetime.now() - datetime.timedelta(days=1)
    price_history = client.get_price_history_every_fifteen_minutes(symbol, start_datetime=earliest_date).json()

    df = price_history_to_dataframe(price_history)

    my_plot_settings(symbol, df)

def print_180_daily(symbol, client):
    earliest_date = datetime.datetime.now() - datetime.timedelta(days=180)
    price_history = client.get_price_history_every_day(symbol, start_datetime=earliest_date).json()

    df = price_history_to_dataframe(price_history)

    my_plot_settings(symbol, df)


def price_history_to_dataframe(price_history):
    df = pd.DataFrame(price_history['candles'], columns=['open', 'high', 'low', 'close', 'volume', 'datetime'])
    df['datetime'] = df['datetime'].apply(date_transform)
    df = df.set_index('datetime')
    # dt_range = pd.date_range(start="2025-05-01", end="2025-05-16")
    # df = df[df.index > (dt_range)]
    # df = df[df.index.]
    return df

def my_plot_settings(symbol, df):
    fplt.plot(
    df,
    type='candle',
    style='charles',
    title='{0}, May - 2025'.format(symbol),
    ylabel='Price ($)',
    figsize=(21,6),
    savefig=dict(fname='{0}_chart.png'.format(symbol), dpi=1200)
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

    



def date_transform(datetime_data):
     timestamp = datetime_data/1000
     return datetime.datetime.fromtimestamp(timestamp)
