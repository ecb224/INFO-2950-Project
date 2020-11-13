import csv
import datetime
from datetime import time
import introcs
import Evan_LIFEApps

#Collection of functions to convert given date/time format into floats

def military_to_time(military):
    """Takes in the time in military format and returns it in the AM/PM format."""
    pos1 = military.index(':')
    hour = int(military[:pos1])
    if hour > 12:
        hour -= 12
        suffix = 'PM'
    elif hour == 12:
        suffix = 'PM'
    elif hour == 0:
        hour = 12
        suffix = 'AM'
    elif hour < 12:
        suffix = 'AM'
        
    minute = military[3:5]
    
    return('{}:{} {}'.format(hour, minute, suffix))

def time_to_float(time):
    """Takes in a string of the time in AM/PM format and returns it as a float,
    with 0 representing 12:00 AM."""
    pos1 = time.index(':')
    pos2 = time.index(' ')
    
    hour = time[:pos1]
    hour = int(hour)
    
    suffix = time[pos2+1:]
    if (suffix == 'PM' and hour != 12):
        hour = hour + 12
    elif (suffix == 'AM' and hour == 12):
        hour = 0
    
    mins = time[pos1+1:pos2]
    mins = int(mins)
    
    end = hour + mins/60

    return(round(end, 3))

def military_to_float(military):
    """Takes in the a string of time in military format and returns it
    as a float, with 0 representing 12:00 AM."""
    return(time_to_float(military_to_time(military)))

def date_to_seconds(data):
    """Takes in a string of the datetime in the form "YYYY-MM-DDTHH:MM:SS.SSS,
        where Y is the year, M is the month, D  is the day, H is the hour, M is
        the minute, and S is the second. Example: December 20, 2019 at 12:30 PM,
        is represented as "2020-12-20T12:30:00.000."
        """
    year = int(data[:4])
    month = int(data[5:7])
    day = int(data[8:10])
    hour = int(data[11:13])
    minute = int(data[14:16])

    x = datetime.datetime(year,month,day, hour, minute)

    seconds = int(round(x.timestamp()))

    return seconds

#Read the json
fast_data = (introcs.read_json('Evan_LIFEApps/life-data/Procedure.json'))

fast_end_time = []
fast_start_time = []

#day_transition = 1 if fast was started on 10/01 and broken 10/02
#Important to keep track of this so that multi-day fasts are recorded appropriately.
#Example: Fast started on 10/01 at 6:00 PM and not ended until 10/03. 
#Fast hour should be recorded as 6 for 10/02 and as -18 for 10/03.
day_transition = []

for _ in range(len(fast_data)):
    if fast_data[_]['code']['coding'][0]['display'] == 'Fasting' and fast_data[_]['status'] == 'completed':
        fast_end_time.append(date_to_seconds(fast_data[_]['performedPeriod']['end']))
        fast_start_time.append(date_to_seconds(fast_data[_]['performedPeriod']['start']))

#Set fast_start_time and fast_end_time in chronological order
fast_start_time.sort()
fast_end_time.sort()

for _ in range(len(fast_end_time)):
    fast_end_time[_] = datetime.datetime.fromtimestamp(fast_end_time[_])
    day2 = datetime.datetime(fast_end_time[_].year, fast_end_time[_].month, fast_end_time[_].day)
    fast_start_time[_] = datetime.datetime.fromtimestamp(fast_start_time[_])
    day1 = datetime.datetime(fast_start_time[_].year, fast_start_time[_].month, fast_start_time[_].day)
    day_transition.append((day2-day1).days)


fast_end = {}
fast_start = {}

"""fast_dict will be a dictionary with the keys as the date the fast was broken,
and the the values as the fast hour. It is important that the date be the day the fast
was broken and not the day it was started becuase it the values will be used
in reference to the session of sleep. For example, if a fast was started on
10/01, we want to study its effect on the sleep session that ends on 10/02; thus,
we list it under 10/02."""
fast_dict = {}


for _ in range(len(fast_end_time)):
    fast_dict.update({str(fast_end_time[_])[:4] + '-' + str(fast_end_time[_])[5:7] + '-'
    + str(fast_end_time[_])[8:10]: military_to_float(str(fast_start_time[_])[11:16])})

    fast_end.update({str(fast_end_time[_])[:4] + '-' + str(fast_end_time[_])[5:7] + '-'
    + str(fast_end_time[_])[8:10]: fast_end_time[_]})
    fast_start.update({str(fast_end_time[_])[:4] + '-' + str(fast_end_time[_])[5:7] + '-'
    + str(fast_end_time[_])[8:10]: fast_start_time[_]})

for _ in range(len(fast_end_time)):
    x = str(fast_end_time[_])[:10]
    if fast_dict[x] >= 12.0:
        fast_dict[x] = round(fast_dict[x] - 12.0 - 24.0 * (day_transition[_]-1),3)
    #if fast started before 6:00 AM, it likely preceded sleep session
    elif fast_dict[x] <= 6.0:
        fast_dict[x] = round(fast_dict[x] + 12.0 - 24.0 * (day_transition[_]), 3)
    else:
        fast_dict[x] = round(fast_dict[x] - 24.0 * (day_transition[_]-1),3)

    #This ensures that fasts the span over more than one day are given an appropriate value
    #that can be subtracted from the bedtime to give an accurate "fast to bed" measurement.
    if day_transition[_] > 1:
        for h in range(2,day_transition[_]+1):
            delta = datetime.timedelta(days = h -1)
            fast_dict.update({str(fast_end_time[_]-delta)[:10]: float(fast_dict[x]) + 24*(h-1)})

      
