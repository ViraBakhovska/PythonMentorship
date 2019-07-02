"""This module fetches the data for whole 2017 year from the OLX API,
day-by-day and stores it into SQL database.
Calculates median price of apartment per square meter by number of rooms.
Draws a time chart (line chart by time)."""
import os
import json
import sqlite3
import argparse
import datetime
from datetime import date
from datetime import timedelta
import collections
from collections import Counter
import requests
import matplotlib.pyplot as plt
import urllib3

urllib3.disable_warnings()

parser = argparse.ArgumentParser(description='Graph: Median price of apartment per square meter by number of rooms')
parser.add_argument('-y', action="store", dest="year", default=2017)
args = parser.parse_args()

API_URL = 'https://35.204.204.210/'

CALCULATION_YEAR = args.year
start = date(CALCULATION_YEAR, 1, 1)
end = date(CALCULATION_YEAR, 12, 31)

api_date_generated = []
for x in range(0, (end-start).days +1):
    api_date_generated.append(start + datetime.timedelta(days=x))

api_link_list = []
for y in api_date_generated:
    api_link_list.append(os.path.join(API_URL, str(y)))

def create_or_open_db(filename):
    file_exists = os.path.isfile(filename)
    conn = sqlite3.connect(filename)
    if file_exists:
        print(''' "{}" database successfully opened '''.format(filename))
    else:
        print(''' "{}" database successfully created '''.format(filename))
    return conn

def create_tbl_appartment_detail(conn):
    sqlite = '''create table if not exists appartment_detail(
            [price_usd] NUMERIC,
            [total_area] NUMERIC,
            [number_of_rooms] INTEGER,
            [added_on] TEXT,
            [price_sq_m] NUMERIC)'''
    conn.execute(sqlite) # shortcut for conn.cursor().execute(sql)
    print("Created appartment_detail table successfully")

def insert_data (conn, curr):
    sqlite = '''insert into appartment_detail (price_usd, total_area, number_of_rooms, added_on, price_sq_m)
                values (:price_usd, :total_area, :number_of_rooms, :added_on, :price_sq_m)'''
    curr.executemany(sqlite, apartment_info)
    conn.commit()

def get_inserted_years (cur):
    sqlite = '''select distinct strftime('%Y',added_on) as year from appartment_detail'''
    cur.execute(sqlite)
    inserted_years = []
    for x in cur.fetchall():
        inserted_years.append(int(x[0]))
    return inserted_years

def data_by_api(api):
    response = requests.get(api, verify=False)
    json_data = json.loads(response.text)
    for element in json_data['postings']:
        if element['total_area'] is not None and element['total_area'] > 0:
            apartment_info.append({'price_usd':element['price_usd'],
                                   'total_area':element['total_area'],
                                   'number_of_rooms':element['number_of_rooms'],
                                   'added_on':element['added_on'],
                                   'price_sq_m':element['price_usd']/element['total_area']})
    return apartment_info

def mediana_calculation(curr):
    sqlite = '''SELECT
                      added_on,
                      number_of_rooms,
                      AVG(price_sq_m) mediana
                FROM
                (
                  SELECT
                        date(added_on) added_on,
                        number_of_rooms,
                        price_sq_m,
                        ROW_NUMBER() OVER (
                        PARTITION BY date(added_on),  number_of_rooms
                        ORDER BY price_sq_m ASC) AS RowAsc,
                        ROW_NUMBER() OVER (
                                           PARTITION BY date(added_on),  number_of_rooms
                                           ORDER BY price_sq_m DESC) AS RowDesc
                FROM appartment_detail
                ) x
                WHERE
                     RowAsc IN (RowDesc, RowDesc - 1, RowDesc + 1)
                GROUP BY added_on, number_of_rooms
                ORDER BY added_on, number_of_rooms;'''

    curr.execute(sqlite)
    statistic_data = curr.fetchall()
    return statistic_data

conn = sqlite3.connect('apartment_db.sqlite3')
curr = conn.cursor()
create_or_open_db('apartment_db.sqlite3')
create_tbl_appartment_detail(conn)

if CALCULATION_YEAR not in get_inserted_years(curr):
    json_data = {}
    apartment_info = []

    index = 0;
    for api in api_link_list:
        data_by_api(api)
        index = index + 1;
    apartment_info = sorted(apartment_info, key=lambda i: i['added_on'])

    insert_data(conn, curr)

statistic_data = collections.defaultdict(collections.Counter)
added_on_list = []
mediana_list = []

for row in mediana_calculation(curr):
    statistic_data[row[1]][row[0]] += row[2]
    added_on_list.append(datetime.datetime.strptime(row[0],'%Y-%m-%d').date())
    mediana_list.append(row[2])


sorted_statistic_data = {}
for x in sorted(statistic_data):
    sorted_statistic_data[x] = sorted(statistic_data[x].items())

dates = []
delta = (max(added_on_list) - min(added_on_list)).days+1
for x in range(0, delta +1):
    dates.append(min(added_on_list) + datetime.timedelta(days=x))




# These are the "Tableau 20" colors as RGB.
tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

# Scale the RGB values to the [0, 1] range, which is the format matplotlib accepts.
for i in range(len(tableau20)):
    r, g, b = tableau20[i]
    tableau20[i] = (r / 255., g / 255., b / 255.)

# You typically want your plot to be ~1.33x wider than tall. This plot is a rare
# exception because of the number of lines being plotted on it.
# Common sizes: (10, 7.5) and (12, 9)
plt.figure(figsize=(12, 14))

# Remove the plot frame lines. They are unnecessary chartjunk.
ax = plt.subplot(111)
ax.spines["top"].set_visible(False)
ax.spines["bottom"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)

# Ensure that the axis ticks only show up on the bottom and left of the plot.
# Ticks on the right and top of the plot are generally unnecessary chartjunk.
ax.get_xaxis().tick_bottom()
ax.get_yaxis().tick_left()
ax.spines["bottom"].set_visible(True)

ax.spines['bottom'].set_linestyle('dashed')
#ax.spines['bottom'].set_capstyle("butt")
ax.spines['bottom'].set_linewidth(.3)
ax.spines['bottom'].set_linestyle((0, (4, 4)))
ax.tick_params(axis=u'both', which=u'both', length=0)

# Limit the range of the plot to only where the data is.
# Avoid unnecessary whitespace.
plt.ylim(0, 2200)
plt.xlim(min(added_on_list), max(added_on_list))


# Make sure your axis ticks are large enough to be easily read.
# You don't want your viewers squinting to read your plot.
max_mediana = max(mediana_list)
plt.yticks(range(0, 2200, 200), [str(x) + "$" for x in range(0, 2200, 200)], fontsize=10)
plt.xticks(fontsize=10, rotation='vertical')

# Provide tick lines across the plot to help your viewers trace along
# the axis ticks. Make sure that the lines are light and small so they
# don't obscure the primary data lines.
for y in range(0, 2200, 200):
    plt.plot(dates, [y]*(len(dates)), "--", lw=0.5, color="black", alpha=0.3)


majors = {}
y_pos = 1700
for rank, x in enumerate(sorted_statistic_data.keys()):
    majors[x] = str(x)+'-room apartment'
    for y in sorted_statistic_data:

        if x == y:
            price = []
            time = []
            for element in sorted_statistic_data[y]:
                price.append(element[1])
                time.append(datetime.datetime.strptime(element[0], '%Y-%m-%d'))
            plt.plot(time, price, lw=1, color=tableau20[rank])
            y_pos = y_pos-70
            plt.text(max(dates), y_pos, majors[x], fontsize=7, color=tableau20[rank])

plt.show()
