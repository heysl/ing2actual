import argparse
from datetime import datetime

import pandas as pd

def remove_at(i, s):
    return s[:i] + s[i+1:]

parser = argparse.ArgumentParser(description='Transform csv-exports from ing to csv for actual budget')
parser.add_argument(
    dest='csv_input_filename',
    type=str,
    help='the csv file to be transformed'
)

args = parser.parse_args()

# set filename for input
csv_input_filename = args.csv_input_filename

# set filename for output
csv_output_filename = "Import_{}.csv".format(datetime.strftime(datetime.now(), '%d-%m-%Y'))

# read csv from ing
df = pd.read_csv(csv_input_filename, encoding='latin_1', skiprows=13, sep=';')

# only keep needed columns and rename them for actual budget
actual_style = df[["Buchung", "Auftraggeber/Empfänger", "Verwendungszweck", "Betrag"]]
actual_style.rename(columns={
    "Buchung" : "Date",
    "Auftraggeber/Empfänger" : "Payee",
    "Verwendungszweck" : "Notes",
    "Betrag" : "Amount"
}, inplace=True)

## clean up VISA transactions
for row in actual_style.index:
    if actual_style.loc[row, "Payee"].startswith('VISA'): # remove 'VISA ' from payee and turn UPPER to Capitalized string
        actual_style.at[row, "Payee"] =  actual_style.loc[row, "Payee"][5:].title()

## clean up PayPal transactions
for row in actual_style.index:
    if actual_style.loc[row, "Payee"] == 'PayPal Europe S.a.r.l. et Cie S.C.A':
        # exported csv from ing has a space at position 35 in the notes for paypal-transactions for some reason...
        if actual_style.loc[row, "Notes"][35] == ' ':
            actual_style.at[row, "Notes"] = remove_at(35, actual_style.at[row, "Notes"])
        # replace paypal as payee with actual payee from notes
        pos_from = actual_style.loc[row, "Notes"].find(' . ') + 3
        pos_to = actual_style.loc[row, "Notes"].find(',')
        actual_payee = actual_style.loc[row, "Notes"][pos_from:pos_to]
        actual_style.at[row, "Payee"] = actual_payee

# export to new csv
actual_style.to_csv(path_or_buf=csv_output_filename, sep=';', index=False)
