#! /usr/bin/python3

import csv
import sys, glob
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams.update({'font.size': 22})

data = []

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jly", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Parse weather data
#  - https://seklima.met.no/
#  - https://www.met.no/frie-meteorologiske-data/frie-meteorologiske-data
weather_file = "weather/vaerdata.csv"
wdata = []
with open(weather_file) as csvfile:
    testreader = csv.reader(csvfile, delimiter=";")
    first = True
    for row in testreader:

        if first:
            first = False
            continue

        date = row[2]
        msr = float(row[3][:].replace(",","."))
        day = int(date.split(".")[0])
        monthi = int(date.split(".")[1])
        mon = months[monthi-1]
        year = int(date.split(".")[2])

        n = {}
        n["year"] = year
        n["month"] = mon
        n["day"] = day
        n["temp"] = msr

        wdata.append(n)

# Oslo Blindern
#temp_2020 = [2.7,1.9,3.0,7.3,10.2,18.8,15.1,17.2,12.8,8.1,5.2,2.2]
#temp_2021 = [-4.7,-3.2,3.1,5.7,10.6,17.3,19.9,16.4,13.2,8.7,2.7,-4.3]
#tdiff = []
#for e in range(12):
#    tdiff.append(temp_2021[e]-temp_2020[e])

# Parse power measurements
arg = "power/*.csv*"
#arg = "power/meteringvalues-mp-707057500053182051-consumption-20211213T2027.csv"
files = glob.glob(arg)
for fname in files:
    print(fname)
    with open(fname) as csvfile:
        testreader = csv.reader(csvfile, delimiter=",")
        first = True
        for row in testreader:

            if first:
                first = False
                continue

            print(row)

            msr_from = row[0]
            msr_to   = row[1]
            msr      = row[2]

            ts_from = row[0].split(" ")[1]
            ts_to   = row[1].split(" ")[1]

            hour, minute = ts_from.split(":")
            hour = int(hour)
            minutes_from = hour * 60 + int(minute)

            hour_n, minute_n = ts_to.split(":")
            minutes_to = int(hour_n) * 60 + int(minute_n)

            if int(minute) != 0:
                print("ERROR!")
                sys.exit(-1)

            if int(minute_n) != 0:
                print("ERROR!!")
                sys.exit(-1)

            #

            date = row[0].split(" ")[0]
            day, month, year = date.split(".")

            day = int(day)
            month = months[int(month)-1]
            year = int(year)

            kwh = float(msr.replace(",","."))

            # Sometimes we have errors
            if minutes_to < minutes_from:
                if minutes_to != 0:
                    print("ERROR2")
                    sys.exit(-1)
                else:
                    minutes_to = 24 * 60

            elapsed = minutes_to - minutes_from

            if elapsed != 60:
                if minutes_to == minutes_from:
                    print(row)
                    print("WARNING: same to-from timestamp!")
                else:
                    if (elapsed % 60) != 0:
                        print("ERROR!")
                        sys.exit(-1)
                    else:
                        num_hours = int(elapsed / 60)
                        avg_kwh = kwh / num_hours

                        for i in range(num_hours-1):
                            n = {}
                            n["year"] = year
                            n["month"] = month
                            n["day"] = day
                            n["hour"] = hour
                            n["kwh"] = avg_kwh
                            hour += 1

                            data.append(n)

                        kwh = avg_kwh

            n = {}
            n["year"] = year
            n["month"] = month
            n["day"] = day
            n["hour"] = hour
            n["kwh"] = kwh

            #print(n)

            #sys.exit(0)

            if n["month"] == "Dec" and n["day"] > 12:
                continue

            if n["month"] == "Dec" and n["day"] < 6:
                continue

            if n["month"] == "Dec" and n["year"] == 2021:
                print(n)
                #sys.exit(-1)
            
            data.append(n)
    #break

months_2020 = {}

def monthly_average(year):
    ret = {}
    for month in months:
        ret[month] = np.mean( [e["kwh"] for e in data if (e["year"] == year and e["month"] == month ) ] )

    return ret

def monthly_sum(year):
    ret = {}
    for month in months:
        ret[month] = np.sum( [e["kwh"] for e in data if (e["year"] == year and e["month"] == month ) ] )

    return ret

def hourly_sum(year, month):
    ret = []
    for hr in range(24):
        ret.append(np.sum( [e["kwh"] for e in data if (e["hour"] == hr and e["year"] == year and e["month"] == month ) ] ))

    return ret

