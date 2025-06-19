#import accounts
# import httpx
import json
import accounts.accounts as accounts

launcher = accounts.AccountsLauncher()
launcher.run()

account_numbers = launcher.account_numbers


hash = launcher.hash

details = launcher.get_account_details(hash)

for item in details:
    print(item)

acct = launcher.Account

print(acct.CurrentBalances.CashBalance)

print(details['aggregatedBalance']['liquidationValue'])
output_file = launcher.config['AppConfig']['output_file']
with open(output_file, 'w') as json_file:
    json.dump(details, json_file)