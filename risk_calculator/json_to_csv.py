import json, csv

def convert_fundamentals_json_response_to_csv(input_file, output_file):
    with open (input_file) as json_file:
        data = json.load(json_file)
        with open(output_file, "wt", newline="\n") as out_file:

            number_of_tickers = len(data['instruments'])

            item = 0 #only write header on the first item, index 0
            for ticker in data['instruments']:
                mydata = ticker
                header = mydata.keys()

                if item == 0:
                    header_row = ""
                    fundamental_cols= ""
                data_row = ""
                fundamentals = ""
                for col in header:
                    if(col == "fundamental"):
                        fundamentals = mydata[col]
                    else:
                        if item == 0: header_row += str.format("{0},", col)
                        data_row += str.format("{0},", mydata[col])
                for col in fundamentals:
                        if item == 0: fundamental_cols += str.format("{0},", col)
                        data_row += str.format("{0},", fundamentals[col])
                if item == 0:
                    header_row += fundamental_cols
                    header_row += "\n"
                    out_file.write(header_row)
                data_row += "\n"
                out_file.write(data_row)
                item = item + 1

def main():
    input_file = './data/output.json'
    output_file = './data/data.csv'

    convert_fundamentals_json_response_to_csv(input_file, output_file)

if __name__ == '__main__':
    # if RUN_ARGS.getboolean('profile'):
    #     import cProfile
    #     cProfile.run('main()', sort='tottime')
    # else:
    #     main()
    main()