# -*- coding: utf8 -*-
'''
Home by SFR wrapping class
Plain use of your Home by SFR device from a Python 2 library

Warning:
This is a wrap aroud website, this could stop working without prior notice
'''

# TODO:
## Manage cameras
### Get image
### Get video
## Manage logs
## Encoding error for sensors' names

authors = (
	'Gilles "Almtesh" Émilien MOREL',
	)
name = 'homesfr for Python 2'
version = '0.10-20160523'

# Settable modes
MODE_OFF = 0
MODE_CUSTOM = 1
MODE_ON = 2

# Sensors names
PRESENCE_DETECTOR = 'PIR_DETECTOR'
MAGNETIC_OPENNING_DETECTOR = 'MAGNETIC'
SMOKE_DETECTOR = 'SMOKE'
SIREN = 'SIREN'
REMOTE_CONTROLER = 'REMOTE'
KEYPAD_CONTROLER = 'KEYPAD'
PRESENCE_CAMERA_DETECTOR = 'PIR_CAMERA'

# This part of code must be the one to adapt to make work the underneath part
from cookielib import CookieJar
import urllib2 as request
from urllib2 import HTTPError
from urllib import urlencode
from xml.etree import ElementTree as ET
from datetime import datetime

# Python2 and 3 adaptations
# BEGIN
def str2bytes (s):
	'''
	Bind to the bytes build-in function
	'''
	return (bytes (s))
# END

# The next must stay a copy from the python3 library, starting from class Common

class Common ():
	'''
	Common ressources to the library's classes
	'''
	
	def __init__ (self):
		
		# Specific configuration
		
		self.base_url = 'https://home.sfr.fr'
		
		# path to login test
		self.auth_path = '/mysensors'
		self.auth_ok = '/accueil'	# if logged
		self.auth_post_url = 'https://boutique.home.sfr.fr/authentification'
		self.auth_referer = 'https://boutique.home.sfr.fr/authentification?back=service'
		self.auth_user_field = 'email'
		self.auth_pass_field = 'passwd'
		self.auth_extra_fields = {'back': 'service', 'token_sso': '', 'error_sso': '', 'SubmitLogin': 'OK'}
		self.auth_logout_path = '/deconnexion'
		
		# Path to sensors and mode
		self.sensors_list = '/mysensors'
		
		# Path to list of alerts
		self.alerts_path = '/listalert'
		
		# Path to get and set modes
		self.mode_get_path = '/mysensors'
		self.mode_get_label = 'alarm_mode'
		self.mode_set_path = '/alarmmode'
		self.mode_set_field = 'action'	# Name for GET field
		self.mode_off = 'OFF'		# Value for off
		self.mode_custom = 'CUSTOM'	# Value for custom
		self.mode_on = 'ON'		# Value for on
		
		# Cameras
		self.cameras_list = '/homescope/mycams'
		self.camera_snapshot = '/homescope/snapshot'
		self.camera_snapshot_mac = 'mac'
		self.camera_video = '/homescope/flv'
		self.camera_vide_mac = 'mac'
		self.camera_recordings_list = '/listenr'
		self.camera_recordings_delete = '/delenr'
		self.camera_recordings_start = '/homescope/record'
		self.camera_recordings_stop = '/homescope/stoprecord'
		self.camera_recordings_mac = 'mac'
		self.camera_get_config_path = '/homescope/camsettings'
		self.camera_get_config_mac = 'mac'
		self.camera_get_config_flip = 'FLIP'
		self.camera_get_config_leds = 'LEDMODE' # set to 0 to turn the leds on
		self.camera_get_config_detectionsensibility = 'DP' # from 1 to 4
		self.camera_get_config_recording = 'REC24'
		self.camera_get_config_name = 'NAME'
		self.camera_set_config_path = '/homescope/camsettings'
		self.camera_set_config_mac = 'mac'
		self.camera_set_config_flip = 'flip'
		self.camera_set_config_leds = 'led_mode' # set to 0 to turn the leds on
		self.camera_set_config_detectionsensibility = 'dp' # from 1 to 4
		self.camera_set_config_recording = 'rec24'
		self.camera_set_config_name = 'name'
		
		# Sensors
		self.sensors_list = '/mysensors'
		self.sensors_label = 'Sensor'
		self.sensors_label_id = 'id'
		self.sensors_mac_field = 'deviceMac'
		self.sensors_type_field = 'deviceType'
		self.sensors_model_field = 'deviceModel'
		self.sensors_version_field = 'deviceVersion'
		self.sensors_name_field = 'name'
		self.sensors_longname_field = 'long_name'
		self.sensors_namegender_field = 'name_gender' # Only usefull for French for the moment
		self.sensors_batterylevel_field = 'batteryLevel'
		self.sensors_signal_field = 'signalLevel'
		self.sensors_lasttrigger_field = 'lastTriggerTime'
		self.sensors_lasttrigger_dateformat = '%Y-%m-%d %H:%M:%S'
		self.sensors_status_field = 'status'
		self.sensors_status_value_ok = 'OK'
		# I don't have any other value for the moment

	def bytes2file (self, b):
		'''
		Gives a file-like class from a Bytes
		'''
		from io import BytesIO
		r = BytesIO ()
		r.write (b)
		r.seek (0)
		return (r)

	def bytes2image (self, b):
		'''
		Gives a Image object from bytes
		Uses the bytes2file function
		'''
		from PIL import Image
		f = self.bytes2file (b)
		r = Image.open (f)
		return (r)

