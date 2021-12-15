#! /usr/bin/python3

import csv
import sys, glob
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams.update({'font.size': 22})

fname = sys.argv[1]

data = []

cur_hour = None

with open(fname) as tfile:
    testreader = csv.reader(tfile, delimiter=",")
    first = True
    for row in testreader:

        if first:
            first = False
            continue

        date = row[0]
        try:
            temp = float(row[1])
        except ValueError:
            print("Ignoring entry: %s" % (row))
            continue

        tstamp = date.split("T")[1].split("Z")[0]

        hour, minute, second = tstamp.split(":")

        n = {}

        hour   = float(hour)
        minute = float(minute)

        hour += (minute / 60)

        if cur_hour == None:
            cur_hour = hour
        elif hour > cur_hour:
            cur_hour += hour - cur_hour # Assume always one
        elif hour < cur_hour: # Wrap around
            cur_hour += 24 - cur_hour
            cur_hour += hour
        else:
            print("not happening")
            sys.exit(-1)

        n["hour"] = cur_hour
        n["min"] = int(minute)
        #n["sec"] = int(second)
        n["temp"] = temp

        data.append(n)

temps = [e["temp"] for e in data]

hours = [e["hour"] for e in data]

min_ = min( hours )
max_ = max( hours )

hours_t = range(int(round(min_)), int(round(max_)), 3)
hours_l = [e % 24 for e in hours_t]

print(hours_t)
print(hours_l)

print(len(temps))
print(len(hours))

fig, ax = plt.subplots()

ax.plot(hours, temps, label=sys.argv[2], lw=3.0, color="tab:cyan")
#ax.fill_between(x, h0_low, h0_hi, alpha=0.1)

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Measured Temperature [C]')
ax.set_xlabel("Time of Day")
#ax.set_title('Mean Hourly Consumption in %s' % (month))
ax.set_xticks(hours_t)
ax.set_xticklabels( hours_l )
ax.legend()

i = 0
for label in ax.xaxis.get_ticklabels():
    if (i % 3) == 0:
        label.set_visible(True)
    else:
        label.set_visible(False)
    i += 1

#ax2.legend(loc="upper left")

#ax2.set_ylabel("Colder or Warmer Than 2020")

#ax.bar_label(rects1, padding=3)
#ax.bar_label(rects2, padding=3)

#fig.tight_layout()

plt.show()


