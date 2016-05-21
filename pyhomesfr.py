#!/usr/bin/python3
'''
Home by SFR wrapping class
Plain use of your Home by SFR device from a Python library

Warning:
This is a wrap aroud website, this could stop working without prior notice

Note about version naming:
The version are formed like <major>.<minor>-<date>
Since the major 1, the method's names, paramters and their default value will never change inside the same major.
So, if a program using a major does not work anymore with another version from the same major, it's a bug from the library.

The major 0 is a testing one
'''

# TODO:
## Return sensors in a class
## Manage cameras
### Get image
### Get video
## Manage logs
## Import/Export cookies

authors = (
	'Gilles "Almtesh" Émilien MOREL',
	)
name = 'pyhomesfr'
version = '0.8-20160521'

# Settable modes
MODE_OFF = 0
MODE_CUSTOM = 1
MODE_ON = 2

from urllib import request
from http.cookiejar import CookieJar
from urllib.parse import urlencode
from xml.etree import ElementTree as ET
from urllib.error import HTTPError

def bytes2file (b):
	'''
	Gives a file-like class from a Bytes
	'''
	from io import BytesIO
	r = BytesIO ()
	r.write (b)
	r.seek (0)
	return (r)

def bytes2image (b):
	'''
	Gives a Image object from bytes
	Uses the bytes2file function
	'''
	from PIL import Image
	f = bytes2file (b)
	r = Image ()
	r.open (f)
	return (r)

class HomeSFR ():
	def __init__ (self, username, password, debug = False, autologin = True):
		'''
		Sets the class with username and password
		The debug parameter defines if the class will write debug messages to stdout, if False, the stdout will never be writen by the class
		The autologin parameter defines if the class will manage the login by itself, if False, the user must call login () to login and test_login () to check the login
		'''
		self.DEBUG = debug
		if self.DEBUG:
			print (name + ' ' + version)
			print ('Authors:')
			for i in authors:
				print (' - ' + i)
			print ('init with username ' + username)
			print ('debug = ' + str (debug))
			print ('autologin = ' + str (autologin))
		
		self.username = username
		self.password = password
		self.autologin = autologin
		self.cookies = CookieJar ()
		self.opener = request.build_opener (request.HTTPCookieProcessor (self.cookies))
		
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
		
		# Path to sensors and mode
		self.sensors_list = '/mysensors'
		self.sensors_label = 'Sensor'
		self.sensors_label_id = 'id'
		
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
		# mac=00:0e:8f:c9:59:44&flip=0&led_mode=0&alert_pan=1&rec24=0&da=1&dp=4&name=Salon
		self.cameras_list = '/homescope/mycams'
		self.camera_snapshot = '/homescope/snapshot'
		self.camera_video = '/homescope/flv'
		self.camera_get_config_path = '/homescope/camsettings'
		self.camera_set_config_path = '/homescope/camsettings'
		self.camera_set_config_mac = 'mac'
		self.camera_set_config_flip = 'flip'
		self.camera_set_config_leds = 'led_mode' # set to 0 to turn the leds on
		self.camera_set_config_detectionsensibility = 'dp' # from 1 to 4,
	
	def __str__ (self):
		'''
		Shows name, version, defined user and debug state
		'''
		return (name + ' ' + version + '\nUser: ' + self.username + '\nDebug: ' + str (self.DEBUG))
	
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
		Return True if the login was a success, False either
		'''
		self.opener.open (self.auth_referer)
		data = self.auth_extra_fields
		data [self.auth_user_field] = self.username
		data [self.auth_pass_field] = self.password
		data = bytes (urlencode (data), 'UTF8')
		if self.DEBUG:
			print ('Cookies ' + str( len(self.cookies)))
			print ('Sending data ' + str (data))
		a = self.opener.open (self.auth_post_url, data = data)
		if self.DEBUG:
			print ('Auth redirected to ' + a.geturl ())
		return (a.geturl () == self.base_url + self.auth_ok)
	
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
		a = bytes2file (self.opener.open (r).readall ())
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
		a = bytes2file (self.opener.open (r).readall ())
		b = ET.parse (a)
		r = []
		for i in b.findall (self.sensors_label):
			r.append (i.get (self.sensors_label_id))
		return (list (r))
	
	def get_sensor (self, id):
		'''
		Returns a dict of all variables for the sensor id or None if sensor is not found
		The available ids can be got from the list_sensors method
		'''
		def build_tree (element):
			r = {}
			if self.DEBUG:
				print ('Diving in the element ' + element.tag)
			for i in element.getchildren ():
				if i.getchildren () == []:
					r.update ({i.tag: i.text})
				else:
					r.update ({i.tag: build_tree (i)})
			return (r)
		if (self.autologin and self.test_login () == False):
			self.login ()
		r = self.base_url + self.sensors_list
		a = bytes2file (self.opener.open (r).readall ())
		b = ET.parse (a)
		r = None
		for i in b.findall (self.sensors_label):
			if self.DEBUG:
				print ('Testing sensors ' + i.get (self.sensors_label_id))
			if (i.get (self.sensors_label_id) == id):
				r = build_tree (i)
				break
		return (r)
	
	def get_all_sensors (self):
		'''
		Returns a tuple of dicts as described in the get_sensor method
		'''
		r = []
		for i in self.list_sensors ():
			r.append (self.get_sensor (i))
		return (list (r))