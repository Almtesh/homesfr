# WARNING: ce code s'appuie sur une API découverte par rétro-ingénérie.
# Il peut cesser de fonctionner sans préavis.

# TODO:
##

from urllib import request
from http.cookiejar import CookieJar
from urllib.parse import urlencode
from urllib.error import HTTPError

authors = (
	'Gilles "Almtesh" Émilien MOREL',
)
name = 'homesfr pour Python 3'
version = '1.3'

# Modes utilisables
MODE_OFF = 0
MODE_CUSTOM = 1
MODE_ON = 2

# Types de capteurs
PRESENCE_DETECTOR = 'PIR_DETECTOR'			# https://boutique.home.sfr.fr/detecteur-de-mouvement
MAGNETIC_OPENNING_DETECTOR = 'MAGNETIC'			# https://boutique.home.sfr.fr/detecteur-d-ouverture-de-porte-ou-fenetre
SMOKE_DETECTOR = 'SMOKE'				# https://boutique.home.sfr.fr/detecteur-de-fumee
SIREN = 'SIREN'						# https://boutique.home.sfr.fr/sirene-interieure (et peut-être https://boutique.home.sfr.fr/sirene-exterieure)
REMOTE_CONTROLER = 'REMOTE'				# https://boutique.home.sfr.fr/telecommande
KEYPAD_CONTROLER = 'KEYPAD'				# https://boutique.home.sfr.fr/clavier-de-commande
PRESENCE_CAMERA_DETECTOR = 'PIR_CAMERA'			# https://boutique.home.sfr.fr/camera
TEMPHUM_SENSOR = 'TEMP_HUM'				# https://boutique.home.sfr.fr/thermometre
ONOFF_PLUG = 'ON_OFF_PLUG'				# https://boutique.home.sfr.fr/prise-commandee-connectee-legrand

base_url = 'https://home.sfr.fr'

# Authentification
auth_path = '/mysensors'
auth_ok_url = 'https://home.sfr.fr/logged'
auth_post_url = 'https://boutique.home.sfr.fr/authentification'
auth_referer = 'https://boutique.home.sfr.fr/authentification?back=service'
auth_user_field = 'email'
auth_pass_field = 'passwd'
auth_extra_fields = {'back': 'service', 'token_sso': '', 'error_sso': '', 'SubmitLogin': 'OK'}
auth_logout_path = '/deconnexion'

# Chemin pour la liste des capteurs
sensors_list = '/mysensors'

# Chemin pour les alertes
alerts_path = '/listalert'

# Détection
mode_get_path = '/mysensors'
mode_get_label = 'alarm_mode'
mode_set_path = '/alarmmode'
mode_set_field = 'action'				# Name for GET field
mode_off = 'OFF'					# Value for off
mode_custom = 'CUSTOM'					# Value for custom
mode_on = 'ON'						# Value for on

# Caméra
cameras_list = '/homescope/mycams'
camera_snapshot = '/homescope/snapshot?size=4'
camera_snapshot_mac = 'mac'
camera_video = '/homescope/flv'
camera_video_mac = 'mac'
camera_recordings_list = '/listenr'
camera_recordings_delete = '/delenr'
camera_recordings_start = '/homescope/record'
camera_recordings_stop = '/homescope/stoprecord'
camera_recordings_mac = 'mac'
camera_get_config_path = '/homescope/camsettings'
camera_get_config_mac = 'mac'
camera_get_config_flip = 'FLIP'
camera_get_config_leds = 'LEDMODE'
camera_get_config_petmode = 'pet_mode'
camera_get_config_recording = 'rec24'
camera_get_config_privacy = 'privacy'
camera_get_config_name = 'NAME'
camera_set_config_path = '/homescope/camsettings'
camera_set_config_mac = 'mac'
camera_set_config_flip = 'flip'
camera_set_config_leds = 'led_mode'
camera_set_config_petmode = 'pet_mode'
camera_set_config_recording = 'rec24'
# Le paramètre privacy se gère avec le bouton derrière la caméra.
camera_set_config_name = 'name'

