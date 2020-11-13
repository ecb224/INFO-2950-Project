import datetime
import csv
import pandas as pd
import numpy as np
import fast_collector


def FitbitDF(file_no):
    
    file = list(csv.reader(open('appendix/fitbit_export_{}.csv'.format(file_no))))

    #The number of days of data that appear in the file
    days = file.index([]) - 2

    #The values of the first and last day in the file can be read in the Body section.
    first_day = file[2][0]
    last_day = file[days+1][0] 

    """Note: if I am interested in a sleep session that is reported for November 1,
    I need to look at the other variables at October 31, as I want to look at the habits
    that preceeded the sleep."""

    day_delta = datetime.timedelta(days=1)
    start_date = pd.to_datetime(first_day, format = '%Y-%m-%d')
    end_date = pd.to_datetime(last_day, format = '%Y-%m-%d')

    def time_to_bed(time):
        """The function will take in a string of the bedtime hour and return it as a float,
        with 0 representing 12:00 PM, 12 representing 12:00 AM, 15 representing 3:00 AM etc.
        Time will be in the format YYYY-MM-DD HH:MMAM (or PM)"""

        #time could be None is Fitbit was not worn that night, or if it did not record properly.
        if time != None:
            dt = pd.to_datetime(time, format = '%Y-%m-%d %I:%M%p')

            if (dt.hour < 12 and time[-2:] == 'AM'):
                dt += datetime.timedelta(hours=12)
                return(round(dt.hour + dt.minute/60.0, 3))
            elif (dt.hour >= 12):
                return(round(dt.hour - 12.0 +dt.minute/60.0, 3))
        else:
            return np.NaN

    def sleep_data(file_number, start_date, end_date):
        """Takes in file number of Fitbit CSV export and returns a DataFrame."""

        file = np.asarray(list(csv.reader(open('appendix/fitbit_export_{}.csv'.format(file_no)))))

        #date_range starts at index number 1 because sleep data is listed under the day of waking up,
        #but the related activities of interest take place on day (index) 0.
        date_range = pd.date_range(start = str(start_date)[:10], end = str(end_date)[:10])[1:]

        #BODY
        weight = []

        #FOODS
        calories_eaten = []

        #ACTIVITIES
        calories_burned = []
        steps_taken = []
        mins_very_active = []

        #SLEEP
        bedtime_hour = []
        sleep_time = []
        awake = []
        REM = []
        light_sleep = []
        deep_sleep = []


        #BODY SECTION
        body_section = file[2:days+2]

        body = []
        for i in range(len(body_section)):
            for j in range(len(body_section[i])):
                body.append(body_section[i][j])

        #The body section has 4 columns in the CSV file        
        body = np.asarray(body).reshape(days, 4)

        for w in body[:-1,1]:
            weight.append(float(w))


        #FOOD SECTION
        #Can infer the indexing based on the shape of all Fitbit CSV exports
        food_section = file[days+5:2*days+5]
        food = []
        for i in range(len(food_section)):
            for j in range(len(food_section[i])):
                food.append(food_section[i][j])

        food = np.asarray(food).reshape(days, 2)
        fast_hour = []

        for f in food[:-1,1]:
            #replace commas with empty strings
            calories_eaten.append(int(f.replace(',', '')))

        fast_dict = fast_collector.fast_dict

        for f in food[:,0]:
            if f in fast_dict.keys():
       #         fast_hour.append(round(float(fast_dict[f]),3))
                fast_hour.append(round(fast_dict[f],3))
            else:
                fast_hour.append(np.NaN)
                
                
        """Note: If I did not log my meals on a given day, the value for Calories In is
        zero. Using the stored dictionary of fasting times, we can see if the
        zero is true or not. If it is, we append to calories_eaten np.NaN"""

        for _ in range(len(fast_hour[:-1])):
            #if Calories In is listed as 0 and the fast that ends on Day 2 was started on Day 1 after
            #8:00 AM, Calories In is np.NaN, as this would indicate that some food was eaten earlier in
            #the day but not recorded, as opposed to a fast that was started very early in the morning
            #(more likely a midnight snack, eaten before a sleep session) or started a day or more before.
            if calories_eaten[_] == 0 and (fast_hour[_+1] > -4):
                calories_eaten[_] = np.NaN
                
            #if there is no record of a fast that ends on the day after no Calories were reported,
            #then Calories In is far more likely to be zero for lack of reporting than for actual
            #abstinence from food.
            elif (calories_eaten[_] == 0 and np.isnan(fast_hour[_])):
                calories_eaten[_] = np.NaN
                
            #This accounts for an edge case in which there are zero Calories In reported and the day 
            #is the last in the file (meaning there is no following fast). We will always collect data
            #after completing a fast
            elif (calories_eaten[_] == 0 and np.isnan(fast_hour[_+1])):
                calories_eaten[_] = np.NaN
        
        fast_hour = fast_hour[1:]

        #ACTIVITIES SECTION
        activies_section = file[2*days+8:3*days+8]
        activities = []
        for i in range(len(activies_section)):
            for j in range(len(activies_section[i])):
                activities.append(activies_section[i][j])

        activities = np.asarray(activities).reshape(days, 10)  

        for c in activities[:-1,1]:
            calories_burned.append(int(c.replace(',', '')))

        for s in activities[:-1,2]:
            steps_taken.append(int(s.replace(',', '')))

        for m in activities[:-1,8]:
            mins_very_active.append(int(m.replace(',', '')))

        """There are days where the Fitbit was dead, and thus did not record any activity.
        For these days, we must replace all activities with np.NaN.""" 
        for _ in range(len(steps_taken)):
            if steps_taken[_] == 0:
                steps_taken[_] = np.NaN
                calories_burned[_] = np.NaN
                mins_very_active[_] = np.NaN

        """Sleep section is different, as there is no row for days where either the
        watch was not worn at night or the watch malfunctioned and failed to record.
        There could also be multiple sleep sessions for one day (naps); given this, there
        is no definite number of rows we should expect in the sleep section. However, we
        can find where sleep ends through the location of an empty cell that always separates
        the Sleep and Food Log sections."""
        
        sleep_file = file[3*days+11:]
        index = []
        for _ in range(len(sleep_file)):
            if len(sleep_file[_]) == 0:
                index.append(_)
                break

        #Updated sleep_file
        sleep_file = file[3*days+11:3*days+11+index[0]]

        sleep = []
        for i in range(len(sleep_file)):
            for j in range(len(sleep_file[i])):
                sleep.append(sleep_file[i][j])

        sleep = np.asarray(sleep).reshape(len(sleep_file), 9)

        sessions = []
        rests = []

        #sleep[:,1] contains the values of wake-up date and time. Index [:10] of such
        #a value is just the date.
        for time in sleep[:,1]:
            sessions.append(time[:10])
            if pd.to_datetime(time[:10], format ='%Y-%m-%d') > start_date:
                rests.append(time[:10])

        """"Important distinction: sessions is a list of the sleep sessions recorded in the
        CSV file. List rests excludes all sessions that end before or on the start date. This is 
        because we want be able to use the actions of the previous day to analyze that day's sleep.
        In the final DataFrame, the number of calories burned on December 1 should be in the same row
        as the sleep session that ends on December 2. List sessions holds all of the sleep sessions
        because it will be useful for indexing."""

        #Now, some data cleaning is in order. We want to eliminate naps so that we do not have
        #multiple sets of sleep metrics for a given day.

        for date in date_range[::-1]:
            """Variable how_many will give us the number of sleep sessions that end on a given day.
            We then subtract one from how_many to represent the number of rows we will shift up
            when collecting values, as we want to skip over sleep sessions that follow the first one
            that ends on a particular day."""
            how_many = np.count_nonzero(str(date)[:10] == np.asarray(rests))
            how_many -= 1

            #x is the index of the first occurrence of the date in sessions
            try:
                x = sessions.index(str(date)[:10])
            except:
                x = 'N/A'
             

            #y is the index of the last occurrence of the date in sessions, the
            #the desired 'non-nap' sleep session
           
            try:
                y = x + how_many
            except:
                y = 'N/A'

            """Index of columns in sleep:
            0: Start Time, 1: End Time, 2: Minutes Asleep, 3: Minutes Awake, 4: Number of Awakenings,
            5: Time in Bed, 6: Minutes REM Sleep, 7: Minutes Light Sleep, 8: Minutes Deep Sleep

            Note that "Minutes Asleep" in this context means minutes in a given sleep stage other than awake.
            If I sleep from 12:00 AM to 8:00 AM, I may spend one hour of that time awake, though I would not
            remember it, and I would say that I slept for 8 hours. The columne "Time in Bed" reflects this 8 hour
            count, and it is what will be represented in the list sleep_time.

            Sometimes a sleep session is recorded, but the sleep stages themselves are not. In this case,
            the values in columns 6, 7, and 8 appear as 'N/A.'"""

            #If there is a recorded sleep session for the date AND it is the first session ending on that
            #day (not a nap)...
            #if x != 'N/A':
            if (str(date)[:10] in rests):
                if (sleep[:,1][x][:10] == sessions[y][:10]):#and (sleep[:,1][x][:10] == sessions[y][:10]) ):
                    sleep_time.append(int(sleep[:,5][y]))
                    bedtime_hour.append(sleep[:,0][y])

                #if the recorded sleep session does not give any data on sleep stages...
                if sleep[:,6][y] == 'N/A':
                    awake.append(None)
                    REM.append(None)
                    light_sleep.append(None)
                    deep_sleep.append(None)
                else:
                    awake.append(int(sleep[:,3][y]))
                    REM.append(int(sleep[:,6][y]))
                    light_sleep.append(int(sleep[:,7][y]))
                    deep_sleep.append(int(sleep[:,8][y]))

            else:
                sleep_time.append(None)
                bedtime_hour.append(None)
                awake.append(None)
                REM.append(None)
                light_sleep.append(None)
                deep_sleep.append(None)
                
        for _ in range(len(bedtime_hour)):
            bedtime_hour[_] = time_to_bed(bedtime_hour[_])

        #In the CSV file, the dates for Body, Food, and Activities are oriented with the earliest
        #date on top and the latest at the bottom. Sleep is in reverse, so we need to reverse it that
        #we can put it in the DataFrame with its lists with the other lists.

        sleep_lists = [sleep_time, bedtime_hour, awake, REM, light_sleep, deep_sleep]

        for sl in sleep_lists:
            sl.reverse()

        #FOOD LOG
        food_log_section = file[3*days+12+index[0]:]
        index2 = []
        for _ in range(len(food_log_section)):
            if food_log_section[_] == ['Daily Totals']:
                index2.append(_)
        

        fat = []
        carbs = []
        protein = []
        #Collect the number of grams consumed of each macronutrient (fat, carbs, proten)
        for i in index2[:-1]:
            fat.append(food_log_section[i+2][2])
            carbs.append(food_log_section[i+4][2])
            protein.append(food_log_section[i+6][2])

        #Recorded macronutrients are strings with "g" for gram. Example: '0 g'
        macros = [fat, carbs, protein]

        for macro in macros:
            for _ in range(len(macro)):
                if np.isnan(calories_eaten[_]):
                    macro[_] = np.NaN
                else:
                    pos = macro[_].index(' g')
                    macro[_] = int(macro[_][:pos])
                    
        date = []
        for _ in range(len(date_range)):
            date.append(date_range[_])
            
        DF1 = pd.DataFrame({'date': date, 'weight': weight,'calories_eaten': calories_eaten,
                           'fast_hour': fast_hour, 'calories_burned': calories_burned,
                           'steps_taken': steps_taken, 'mins_very_active': mins_very_active,
                           'bedtime_hour': bedtime_hour, 'sleep_time': sleep_time, 'awake': awake,
                           'REM': REM, 'light_sleep': light_sleep, 'deep_sleep': deep_sleep, 'fat': fat,
                           'carbs': carbs, 'protein': protein},
                          
                          columns = ['date', 'fast_hour', 'bedtime_hour', 'sleep_time', 'awake', 'REM',
                                     'light_sleep','deep_sleep', 'steps_taken','mins_very_active',
                                     'calories_burned', 'calories_eaten', 'fat', 'carbs', 'protein','weight'] )
        return DF1
    
    return sleep_data(file_no, start_date, end_date)
        
