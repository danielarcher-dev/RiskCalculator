import json, csv
import pandas as pd
import accounts.securities_account as pa
import accounts.position as pos

def main():
    input_file = './data/output.json'
    output_file = './data/data.csv'

    # work with history file instead of live client
    with open (input_file) as json_file:
        data = json.load(json_file)
        accountDetails = pa.SecuritiesAccount(data)
        print(accountDetails.CurrentBalances.CashBalance)



        for po in accountDetails.Positions:
            print(po.symbol)


if __name__ == '__main__':
    # if RUN_ARGS.getboolean('profile'):
    #     import cProfile
    #     cProfile.run('main()', sort='tottime')
    # else:
    #     main()
    main()


