import conf
import pandas as pd
import requests
import json


class IndexUtility():
    def __init__(self):
        self.read_config()
        # self.parse_args()

        self.get_sp500()

        # self.get_nyse()
        # self.get_nasdaq()
        # self.get_amex()



    def read_config(self):
        self.config = conf.get_config()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        self.sp500_file = self.config['AppConfig']['index_file'].replace("<index>", "sp500")
        self.nyse_file = self.config['AppConfig']['index_file'].replace("<index>", "nyse")
        self.nasdaq_file = self.config['AppConfig']['index_file'].replace("<index>", "nasdaq")
        self.amex_file = self.config['AppConfig']['index_file'].replace("<index>", "amex")

    def get_sp500(self):
        response = requests.get("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies", headers=self.headers)
        response.raise_for_status()  # Raises HTTPError if status is 403

        tables = pd.read_html(response.text)
        sp500 = tables[0]
        
        self.save_result(sp500, self.sp500_file)
        
    # def get_nyse(self):
    #     tickers = gt.get_tickers(NYSE=True, NASDAQ=False, AMEX=False)
    #     self.save_result(tickers, self.nyse_file)

    # def get_nadsaq(self):
    #     tickers = gt.get_tickers(NYSE=False, NASDAQ=True, AMEX=False)
    #     self.save_result(tickers, self.nasdaq_file)

    # def get_amex(self):
    #     tickers = gt.get_tickers(NYSE=False, NASDAQ=False, AMEX=True)
    #     self.save_result(tickers, self.amex_file)

    def save_result(self, df, save_file):
        # with open(save_file, 'w') as json_file:
        #     json.dump(df, json_file)
        df.to_json(save_file, orient="records", lines=False)


def run():
    launcher = IndexUtility()
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