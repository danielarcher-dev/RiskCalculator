from schwab import auth, client, streaming
import json
import csv
# from configparser import ConfigParser
import conf
import json_to_csv
import pandas as pd
from io import StringIO



def main():
    # args = parser.parse_args()
    c = conf.get_client()
    config = conf.get_config()
    # r = c.get_price_history_every_day('AAPL')
    # r.raise_for_status()
    # print(json.dumps(r.json(), indent=4))

    # r2 = c.get_instruments('AAPL,MSFT,GME,NTB',c.Instrument.Projection.FUNDAMENTAL)
    # r2 = c.get_instruments('MSFT',c.Instrument.Projection.FUNDAMENTAL)
    # r2.raise_for_status()
    # df = pd.read_json(json.dumps(r2.json()))
    # print(df)
    # print(df['instruments'][0]['fundamental']['symbol'])
    
    # in_memory_file = StringIO()

    r3 = c.get_quote('MSFT')
    r3.raise_for_status()
    # print(r3.json())
    df3 = pd.read_json(json.dumps(r3.json()))
    print(df3)
    price = df3['MSFT']['regular']['regularMarketLastPrice']
    print(price)

    # c.get_price_history('MSFT')
    # streaming.StreamClient.login()
    # # conf.get_stream_client()
    # streaming.StreamClient
    
    # streaming.StreamClient.logout()
    

    # save to file
    # output_file = config['AppConfig']['output_file']
    # with open(output_file, 'w') as json_file:
    #     json.dump(r2.json(), json_file)


if __name__ == '__main__':
    # if RUN_ARGS.getboolean('profile'):
    #     import cProfile
    #     cProfile.run('main()', sort='tottime')
    # else:
    #     main()
    main()