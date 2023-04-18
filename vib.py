import requests
import hashlib
import time
import os
from datetime import datetime

INFLUXDB_URL = os.environ['INFLUXDB_URL']
INFLUXDB_TOKEN = os.environ['INFLUXDB_TOKEN']

EMAIL = os.environ['VESYNC_EMAIL'] 
PASSWORD = hashlib.md5(os.environ['VESYNC_PASSWORD'].encode('utf-8')).hexdigest() 


# api calls derived from pyvesync

API_BASE_URL = 'https://smartapi.vesync.com'
API_RATE_LIMIT = 30
API_TIMEOUT = 5
USER_AGENT = ("VeSync/3.2.39 (com.etekcity.vesyncPlatform;"
              " build:5; iOS 15.5.0) Alamofire/5.2.1")

DEFAULT_TZ = 'America/New_York'
DEFAULT_REGION = 'US'

APP_VERSION = '2.8.6'
PHONE_BRAND = 'SM N9005'
PHONE_OS = 'Android'
MOBILE_ID = '1234567890123456'
USER_TYPE = '1'
BYPASS_APP_V = "VeSync 3.0.51"

class VeSyncApi:

	def __init__(self):
		self.token = None
		self.account_id = None
		self.country_code = None

	def login(self):
		body = {
			'timeZone': DEFAULT_TZ,
			'acceptLanguage': 'en',
			'appVersion': APP_VERSION,
			'phoneBrand': PHONE_BRAND,
			'phoneOS': PHONE_OS,
			'traceId': str(int(time.time())),
			'email': EMAIL,
			'password': PASSWORD,
			'devToken': '',
			'userType': USER_TYPE,
			'method': 'login'
		}

		r = requests.post(API_BASE_URL + '/cloud/v1/user/login', json=body)

		if r.status_code < 200 or r.status_code > 299 :
			print("error status_code = " + r.status_code)
			time.sleep(60) # wait 60s before bailing so we don't try too fast
			raise RuntimeError("Auth failed status code = {}".format(r.status_code))

		auth_response = r.json()

		if 'result' not in auth_response:
			print("auth failed missing result")
			time.sleep(60) # wait 60s before bailing so we don't try too fast
			raise RuntimeError("Auth failed no result")

		self.token = auth_response['result']['token']
		self.account_id = auth_response['result']['accountID']
		self.country_code = auth_response['result']['countryCode']


	def device_list(self):

		if self.token == None:
			raise RuntimeError("must login first")

		headers = {
			'Content-Type': 'application/json; charset=UTF-8',
			'User-Agent': 'okhttp/3.12.1',
		}

		body = {
			'timeZone': DEFAULT_TZ,
			'acceptLanguage': 'en',
			'accountID': self.account_id,
			'token': self.token,
			'appVersion': APP_VERSION,
			'phoneBrand': PHONE_BRAND,
			'phoneOS': PHONE_OS,
			'traceId': str(int(time.time())),
			'method': 'devices',
			'pageNo': '1',
			'pageSize': '100'
		}

		r = requests.post(API_BASE_URL + '/cloud/v1/deviceManaged/devices', headers=headers, json=body)

		if r.status_code < 200 or r.status_code > 299:
			print("error getting device info status code = {}".format(r.status_code))
			time.sleep(60) # wait 60s before bailing so we don't try too fast
			raise RuntimeError("error getting device info status code = {}".format(r.status_code))

		response = r.json()

		if 'result' not in response:
			print("get device info failed no result")
			time.sleep(60) # wait 60s before bailing so we don't try too fast
			raise RuntimeError("get device info failed no result")

		
		return response['result']['list']


vsapi = VeSyncApi()
vsapi.login()

while True:

	devices = vsapi.device_list()
	
#	print(devices)

	for device in devices:
		
		deviceName = device['deviceName'].replace(" ", "-").lower()
		influxLine = "status,device-name={} ".format(deviceName)
				
		for deviceProp in device['deviceProp']:
			devicePropValue = device['deviceProp'][deviceProp]
			if type(devicePropValue) == str:
				devicePropValue = '"{}"'.format(devicePropValue)
			influxLine = influxLine + "{}={},".format(deviceProp.replace(" ", "-").lower(),devicePropValue)
		
		influxLine = influxLine.rstrip(",")

		print("[{}] {}".format(datetime.now().isoformat(), influxLine))


		r = requests.post(INFLUXDB_URL, headers={'Authorization':'Token {}'.format(INFLUXDB_TOKEN), 'Content-Type': 'text/plain; charset=utf-8', 'Accept': 'application/json'}, data=influxLine)

		if r.status_code != 204:
			raise("Error writing to InfluxDB code={}".format(r.status_code))

	time.sleep(60)


