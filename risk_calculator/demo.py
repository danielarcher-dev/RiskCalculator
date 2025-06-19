from schwab import auth, client
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
    r2 = c.get_instrument('MSFT',c.Instrument.Projection.FUNDAMENTAL)
    r2.raise_for_status()
    # print(json.dumps(r2.json(), indent=4))
    
    in_memory_file = StringIO()

    # json.dump(r2.json(), in_memory_file)
    # in_memory_file.write(json.dumps(r2.json()))
    # in_memory_file.write("hello")
    df = pd.read_json(json.dumps(r2.json()))
    # print(in_memory_file.readlines)
    # df = pd.read_json(in_memory_file)
    print(df)


    output_file = config['AppConfig']['output_file']
    with open(output_file, 'w') as json_file:
        json.dump(r2.json(), json_file)


    # output_csv = './data/output.csv'
    # with open(output_csv, "w", newline="") as csv_file:
    #     csv_writer = csv.writer(csv_file)  
    #     # Write the header
    #     data = json.loads(r2.json())
    #     print(data['instruments'])
    #     # header = data[0].keys()
    #     # csv_writer.writerow(header)

    #     # # Write the data rows
    #     # for row in data:
    #     #     csv_writer.writerow(row.values())

if __name__ == '__main__':
    # if RUN_ARGS.getboolean('profile'):
    #     import cProfile
    #     cProfile.run('main()', sort='tottime')
    # else:
    #     main()
    main()