# Capteurs
sensors_list = '/mysensors'
sensors_label = 'Sensor'
sensors_label_id = 'id'
sensors_mac_field = 'deviceMac'
sensors_type_field = 'deviceType'
sensors_model_field = 'deviceModel'
sensors_version_field = 'deviceVersion'
sensors_name_field = 'name'
sensors_longname_field = 'long_name'
sensors_namegender_field = 'name_gender'
sensors_batterylevel_field = 'batteryLevel'
sensors_signal_field = 'signalLevel'
sensors_status_field = 'status'
sensors_status_value_ok = 'OK'

# Capteurs de température et humidité
sensors_temphum_root_field = 'sensorValues'
sensors_temp_name = 'name'
sensors_temp_text = 'Temperature'
sensors_hum_name = 'name'
sensors_hum_text = 'Humidity'

# Prise connectée (ON_OFF_PLUG)
sensors_oop_stateroot = 'automation'
sensors_oop_state = 'on_off'
sensors_oop_power = 'power_level'

# Fil d'événements
logs_path = '/getlog?page=1&nbparpage=10000'		# je pense qu'on récupère tous les événements avec cette valeur
logs_labels = 'LOG'


def bytes2file (b):
	'''
	Retourne une classe semblable à un fichier contant b
	'''
	from io import BytesIO
	r = BytesIO ()
	r.write (b)
	r.seek (0)
	return (r)


def bytes2image (b):
	'''
	Retourne une Image PIL contenant l'image donnée en b
	'''
	from PIL import Image
	f = bytes2file (b)
	r = Image.open (f)
	return (r)


def get_xml_tree (fp):
	'''
	Retourne une variable itérable contenant les données d'un arbre XML
	'''
	def build_tree (element):
		if tuple (element) == ():
			return (element.tag, dict (element.items ()), element.text)
		else:
			sub = []
			for i in element:
				sub.append (build_tree (i))
			return (element.tag, dict (element.items ()), sub)
	from xml.etree import ElementTree as ET
	fp.seek (0)
	root = ET.parse (fp).getroot ()
	return (build_tree (root))


