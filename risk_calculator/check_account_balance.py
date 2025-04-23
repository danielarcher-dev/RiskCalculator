from schwab import auth, client
import json
import csv
# from configparser import ConfigParser
import configparser
import json_to_csv
import pandas as pd
from io import StringIO
import httpx

def get_client():
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    config.read('./secrets/secrets.conf')

    api_key = config['AppSecrets']['app_key']
    app_secret = config['AppSecrets']['secret']
    callback_url = config['AppSecrets']['callback_url']
    token_path = config['AppSecrets']['token_path']

    return auth.easy_client(api_key, app_secret, callback_url, token_path)

def get_config():
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    config.read('./secrets/local_config.conf')
    return config

def get_account_hash(c):
    resp = c.get_account_numbers()
    assert resp.status_code == httpx.codes.OK

    # The response has the following structure. If you have multiple linked
    # accounts, you'll need to inspect this object to find the hash you want:
    # [
    #    {
    #        "accountNumber": "123456789",
    #        "hashValue":"123ABCXYZ"
    #    }
    #]
    account_hash = resp.json()[0]['hashValue']
    return account_hash

def main():
    # args = parser.parse_args()
    c = get_client()
    conf = get_config()
    # r = c.get_price_histor
    hash = get_account_hash(c)
    print(hash)


if __name__ == '__main__':
    # if RUN_ARGS.getboolean('profile'):
    #     import cProfile
    #     cProfile.run('main()', sort='tottime')
    # else:
    #     main()
    main()