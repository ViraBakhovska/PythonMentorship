"""This module downloads 10-year historical csv stock prices and draws a graph"""
import csv
import argparse
import datetime
from datetime import timedelta
import matplotlib.pyplot as plt


parser = argparse.ArgumentParser(description='Draw a graph')

parser.add_argument('-u', action="store", dest="url",
                    default=r'C:\PythonMentorship\Task_4\input\HistoricalQuotes.csv')
args = parser.parse_args()

low_price = []
high_price = []
time = []

with open(args.url, newline='', encoding='utf-8') as csv_input:
    reader = csv.DictReader(csv_input)
    for item in reader:
        time.append(datetime.datetime.strptime(item['date'], "%Y/%m/%d"))
        low_price.append(float(item['low']))
        high_price.append(float(item['high']))

plt.figure(figsize=(12, 14))

# These are the colors as RGB.
colour_tbl = [(23, 190, 207), (188, 189, 34), (227, 119, 194), (247, 182, 210),
              (127, 127, 127), (199, 199, 199), (219, 219, 141), (23, 190, 207),
              (152, 223, 138), (158, 218, 229), (31, 119, 180), (255, 187, 120),
              (255, 152, 150), (148, 103, 189), (197, 176, 213), (196, 156, 148),
              (227, 119, 194), (214, 39, 40), (255, 127, 14), (140, 86, 75)]

# Scale the RGB values to the [0, 1] range, which is the format matplotlib accepts.
for i in range(len(colour_tbl)):
    r, g, b = colour_tbl[i]
    colour_tbl[i] = (r / 255., g / 255., b / 255.)


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


plt.yticks(range(0, int(max(high_price)), 10),
           [str(x) + "$" for x in range(0, int(max(high_price)), 10)],
           fontsize=12)
plt.xticks(fontsize=12)

# Provide tick lines across the plot to help viewers trace along
# the axis ticks.
for y in range(0, int(max(high_price)), 10):
    plt.plot(time, [y] * len(time),
             "--", lw=1.5, color="black", alpha=0.2)

# Remove the tick marks;
plt.tick_params(axis="both", which="both", bottom=False, top=False,
                labelbottom=True, left=False, right=False, labelleft=True)

price_type = ['high price', 'low price']

for rank, column in enumerate(price_type):
    # Plot each line separately with its own color, using the Tableau 20
    # color set in order.
    # Add a text label to the right end of every line.
    y_pos = high_price[0]

    if column == "high price":
        plt.plot(time, high_price,
                 lw=0.5, color=colour_tbl[rank])
        y_pos += 3
    elif column == "low price":
        plt.plot(time, low_price,
                 lw=0.5, color=colour_tbl[rank])
        y_pos -= 3

    plt.text(max(time)+ timedelta(days=10), y_pos, column, fontsize=10, color=colour_tbl[rank])

plt.title("EPAM Stock", fontsize=16)
plt.ylabel("Price in USD", fontsize=12)
plt.xlabel("Date", fontsize=12)
plt.show()
