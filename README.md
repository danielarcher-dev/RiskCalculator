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
    options_chain_file = ${data_folder}/option_chains/<symbol>_<date>.json
    default_transaction_history_lookback = 10
    output_file = ${data_folder}/output.file

    [RuntimeSecrets]
    target_account =

    [Charting]
    project_root = /RiskCalculator
    data_folder = ${project_root}/data
    charts_path = ${data_folder}/charts/charts
    charts_file = ${data_folder}/charts/charting_file_<date>.xlsx
    watchlist = ${data_folder}/watchlist.json

Structure of the data folder:
    data
    |   charts
    |   |   charts (ticker.png)
    |   option_chains
    |   securities_account
    |   transactions