import EvanBynoe
import os
import datetime
import introcs
import numpy as np
import pandas as pd

def FitbitDF2():
    
    vo2_max = []
    sleep_score = []
    time_asleep = []
    deep_and_rem = []
    restoration = []
    restlessness = []
    resting_heart_rate = []
    
    start_date = datetime.datetime(2019, 11, 12)
    #end_date will be revised if I choose to add more data before due date
    # end_date = datetime.datetime(2020, 11, 2)
    end_date = datetime.datetime.today()
    day_delta = datetime.timedelta(days=1)


    def any(list_of_lists):
        one_list = []
        for i in range(len(list_of_lists)):
            for j in list_of_lists[i]:
                one_list.append(j)
        return one_list
    
    count = []
    first_year = datetime.datetime(2019, 1, 1)
    
    """The VO2 max values are separated into documents that hold a year 
    of data each. The title of each file is a date, and they are separated by exactly
    one year."""

    
#     #Printing count[0], we get that the file is called 'demographic_vo2_max-2019-02-08.'
#     #This means that there is a second file, 'demographic_vo2_max_2020_02_08.'
   
    vo2_data = []
    vo2_dict = {}
    
    year = [2019, 2020]
    for y in year:
        file = 'EvanBynoe/Physical Activity/demographic_vo2_max-{}-02-08.json'.format(y)
        if os.path.isfile(file):
            vo2_data = introcs.read_json(file)
        for _ in range(len(vo2_data)):
            x = pd.to_datetime(vo2_data[_]['dateTime'][:8], format='%m/%d/%y')
            vo2_dict.update({x: vo2_data[_]['value']['filteredDemographicVO2Max']})
    
    while start_date <= end_date:
        if start_date in vo2_dict.keys():
            vo2_max.append(round(vo2_dict[start_date],4))
        else:
            vo2_max.append(np.NaN)
        start_date += day_delta


    #sleep_score.csv comes in a nice, readable csv format, but we want to clean up
    #the data by ignoring days with multiple sleep sessions.
    sleep_score_data = pd.read_csv('EvanBynoe/Sleep/sleep_score.csv')
    
    values = []
    for _ in range(len(sleep_score_data['timestamp'])-1):
        #how_many counts the number of times the same date shows up in the CSV file.
        how_many = np.count_nonzero(sleep_score_data['timestamp'].str[:10] == sleep_score_data['timestamp'][_][:10])
        #if a date shows up twice in the CSV, collect their indices in list values.
        if how_many > 1:
            values.append(_)
    
    rows = []
    index = 0
    for _ in range(1, len(values)):
        """values is a list that tells the number of occurrences of the date of the given
        index. Suppose a list of nine sleep sessions. The first three days have one session each,
        the fourth day has two sleep sessions, the fifth day has one, and the sixth day has three.
        values would be [3, 4, 6, 7, 8]. A difference greater than 1 between any two consecutive values of the
        list indicates a switch in the day."""
        if values[_] - values[_-1] != 1:
            rows.append(values[index:_])
            index = _
    rows.append(values[index:])
        
    start_date = datetime.datetime(2019, 11, 12)
    while True:
        if str(start_date)[:10] in sleep_score_data['timestamp'].str[:10].unique():
            x = (np.where(sleep_score_data['timestamp'].str[:10] == str(start_date)[:10])) 
            x = x[0][0]
            break
        else:
            start_date += day_delta
            
    
    
    start_date = datetime.datetime(2019, 11, 12)
    
    while start_date <= end_date:
        #if there is exactly one sleep session on the date, append values to respective lists and move
        #down one row in CSV file.
        if (x not in any(rows)) and (str(start_date)[:10] in sleep_score_data['timestamp'].str[:10].unique()):
            sleep_score.append(sleep_score_data['overall_score'][x])
            time_asleep.append(sleep_score_data['duration_score'][x])
            deep_and_rem.append(sleep_score_data['composition_score'][x])
            restoration.append(sleep_score_data['revitalization_score'][x])
            restlessness.append(sleep_score_data['restlessness'][x])
            resting_heart_rate.append(sleep_score_data['resting_heart_rate'][x])
            x -= 1
        
        #if there is more than one sleep session on the date, append np.NaN and move down row in CSV
        #by the number of sleep sessions there are on said date.
        elif (str(start_date)[:10] in sleep_score_data['timestamp'].str[:10].unique()):
            spot = 0
            while True:
                if x in rows[spot]:
                    break
                spot += 1
            sleep_score.append(np.NaN)
            time_asleep.append(np.NaN)
            deep_and_rem.append(np.NaN)
            restoration.append(np.NaN)
            restlessness.append(np.NaN)
            resting_heart_rate.append(np.NaN)
            x -= len(rows[spot])
        #if there are no recorded sleep sessions on the date.
        else:
            sleep_score.append(np.NaN)
            time_asleep.append(np.NaN)
            deep_and_rem.append(np.NaN)
            restoration.append(np.NaN)
            restlessness.append(np.NaN)
            resting_heart_rate.append(np.NaN)
            

        start_date += day_delta
        
    date_range = pd.date_range(datetime.datetime(2019,11,12), end_date)

    DF2 = pd.DataFrame({'date': date_range, 'RHR': resting_heart_rate, 'sleep_score': sleep_score,
                          'time_asleep': time_asleep, 'deep_and_rem': deep_and_rem, 'restoration': restoration,
                          'vo2_max': vo2_max, 'restlessness': restlessness},
                         
                         columns = ['date', 'RHR','vo2_max', 'sleep_score','time_asleep', 'deep_and_rem',
                                    'restoration', 'restlessness'])

    return DF2
