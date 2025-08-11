import configparser
from schwab import auth

def get_config():
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    config.read('./secrets/local_config.conf')
    return config

def get_client():
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    config.read('./secrets/secrets.conf')

    api_key = config['AppSecrets']['app_key']
    app_secret = config['AppSecrets']['secret']
    callback_url = config['AppSecrets']['callback_url']
    token_path = config['AppSecrets']['token_path']

    return auth.easy_client(api_key, app_secret, callback_url, token_path)