def hourly_average(year, month):
    ret = []
    for hr in range(24):
        ret.append(np.mean( [e["kwh"] for e in data if (e["hour"] == hr and e["year"] == year and e["month"] == month ) ] ))

    return ret

def daily_temperature(year):

    ret = []
    
    for mon in months:
        for day in range(1,32):
            for w in wdata:
                if (w["year"] == year) and (w["day"] == day) and (w["month"] == mon):
                    ret.append(w["temp"])
                    break

    #while( len(ret) < 365 ):
    #    ret.append(0)

    return ret

def weekly_temperature(year):

    ret = []

    cur_days = 0
    cur_avg = 0
    
    for mon in months:
        for day in range(1,32):
            for w in wdata:
                if (w["year"] == year) and (w["day"] == day) and (w["month"] == mon):
                    cur_avg += w["temp"]
                    cur_days += 1
                    if cur_days == 7:
                        ret.append( cur_avg / 7 )
                        cur_avg = 0
                        cur_days = 0
                    break

    #while( len(ret) < 365 ):
    #    ret.append(0)

    return ret

temp_weekly_2020 = weekly_temperature(2020)
temp_weekly_2021 = weekly_temperature(2021)

#temp_daily_2020 = daily_temperature(2020)
#temp_daily_2021 = daily_temperature(2021)
print(len(temp_weekly_2020))
print(len(temp_weekly_2021))

temp_weekly_diff = []
for i in range(52):
    try:
        #print("%.2f vs %.2f" % (temp_weekly_2021[i], temp_weekly_2020[i]))
        temp_weekly_diff.append(temp_weekly_2021[i] - temp_weekly_2020[i])
    except IndexError:
        break

def monthly_average_chart():

    months_2020 = []
    months_2021 = []

    months_2020_d = monthly_sum(2020)
    months_2021_d = monthly_sum(2021)

    for m in months:
        months_2020.append(months_2020_d[m])
        months_2021.append(months_2021_d[m])

    print("2020,2021,diff")
    for e in zip(months_2021, months_2020):
        print("%.2f,%.2f,%.2f" % (e[0], e[1], e[0] - e[1]))

    fig, ax = plt.subplots()

    x = np.arange(len(months_2020))  # the label locations
    width = 0.35  # the width of the bars

    rects1 = ax.bar(x - width/2, months_2020, width, label="2020", color="tab:cyan")
    rects2 = ax.bar(x + width/2, months_2021, width, label="2021", color="tab:green")

    #print(x)
    max_x = max(x) + 1
    min_x = min(x)

    x_temp_step = (max_x - min_x) / 52
    x_temp = []

    cur = min_x
    for i in range(min([len(temp_weekly_2020),len(temp_weekly_2021)])):
        print(cur)
        x_temp.append(cur)
        cur += x_temp_step

    print(x_temp)
    ax2 = ax.twinx()
    ax2.plot( x_temp, temp_weekly_diff, label="Temperature Diff (Blindern, Oslo)", lw=3.0, linestyle="dashed", color="black")

    [xmin, xmax] = ax.get_xlim()
    ax2.set_xlim([xmin, xmax])

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Total Energy Consumption [kWh]')
    ax.set_title('Monthly Consumption of Energy')
    ax.set_xticks(x)
    ax.set_xticklabels( months)
    ax.legend()

    ax2.legend(loc="upper left")

    ax2.set_ylabel("Colder or Warmer Than 2020")

    #ax.bar_label(rects1, padding=3)
    #ax.bar_label(rects2, padding=3)

    #fig.tight_layout()

    plt.show()

#################################
monthly_average_chart()

