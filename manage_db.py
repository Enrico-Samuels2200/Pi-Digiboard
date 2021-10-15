import pyrebase
import os
import requests
import json
import argparse
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')
DOMAIN = os.getenv('DOMAIN')
DB_URL = os.getenv('DB_URL')
PROJECT_ID = os.getenv('PROJECT_ID')
STORAGE_BUCKET = os.getenv('STORAGE_BUCKET')
SENDER_ID = os.getenv('SENDER_ID')
APP_ID = os.getenv('APP_ID')

WEATHER_DOMAIN = os.getenv('WEATHER_DOMAIN')

date = f'{datetime.today().year}-{datetime.today().month}-{datetime.today().day}'

firebase_config = {
	"apiKey": API_KEY,
	"authDomain": DOMAIN,
	"databaseURL": DB_URL,
	"projectId": PROJECT_ID,
	"storageBucket": STORAGE_BUCKET,
	"messagingSenderId": SENDER_ID,
	"appId": APP_ID
}

# Connect to firebase DB
firebase = pyrebase.initialize_app(firebase_config)
db = firebase.database()
local_area = "cape town"

def get_weather(location=""):
	try:	
		api = requests.get(WEATHER_DOMAIN)
		
		# True if api returns code 200
		if api.status_code:
			print("[*] Weather API Online")
			print(f"[*] Searching weather data.")
			if location:
				data = json.loads(requests.get(f'{WEATHER_DOMAIN}&q={location}').text)
				print(f"[*] Weather data for {location} successfully recieved.")
				return data
			else:
				data = json.loads(requests.get(f'{WEATHER_DOMAIN}&q={local_area}').text)
				print(f"[*] Weather data for {local_area} successfully recieved.")
				return data
		
	except Exception as err:
		print("[!] Error occured while fetching data")
		print(err)

def format_weather(data):
	print(f'{data["city"]["name"]} forecast:')

	for i in data['list']:
		date_found = i['dt_txt'][:10]
		
		max_temp = int(i['main']['temp_max'] - 273.15)
		min_temp = int(i['main']['temp_min'] - 273.15)
		humidity = i['main']['humidity']
		weather = i['weather'][0]['description']
		wind = i['wind']['speed']
		time = i['dt_txt'][-8:-3]

		if date_found == date:
			data = f'''
		Estimated Time: {time}
		Max Temp: {max_temp}°C
		Min Temp: {min_temp}°C

		Weather:  {weather}
		Humidity: {humidity}%
		wind:     {wind} knots
		-------------------------	
			'''
			print(f'{data}\n')

# Get data from db
def get_data(data_key):
    raw_data = dict(db.child(data_key).get().val())
    return raw_data

# Add data to db
def push_data(data_key, data):
	try:
		print(f"[*] Updating '{data_key}' in database.")
		db.child(data_key).set(data)
		print("[*] Successfully updated database")
	except:
		print("[!!] Error occured will pushing data to database.")

#  Returns list of commands that can be used.
def help_list():
	command_list = ''

	commands = {
		1 : 'Get local weather',
		2 : 'Search area specific weather',
		3 : 'Update database'
	}

	for i in commands:
		command_list += f'{i} : {commands[i]}\n'
	
	return command_list

def main():
	my_parser = argparse.ArgumentParser(description='Choose a command')
	print(f'Commands\n\n{help_list()}\n\n')

	my_parser.add_argument('-v', '--value', type=int, metavar='', help='run command')
	args = my_parser.parse_args()

	if args.value == 1:
		format_weather(get_data('weather'))
	
	elif args.value == 2:
		location = input('[*] Enter location: ')
		format_weather(get_weather(location))

	elif args.value == 3:
		db_key = input('[*] Enter DB key value: ')
		location = input('[*] Enter location: ')
		push_data(db_key, get_weather(location))

if __name__ == '__main__':
	main()