class HomeSFR ():
	def __init__ (self, username = None, password = None, cookies = None, debug = False, autologin = True):
		'''
		Instancie la classe avec un identifiant et un mot de passe, ou des cookies
		On peut définir les identifiants et les cookies, la classe utilisera les cookies par défaut et les identifiants si on n'est pas connecté
		debug fourni des informations supplémentaires sur la sortie standard, s'il est à False, cette classe n'envoie rien sur la sortie standard
		'''
		self.DEBUG = debug
		if self.DEBUG:
			print (name + ' ' + version)
			print ('Auteurs:')
			for i in authors:
				print (' - ' + i)
			if username is not None:
				print ('initalisé avec l\'identifiant ' + username)
			if cookies is not None:
				print ('initialisé avec des cookies')
			print ('debug = ' + str (debug))
			print ('autologin = ' + str (autologin))
		
		if (username is None or password is None) and cookies is None:
			raise TypeError ('Vous devez définir des identifiant ou des cookies !')
		self.username = username
		self.password = password
		if self.username is not None and self.password is not None:
			self.autologin = autologin
		else:
			self.autologin = False
		if cookies is None:
			self.cookies = CookieJar ()
		elif type (cookies) == CookieJar:
			self.cookies = cookies
		else:
			raise TypeError ('Les cookies doivent être de type CookieJar !')
		self.opener = request.build_opener (request.HTTPCookieProcessor (self.cookies))
	
	def __str__ (self):
		'''
		Returne des informations sur l'état de l'instance
		'''
		if self.username is not None:
			return (name + ' ' + version + '\nUtilisateur : ' + self.username + '\nDebug : ' + str (self.DEBUG))
		else:
			return (name + ' ' + version + '\nUtilisateur : Inconnu, authentifié avec des cookies.\nDebug : ' + str (self.DEBUG))

	def test_login (self):
		'''
		Retourne l'état de l'authentification
		'''
		try:
			if self.DEBUG:
				print ('Test de l\'authentification')
			self.opener.open (base_url + auth_path)
		except HTTPError:
			if self.DEBUG:
				print ('Non connecté')
			return (False)
		if self.DEBUG:
			print ('Connecté')
		return (True)
	
	def login (self):
		'''
		S'authentifier auprès du service
		Retourne True si c'est réussi, False sinon
		Si seuls les cookies sont définis, la méthode retournera False, même si nous sommes authentifiés, pour savoir si on est authentifiés, utiliser test_login ()
		'''
		if self.username is not None and self.password is not None:
			self.opener.open (auth_referer)
			data = auth_extra_fields
			data [auth_user_field] = self.username
			data [auth_pass_field] = self.password
			data = bytes (urlencode (data), 'UTF8')
			if self.DEBUG:
				print ('Cookies ' + str (len (self.cookies)))
				print ('Envoi de ' + str (data))
			a = self.opener.open (auth_post_url, data = data)
			if self.DEBUG:
				print ('Authentification redirigée vers ' + a.geturl ())
			return (a.geturl () == auth_ok_url)
		else:
			return (False)
	
	def get_or_autologin (self, url, data = None):
		'''
		Fais une requête, si une erreur 403 est retourné, tente une authentification automatiquement (si réglé dans le paramètre autologin), sinon lève une exception
		'''
		try:
			return (self.opener.open (url, data = data))
		except HTTPError as e:
			if '403' in str (e) and self.autologin:
				self.login ()
				return (self.opener.open (url, data = data))
			else:
				raise e
	
	def logout (self):
		'''
		Se déconnecter
		L'instance devrait être supprimée après l'appel de cette fonction
		'''
		if self.DEBUG:
			print ('Demande de déconnexion')
		self.opener.open (base_url + auth_logout_path)
		if self.DEBUG:
			print ('Destruction des cookies')
		del self.cookies
		self.cookies = None
		return (None)
	
	def get_cookies (self):
		'''
		Récupérer les cookies
		Il est recommandé de supprimer l'instance après cette fonction
		'''
		return (self.cookies)
	
	def set_mode (self, mode):
		'''
		Modifie le mode de détection
		'''
		if mode == MODE_OFF:
			m = mode_off
		elif mode == MODE_CUSTOM:
			m = mode_custom
		elif mode == MODE_ON:
			m = mode_on
		else:
			if self.DEBUG:
				print ('Vous devriez utiliser les constantes MODE_OFF, MODE_ON et MODE_CUSTOM.')
			raise ValueError
		r = base_url + mode_set_path + '?' + mode_set_field + '=' + m
		if self.DEBUG:
			print ('Demande ' + r)
		self.get_or_autologin (r)
		return (True)
	
	def get_mode (self):
		'''
		Retourne le mode de détection
		'''
		r = base_url + mode_get_path
		if self.DEBUG:
			print ('Demande ' + r)
		a = bytes2file (self.get_or_autologin (r).read ())
		b = get_xml_tree (a) [1]
		c = b [mode_get_label]
		if self.DEBUG:
			print ('Mode de détection ' + c)
		if (c == mode_off):
			return (MODE_OFF)
		if (c == mode_custom):
			return (MODE_CUSTOM)
		if (c == mode_on):
			return (MODE_ON)
		return (None)
	
	def list_sensors (self):
		'''
		Retourne une liste des IDs des capteurs
		'''
		r = base_url + sensors_list
		a = bytes2file (self.get_or_autologin (r).read ())
		b = get_xml_tree (a)
		r = []
		for i in b [2]:
			try:
				r.append (i [1] [sensors_label_id])
			except KeyError:
				pass
		return (list (r))
	
	def get_sensor (self, id):
		'''
		Retourne un objet Sensor à partir de l'ID
		'''
		r = Sensor (id, self.get_or_autologin)
		r.refresh ()
		return (r)
	
	def get_all_sensors (self):
		'''
		Retourne un tuple d'objet Sensor contenant tous les capteurs
		'''
		r = []
		for i in self.list_sensors ():
			r.append (self.get_sensor (i))
		return (tuple (r))