def day_average_chart(month):

    hourly_2020 = []
    hourly_2021 = []

    hourly_2020 = hourly_average( 2020, month )
    hourly_2021 = hourly_average( 2021, month )

    std0 = np.std(hourly_2020)
    std1 = np.std(hourly_2021)

    h0_low = []
    h0_hi = []
    h1_low = []
    h1_hi = []

    print(std0)
    print(std1)
    for e in zip(hourly_2020, hourly_2021):
        print("%.2f %.2f" % (e[0], e[1]))
        h0_low.append(e[0] - std0)
        h0_hi.append(e[0] + std0)
        h1_low.append(e[1] - std1)
        h1_hi.append(e[1] + std1)

    fig, ax = plt.subplots()

    x = np.arange(24)  # the label locations
    width = 0.35  # the width of the bars

    ax.plot(x, hourly_2020, label="2020", lw=3.0, color="tab:cyan")
    ax.fill_between(x, h0_low, h0_hi, alpha=0.1)
    #ax.errorbar(x, hourly_2020, std0, errorevery=4)
    ax.plot(x, hourly_2021, label="2021", lw=3.0, color="tab:green")
    ax.fill_between(x, h1_low, h1_hi, color="tab:green", alpha=0.1)
    #ax.errorbar(x, hourly_2021, std1, errorevery=4)
    #rects1 = ax.bar(x - width/2, hourly_2020, width, label="2020", color="tab:cyan")
    #rects2 = ax.bar(x + width/2, hourly_2021, width, label="2021", color="tab:green")

    #print(x)
    #max_x = max(x) + 1
    #min_x = min(x)

    #x_temp_step = (max_x - min_x) / 52
    #x_temp = []

    #cur = min_x
    #for i in range(min([len(temp_weekly_2020),len(temp_weekly_2021)])):
    #    print(cur)
    #    x_temp.append(cur)
    #    cur += x_temp_step

    #print(x_temp)
    #ax2 = ax.twinx()
    #ax2.plot( x_temp, temp_weekly_diff, label="Temperature Diff (Blindern, Oslo)", lw=3.0, linestyle="dashed", color="black")

    #[xmin, xmax] = ax.get_xlim()
    #ax2.set_xlim([xmin, xmax])

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Energy Consumption [kWh]')
    ax.set_xlabel("Time of Day")
    ax.set_title('Mean Hourly Consumption in %s' % (month))
    ax.set_xticks(x)
    #ax.set_xticklabels( months)
    ax.legend()

    #ax2.legend(loc="upper left")

    #ax2.set_ylabel("Colder or Warmer Than 2020")

    #ax.bar_label(rects1, padding=3)
    #ax.bar_label(rects2, padding=3)

    #fig.tight_layout()

    plt.show()


#################################
day_average_chart("Aug")
day_average_chart("Sep")
day_average_chart("Oct")
day_average_chart("Nov")
day_average_chart("Dec")

"""
#months_2020 = monthly_average(2020)
#months_2021 = monthly_average(2021)


for m in months:
    #print(months_2020[m])
    #print(months_2021[m])
    print(months_2021[m] - months_2020[m])


October_2021_sums = hourly_sum(2021, "Oct")
October_2020_sums = hourly_sum(2020, "Oct")

def plot_bars(series0_d, l0, series1_d, l1):

    series0 = []
    series1 = []

    for m in months:
        series0.append(series0_d[m])
        series1.append(series1_d[m])

    fig, ax = plt.subplots()

    x = np.arange(len(series0))  # the label locations
    width = 0.35  # the width of the bars

    rects1 = ax.bar(x - width/2, series0, width, label=l0, color="tab:cyan")
    rects2 = ax.bar(x + width/2, series1, width, label=l1, color="tab:orange")

    ax2 = ax.twinx()
    ax2.plot( x, tdiff, label="Oslo, Blindern", lw=3.0, color="Blue")

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Month')
    ax.set_title('Hourly Consumption of Energy')
    ax.set_xticks(x, months)
    ax.legend()

    ax2.legend(loc="upper left")

    ax2.set_ylabel("Temperature Difference")

    #ax.bar_label(rects1, padding=3)
    #ax.bar_label(rects2, padding=3)

    #fig.tight_layout()

    plt.show()

def plot_hourly_sums(series0, l0, series1, l1):

    fig, ax = plt.subplots()

    x = np.arange(len(series0))  # the label locations
    width = 0.35  # the width of the bars

    rects1 = ax.bar(x - width/2, series0, width, label=l0, color="tab:cyan")
    rects2 = ax.bar(x + width/2, series1, width, label=l1, color="tab:orange")

    #ax2 = ax.twinx()
    #ax2.plot( x, tdiff, label="Oslo, Blindern", lw=3.0, color="Blue")

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Month')
    ax.set_title('Monthly Consumption of Energy')
    ax.set_xticks(x, months)
    ax.legend()

    #ax2.legend(loc="upper left")

    #ax2.set_ylabel("Temperature Difference")

    #ax.bar_label(rects1, padding=3)
    #ax.bar_label(rects2, padding=3)

    #fig.tight_layout()

    plt.show()

# Yearly sums
plot_bars(months_2020, "2020", months_2021, "2021")

# October hour by hour sums
#plot_hourly_sums( October_2020_sums, "October 2020", October_2021_sums, "October 2021")
"""