class HomeSFR (Common):
	def __init__ (self, username = None, password = None, cookies = None, debug = False, autologin = True):
		'''
		Sets the class with username and password couple, or cookies
		Both user/password and cookies can be set, the cookies will be used first
		The debug parameter defines if the class will write debug messages to stdout, if False, the stdout will never be writen by the class
		The autologin parameter defines if the class will manage the login by itself, if False, the user must call login () to login and test_login () to check the login
		The autologin paramater will always be False if no username and password are defined, and the login () method will always return False
		'''
		Common.__init__ (self)
		self.DEBUG = debug
		if self.DEBUG:
			print (name + ' ' + version)
			print ('Authors:')
			for i in authors:
				print (' - ' + i)
			if username != None:
				print ('init with username ' + username)
			if cookies != None:
				print ('init with cookies')
			print ('debug = ' + str (debug))
			print ('autologin = ' + str (autologin))
		
		if (username == None or password == None) and cookies == None:
			raise TypeError ('You must define either username AND password or cookies')
		self.username = username
		self.password = password
		if self.username != None and self.password != None:
			self.autologin = autologin
		else:
			self.autologin = False
		if cookies == None:
			self.cookies = CookieJar ()
		else:
			self.cookies = cookies
		self.opener = request.build_opener (request.HTTPCookieProcessor (self.cookies))
	
	def __str__ (self):
		'''
		Shows name, version, defined user and debug state
		'''
		if self.username != None:
			return (name + ' ' + version + '\nUser: ' + self.username + '\nDebug: ' + str (self.DEBUG))
		else:
			return (name + ' ' + version + '\nUser: Unknown (auth from cookie class)\nDebug: ' + str (self.DEBUG))
	
	def test_login (self):
		'''
		Tests if the client is logged
		Return True if it's logged, returns False either
		'''
		try:
			if self.DEBUG:
				print ('Testing login')
			self.opener.open (self.base_url + self.auth_path)
		except HTTPError:
			if self.DEBUG:
				print ('Not connected')
			return (False)
		if self.DEBUG:
			print ('Connected')
		return (True)
	
	def login (self):
		'''
		Logs in the HomeBySFR service
		Call this function first or exception will be raised
		Returns True if the login was a success, False either
		This method will always return False if no username and password are defined
		'''
		if self.username != None and self.password != None:
			self.opener.open (self.auth_referer)
			data = self.auth_extra_fields
			data [self.auth_user_field] = self.username
			data [self.auth_pass_field] = self.password
			data = str2bytes (urlencode (data))
			if self.DEBUG:
				print ('Cookies ' + str( len(self.cookies)))
				print ('Sending data ' + str (data))
			a = self.opener.open (self.auth_post_url, data = data)
			if self.DEBUG:
				print ('Auth redirected to ' + a.geturl ())
			return (a.geturl () == self.base_url + self.auth_ok)
		else:
			return (False)
	
	def logout (self):
		'''
		Logs out from HomeBySFR service
		The object should be destroyed just after calling this method
		'''
		if self.DEBUG:
			print ('Sending disconnect')
		self.opener.open (self.base_url + self.auth_logout_path)
		if self.DEBUG:
			print ('Destroying cookies')
		del self.cookies
		self.cookies = None
		return (None)
	
	def get_cookies (self):
		'''
		Returns the CookieJar as it is now, for further use
		It's strongly recommended to use this method only before a object delete
		'''
		return (self.cookies)
	
	def set_mode (self, mode):
		'''
		Sets the detection mode
		For the current version, use the MODE_OFF, MODE_ON and MODE_CUSTOM constants and always returns True, but raises an exception if a problem happens
		'''
		if (self.autologin and self.test_login () == False):
			self.login ()
		if mode == MODE_OFF:
			m = self.mode_off
		elif mode == MODE_CUSTOM:
			m = self.mode_custom
		elif mode == MODE_ON:
			m = self.mode_on
		else:
			if self.DEBUG:
				print ('You should use the MODE_OFF, MODE_ON and MODE_CUSTOM constants to set this.')
			raise ValueError
		r = self.base_url + self.mode_set_path + '?' + self.mode_set_field + '=' + m
		if self.DEBUG:
			print ('Will get ' + r)
		self.opener.open (r)
		return (True)
	
	def get_mode (self):
		'''
		Gets the detection mode
		Returns one of MODE_OFF, MODE_ON and MODE_CUSTOM constants, or None if something went wrong
		'''
		if (self.autologin and self.test_login () == False):
			self.login ()
		r = self.base_url + self.mode_get_path
		if self.DEBUG:
			print ('Getting ' + r)
		a = self.bytes2file (self.opener.open (r).read ())
		b = ET.parse (a).getroot ()
		c = b.get (self.mode_get_label)
		if self.DEBUG:
			print ('Got mode ' + c)
		if (c == self.mode_off):
			return (MODE_OFF)
		if (c == self.mode_custom):
			return (MODE_CUSTOM)
		if (c == self.mode_on):
			return (MODE_ON)
		return (None)
	
	def list_sensors (self):
		'''
		Returns a list of sensors' ids.
		'''
		if (self.autologin and self.test_login () == False):
			self.login ()
		r = self.base_url + self.sensors_list
		a = self.bytes2file (self.opener.open (r).read ())
		b = ET.parse (a)
		r = []
		for i in b.findall (self.sensors_label):
			r.append (i.get (self.sensors_label_id))
		return (list (r))
	
	def get_sensor (self, id):
		'''
		Returns a Sensor object for the sensor id or None if sensor is not found
		The available ids can be got from the list_sensors method
		'''
		if (self.autologin and self.test_login () == False):
			self.login ()
		r = Sensor (id, self.opener)
		r.refresh ()
		return (r)
	
	def get_all_sensors (self):
		'''
		Returns a tuple of sensors as described in the get_sensor method
		'''
		r = []
		for i in self.list_sensors ():
			r.append (self.get_sensor (i))
		return (tuple (r))
	
	def get_camera (self, id):
		'''
		Get a Camera object from the sensor's id
		'''
		if (self.autologin and self.test_login () == False):
			self.login ()
		r = Camera (id, self.opener)
		r.refresh ()
		return (r)

