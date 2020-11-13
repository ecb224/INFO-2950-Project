import pandas as pd

def DataFrame(health_data):

	health_data['awake'] = health_data['awake']/health_data['sleep_time']
	health_data['REM'] = health_data['REM']/health_data['sleep_time']
	health_data['light_sleep'] = health_data['light_sleep']/health_data['sleep_time']
	health_data['deep_sleep'] = health_data['deep_sleep']/health_data['sleep_time']

	health_data['sleep_time']= round(health_data['sleep_time']/60, 3)
	health_data.insert(3, 'fast_to_bed',health_data['bedtime_hour']- health_data['fast_hour'])

	return health_data
