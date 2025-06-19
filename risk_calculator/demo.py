from schwab import auth, client
import json
import csv
# from configparser import ConfigParser
import configparser
import json_to_csv
import pandas

def load_secrets_conf():
    if os.path.exists('secrets.conf'):
        print("has file")

def main():
    # args = parser.parse_args()
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    config.read('./secrets/secrets.conf')

    api_key = config['AppSecrets']['app_key']
    app_secret = config['AppSecrets']['secret']
    callback_url = config['AppSecrets']['callback_url']
    token_path = config['AppSecrets']['token_path']

    c = auth.easy_client(api_key, app_secret, callback_url, token_path)

    # r = c.get_price_history_every_day('AAPL')
    # r.raise_for_status()
    # print(json.dumps(r.json(), indent=4))

    r2 = c.get_instruments('AAPL',c.Instrument.Projection.FUNDAMENTAL)
    r2.raise_for_status()
    # print(json.dumps(r2.json(), indent=4))
    
    # output_file = './data/output.json'
    # with open(output_file, 'w') as json_file:
    #     json.dump(r2.json(), json_file)

    output_csv = './data/output.csv'
    with open(output_csv, "w", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)  
        # Write the header
        data = json.loads(r2.json())
        print(data['instruments'])
        # header = data[0].keys()
        # csv_writer.writerow(header)

        # # Write the data rows
        # for row in data:
        #     csv_writer.writerow(row.values())

if __name__ == '__main__':
    # if RUN_ARGS.getboolean('profile'):
    #     import cProfile
    #     cProfile.run('main()', sort='tottime')
    # else:
    #     main()
    main()