class Sensor (Common):
	'''
	Class used to read easily the sensors
	'''
	def __init__ (self, id, opener):
		'''
		Initialize the class with the dict producted by HomeSFR.get_sensors ()
		'''
		Common.__init__ (self)
		
		self.id = id
		self.sensor_dict = None
		self.opener = opener
	
	def refresh (self):
		'''
		Gets or refresh the data for the sensor
		'''
		def build_tree (element):
			r = {}
			for i in element.getchildren ():
				if i.getchildren () == []:
					r.update ({i.tag: i.text})
				else:
					r.update ({i.tag: build_tree (i)})
			return (r)
		r = self.base_url + self.sensors_list
		a = self.bytes2file (self.opener.open (r).read ())
		a.seek (0)
		b = ET.parse (a)
		self.sensor_dict = None
		for i in b.findall (self.sensors_label):
			if (i.get (self.sensors_label_id) == self.id):
				self.sensor_dict = build_tree (i)
				break
	
	def get_raw (self):
		'''
		Returns the raw dict, as presented in the original XML file
		'''
		return (self.sensor_dict)
	
	def get_mac (self):
		'''
		Returns the sensor's model, if any, None either
		'''
		return (self.sensor_dict [self.sensors_mac_field])
	
	def get_type (self):
		'''
		Returns the sensor's type
		'''
		return (self.sensor_dict [self.sensors_type_field])
	
	def get_model (self):
		'''
		Returns the sensor's model, if any, None either
		'''
		return (self.sensor_dict [self.sensors_model_field])
	
	def get_version (self):
		'''
		Returns the sensor's version
		'''
		return (self.sensor_dict [self.sensors_version_field])
	
	def get_name (self):
		'''
		Returns the sensor's name
		'''
		return (self.sensor_dict [self.sensors_name_field])
	
	def get_longname (self):
		'''
		Returns the sensor's type name in system's language and the sensor's name
		'''
		return (self.sensor_dict [self.sensors_longname_field])
	
	def get_namegender (self):
		'''
		Return M for male and F for female.
		Only usefull for languages with gender on nouns
		'''
		return (self.sensor_dict [self.sensors_namegender_field])
	
	def get_batterylevel (self):
		'''
		Returns the sensor's battery level, out of 10
		It seems that batteryless sensors return 255
		'''
		return (int (self.sensor_dict [self.sensors_batterylevel_field]))
	
	def get_signal (self):
		'''
		Returns the sensor's signal quality, out of 10
		'''
		return (int (self.sensor_dict [self.sensors_signal_field]))
	
	def get_lasttrigger (self):
		'''
		Return the timestamp of the sensor's last triger
		The sensors always trigger, even when the alarm's mode is off
		'''
		a = self.sensor_dict [self.sensors_lasttrigger_field]
		# Try because camera return the date '0000-00-00 00:00:00' that is ununderstandable
		try:
			b = datetime.strptime (a, self.sensors_lasttrigger_dateformat)
		except ValueError:
			return (0)
		r = int (b.timestamp ())
		return (r)
	
	def get_status (self):
		'''
		Returns True is the sensor is OK, False either
		'''
		return (self.sensor_dict [self.sensors_status_field] == self.sensors_status_value_ok)

class Camera (Sensor):
	'''
	Class used to manipulate easily cameras
	'''
	def __init__ (self, sensor_dict, opener):
		'''
		Initialize the class with the dict producted by HomeSFR.get_camera ()
		'''
		Sensor.__init__ (self, sensor_dict, opener)
	
	def get_snapshot (self):
		'''
		Get a snapshot from the camera
		Return a PIL.Image object
		'''
		r = self.base_url + self.camera_snapshot + '?' + self.camera_snapshot_mac + '=' + self.get_mac ()
		a = self.bytes2image (self.opener.open (r).read ())
		return (a)