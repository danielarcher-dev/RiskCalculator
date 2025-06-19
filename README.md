Layout of the secrets folder.

secrets.conf
    [AppSecrets]
    project_root = /RiskCalculator
    app_key = 
    secret = 
    callback_url = 
    token_path = ${project_root}/secrets/token.json

local_config.conf
    [AppConfig]
    project_root = /RiskCalculator
    data_folder = ${project_root}/data
    securities_account_file = ${data_folder}/securities_account/securities_account_<date>.json
    transactions_file = ${data_folder}/transactions/transactions_file_<date>.json
    default_transaction_history_lookback = 10

    [RuntimeSecrets]
    target_account =


Structure of the data folder:
    data
    |   charts
    |   securities_account
    |   transactions