class Sensor ():
	def __init__ (self, id, get_or_autologin):
		
		self.id = id
		self.sensor_dict = None
		self.get_or_autologin = get_or_autologin
	
	def refresh (self):
		'''
		Mets à jour les données du capteur
		'''
		
		r = base_url + sensors_list
		self.sensor_dict = None
		for i in get_xml_tree (bytes2file (self.get_or_autologin (r).read ())) [2]:
			if i [0] == sensors_label and i [1] [sensors_label_id] == self.id:
				self.sensor_dict = i [2]
				break
	
	def get_raw (self):
		'''
		Retourne les données brutes du capteur
		'''
		return (self.sensor_dict)
	
	def get_attributes (self, lst, key):
		for i in lst:
			if i [0] == key:
				return (i [1])
		raise KeyError ('no key ' + key)
	
	def get_value (self, lst, key):
		for i in lst:
			if i [0] == key:
				return (i [2])
		raise KeyError ('no key ' + key)
	
	def get_mac (self):
		'''
		Retourne l'adresse matérielle du capteur, s'il en a une
		'''
		return (self.get_value (self.sensor_dict, sensors_mac_field))
	
	def get_type (self):
		'''
		Retourne le type du capteur
		Les types sont ceux définis dans les constantes
		'''
		return (self.get_value (self.sensor_dict, sensors_type_field))
	
	def get_model (self):
		'''
		Retourne le modèle du capteur
		'''
		return (self.get_value (self.sensor_dict, sensors_model_field))
	
	def get_version (self):
		'''
		Retourne la version du capteur
		'''
		return (self.get_value (self.sensor_dict, sensors_version_field))
	
	def get_name (self):
		'''
		Retourne le nom du capteur
		'''
		return (self.get_value (self.sensor_dict, sensors_name_field))
	
	def get_longname (self):
		'''
		Retourne un nom long du capteur composé de son type en français et de son nom
		'''
		return (self.get_value (self.sensor_dict, sensors_longname_field))
	
	def get_namegender (self):
		'''
		Retourne le genre du nom du type de capteur en français
		M pour masculin et F pour féminin
		'''
		return (self.get_value (self.sensor_dict, sensors_namegender_field))
	
	def get_batterylevel (self):
		'''
		Retourne le niveau de batterie sur 10
		Toute autre valeur doit être considérée comme venant d'un capteur n'ayant pas de batterie
		'''
		return (int (self.get_value (self.sensor_dict, sensors_batterylevel_field)))
	
	def get_signal (self):
		'''
		Retourne le niveau de signal sur 10
		Tout autre valeur est pour un capteur connecté par câble
		'''
		return (int (self.get_value (self.sensor_dict, sensors_signal_field)))
	
	def get_status (self):
		'''
		Retourne True si le capteur est considéré comme opérationnel par le système
		'''
		return (self.get_value (self.sensor_dict, sensors_status_field) == sensors_status_value_ok)
	
	def get_camera_snapshot (self):
		'''
		Retourne une capture de la caméra dans un objet PIL.Image
		'''
		r = base_url + camera_snapshot + '&' + camera_snapshot_mac + '=' + self.get_mac ()
		a = bytes2image (self.get_or_autologin (r).read ())
		return (a)
	
	def get_camera_petmode (self):
		'''
		Retourne l'état du mode animaux domestiques
		Ce mode réduit la sensibilité du capteur pour éviter des déclanchements d'alarme dus aux animaux
		'''
		return (self.sensor_dict [camera_get_config_petmode] == '1')
	
	def get_camera_recording (self):
		'''
		Retourne l'état de l'enregistrement vidéo 24/24
		'''
		return (self.sensor_dict [camera_get_config_recording] == '1')
	
	def get_camera_privacy (self):
		'''
		Si cette méthode retourne True, la caméra est paramétrée pour ne pas capture d'image
		'''
		return (self.sensor_dict [camera_get_config_privacy] == '1')
	
	def get_temperature (self):
		'''
		Retourne la température donnée par le capteur
		'''
		a = self.get_value (self.sensor_dict, sensors_temphum_root_field)
		for i in a:
			if i [1] [sensors_temp_name] == sensors_temp_text:
				return (float (i [2].replace ('°C', '')))
	
	def get_humidity (self):
		'''
		Retourne l'humidité donnée par le capteur
		'''
		a = self.get_value (self.sensor_dict, sensors_temphum_root_field)
		for i in a:
			if i [1] [sensors_hum_name] == sensors_hum_text:
				return (int (i [2].replace ('%', '')))
	
	def get_on_off_state (self):
		'''
		Retourne l'état d'une prise connectée, True sur la prise est fermée
		'''
		a = self.get_attributes (self.sensor_dict, sensors_oop_stateroot)
		return (True if a [sensors_oop_state] == '1' else False)
	
	def get_on_off_power (self):
		'''
		Retourne la puissance active qui traverse la prise, en watts
		'''
		a = self.get_attributes (self.sensor_dict, sensors_oop_stateroot)
		return (int (a [sensors_oop_power]))