import sqlite3
import csv
import requests
import argparse
import os

parser = argparse.ArgumentParser(description='Extract github avatars')
parser.add_argument('-u', "--url", action='store', #required = True,
                    default='https://api.exchangeratesapi.io/latest', help = 'exchange rates api')
parser.add_argument('-d', "--database", action='store', #required = True,
                    default='C:\Work\Personal\PythonMentorship\Task4', help = 'DB path')
args = parser.parse_args()


URL = args.url

response = requests.get(URL)
rates_data = response.json()

currency_rates_api = rates_data['rates']

currency_rates_dict = []
for  row in currency_rates_api:
    currency_rates_dict.append({'currency_code':row,
                                'rate':currency_rates_api[row]})
#print(currency_rates_dict)

def search(currency_code):
    for item in data_for_update:
        if item['currency_code'] == currency_code:
            return True
    return False

data_for_update = []
data_for_delete = []
data_for_insert = []
with sqlite3.connect(os.path.join(args.database, 'forex.sqlite3')) as conn:
    cursor = conn.cursor()
    cursor = conn.execute('select * from rates')

    for row in cursor.fetchall():
        #print(row)
        if row[0] in currency_rates_api:
            data_for_update.append({'currency_code':row[0],
                                    'old_rate':row[2],
                                    'new_rate':currency_rates_api[row[0]],
                                    'percent_change':((currency_rates_api[row[0]]-
                                                       row[2])*100/row[2])})

            if row[2] != currency_rates_api[row[0]]:
                diff_rate = (currency_rates_api[row[0]], row[0])
                #print(diff_rate)
                cursor.execute('update rates set rate = ? where currency_code = ?', diff_rate)
        elif row[0] not in currency_rates_api:
            data_for_delete.append({'currency_code':row[0],
                                    'old_rate':row[2],
                                    'new_rate':'',
                                    'percent_change':''})
            cursor.execute('delete from rates where currency_code = ?', (row[0],))
            #print(data_for_delete)

    #print(search('USD'))
    #print(data_for_update)


    for row in currency_rates_api:
        #print(search(row))
        if not search(row):
            data_for_insert.append({'currency_code':row,
                                    'old_rate':'',
                                    'new_rate':currency_rates_api[row],
                                    'percent_change':''})
            new_rate = (row, currency_rates_api[row])
            cursor.execute('insert into rates (currency_code, rate) values (?, ?)', new_rate)


with open('currency_rates.csv',
          mode='w', newline='') as currency_rates:
    currency_rates_writer = csv.writer(currency_rates, delimiter=',', quotechar='"')

    for element in data_for_update:
        currency_rates_writer.writerow([element['currency_code'],
                                        element['old_rate'],
                                        element['new_rate'],
                                        element['percent_change']])

    for element in data_for_delete:
        currency_rates_writer.writerow([element['currency_code'],
                                        element['old_rate'],
                                        element['new_rate'],
                                        element['percent_change']])

    for element in data_for_insert:
        currency_rates_writer.writerow([element['currency_code'],
                                        element['old_rate'],
                                        element['new_rate'],
                                        element['percent_change']])
