#!/usr/bin/python
import os
from time import time, sleep
import threading
import RPi.GPIO as GPIO
import smbus

GPIO.setmode(GPIO.BCM)

# 1 indicates /dev/i2c-1 (port I2C1)
bus = smbus.SMBus(1)

#################################################################################
# Sensors
#################################################################################

#################################################################################
# Ultrasonic
#################################################################################

class Ultrasonic():
	'''This class is responsible for handling i2c requests to an ultrasonic sensor'''

	# i2c address of this ultrasonic sensor
	address_SRF = 0x00

	def __init__(self,address_SRF):
		self.address_SRF = address_SRF
 	
 	# Aufgabe 2
 	#
	# Diese Methode soll ein Datenbyte an den Ultraschallsensor senden um eine Messung zu starten
	def write(self,value):
		try:
			# Hier die Implementierung definieren
			####################################################
			# TODO remove code
			bus.write_byte_data(self.address_SRF, 0x00, value)
			####################################################

		except IOError:
			print "Ultrasonic: Failed to write on bus"
			return -1
		return 0

	# Aufgabe 2
	#
	# Diese Methode soll den Lichtwert auslesen und per return zurueckgeben
	# Aus welchem Register soll diese Information gelesen werden? 
	def lightlevel(self):
		light = 0

		try:
			# Hier die Implementierung definieren
			####################################################
			# TODO remove code
			light = bus.read_byte_data(self.address_SRF, 0x01)
			####################################################
		except IOError:
			print "Ultrasonic: Failed to read lightlevel on bus %x" % self.address_SRF
			return 0

		return light

	# Aufgabe 2
	#
	# Diese Methode soll die Entfernung auslesen. 
	# Welche Werte werden hierfuer benoetigt?
	# Aus welchen Registern sollen diese ausgelesen werden?
	# Wie sollen sie kombiniert werden?
	def range(self):

		total_range = 0

		try:
			# Hier die Implementierung definieren
			#####################################################
			# TODO remove code
			range_h = bus.read_byte_data(self.address_SRF, 0x02) 
			range_l = bus.read_byte_data(self.address_SRF, 0x03)
			total_range = (range_h<<8) + range_l
			#####################################################
		except IOError:
			print "Ultrasonic: Failed to read range on bus"
			return 0

		return total_range

	def getAddress(self):
		return self.address_SRF

class UltrasonicThread(threading.Thread):
	''' Thread-class for holding ultrasonic data '''

	light = -1.0
	range = -1.0

	def __init__(self, address):		
		threading.Thread.__init__(self)
		sleep(0.1)
		self.ultrasonic = Ultrasonic(address)
		self.setDaemon(True)
		self.stopped = False
		print('UltrasonicThread started')

	# Aufgabe 3
	#
	# Schreiben Sie die Messwerte in die lokalen Variablen light und range
	# Die Messwerte sollen in Zentimeter ausgegeben werden. Mit welchem Befehl soll eine Messung gestartet werden?
	def run(self):
		while not self.stopped:

			try:
				# Hier die Implementierung definieren
				#####################################################
				# TODO remove code
				self.ultrasonic.write(0x51)
				sleep(0.07)
				
				light_temp = self.ultrasonic.lightlevel()
				if light_temp > 0:
					self.light = light_temp

				range_temp = self.ultrasonic.range()
				if range_temp > 0:
					self.range = range_temp
				sleep(0.07)
				#####################################################
			except IOError, err:
				print "Error accessing 0x%02X: check your I2C address" %self.ultrasonic.getAddress() 
				return -1

	def stop(self):
		self.stopped = True

#################################################################################
# Compass
#################################################################################

class Compass(object):
	'''This class is responsible for handling i2c requests to a compass sensor'''

	# i2c address of this compass sensor
	address_COM = 0x00

	def __init__(self,address_COM):
		self.address_COM = address_COM

	# Aufgabe 2
	#
	# Diese Methode soll die Richtung auslesen. 
	# Welche Werte werden hierfuer benoetigt?
	# Aus welchen Registern sollen die ausgelesen werden?
	# Wie sollen sie kombiniert werden?
	def bearing(self):

		bear = 0

		try:
			# Hier die Implementierung definieren
			#####################################################
			# TODO remove code
			bear_h = bus.read_byte_data(self.address_COM, 0x02)
			bear_l = bus.read_byte_data(self.address_COM, 0x03)
			bear = (bear_h<<8) + bear_l
			#####################################################
		except IOError:
			print "Compass: Failed to read bus"
			return 0

		return bear/10

class CompassThread(threading.Thread):
	''' Thread-class for holding compass data '''

	
	bear = -1.0

	def __init__(self,address):
		threading.Thread.__init__(self)
		sleep(0.1)
		self.compass = Compass(address)
		self.setDaemon(True)
		self.stopped = False
		print('CompassThread started')

	# Aufgabe 3
	#
	# Diese Methode soll den Kompasswert 'bear' aktuell halten.
	# Achreiben Sie eine Schleife die das bewerkstelligt.
	def run(self):
		# Hier die Implementierung definieren
		#####################################################
		# TODO remove code
		while not self.stopped:
			self.bear = self.compass.bearing()
			sleep(0.1)
		#####################################################
	def stop(self):
		self.stopped = True

#################################################################################
# Infrared
#################################################################################

class Infrared(object):
	'''This class is responsible for handling i2c requests to an infrared sensor'''

	vMax = 5.0

	def __init__(self,address_IR):
		self.address_IR = address_IR
		bus.write_byte(self.address_IR, 0x00) # only use input 0
		
	# Aufgabe 2 
	#
	# In dieser Methode soll der gemessene Spannungswert des Infrarotsensors ausgelesen und in einen Distanzwert umgerechnet werden.
	# Wie kann der Spannungswert interpretiert werden? Erstellen Sie empirisch eine Methode die das bewerkstelligt.
	def distance(self):
		try:

			dist = 0

			# Hier die Implementierung definieren
			#####################################################
			# TODO remove code
			v_infrarot = bus.read_byte_data(self.address_IR, 0x00) 
			
			voltage = self.vMax * v_infrarot / 255.0 
			
			if voltage > 0.43 :
				#dist = 27.933* voltage**(-1.255)
				#dist = 11.7096*voltage**4 - 84.4938*voltage**3 + 228.284*voltage**2 - 284.055*voltage + 156.485
				dist = 6787/(4*v_infrarot-3)-2
				if dist > 80:
					dist = 80
			else:
				dist = 80.0
			#####################################################

		except IOError:
			print "IR: Failed to read bus"
			return 0
		return dist

class InfraredThread(threading.Thread):
	''' Thread-class for holding Infrared (IR) data '''

	ir = -1.0

	def __init__(self, address, encoder_r, encoder_l):
		threading.Thread.__init__(self)
		sleep(0.1)
		self.address = address
		self.encoder_r = encoder_r
		self.encoder_l = encoder_l
		self.infrared = Infrared(address)
		self.setDaemon(True)
		self.stopped = False
		
		self.threshold = 20 		# Distance threshold for parking lot
		self.parkinglot = 0.0
		self.led = 0
		
		print('InfraredThread started')

	def run(self):
		
		encoderDist_r_old = 0.0

		while not self.stopped:

			# Aufgabe 3
			#
			# Diese Methode soll den Infrarotwert 'ir' aktuell halten

			# Hier die Implementierung definieren
			#####################################################
			# TODO remove code
			distance = self.infrared.distance()
			if distance < 80:
				self.ir = distance
			#####################################################

			# Aufgabe 6
			#
			# Hier soll die Berechnung der Laenge der Parkluecke definiert werden

			# Hier die Implementierung definieren
			#####################################################
			# TODO remove code

			encoderDist_r = self.encoder_r.travelledDist()

			if self.ir > self.threshold:
				self.led = 1
				if encoderDist_r_old != 0.0:
					self.parkinglot += encoderDist_r - encoderDist_r_old	
			else:
				self.led = 0
				self.parkinglot = 0.0
				
			encoderDist_r_old = encoderDist_r
			sleep(0.1)
			#####################################################

	def stop(self):
		self.stopped = True

#################################################################################
# Encoder
#################################################################################
	
class Encoder(object):
	''' This class is responsible for handling encoder data '''

	# Aufgabe 2
	#
	# Wieviel cm betraegt ein einzelner Encoder-Schritt d_click?

	# Hier die Implementierung definieren
	#####################################################
	# TODO remove code
	d_click = 1.0406525665 # in cm
	#####################################################

	def __init__(self, pin):
		self.pin = pin
		GPIO.setup(self.pin, GPIO.IN)		
		self.count = 0

		# Aufgabe 2
		#
		# Jeder Flankenwechsel muss zur Berechnung der Entfernung gezaehlt werden. 
		# Definieren Sie eine Methode, die diesen Wert in der Variable 'count' speichert.

		# Hier die Implementierung definieren
		#####################################################
		# TODO remove code
		GPIO.add_event_detect(self.pin, GPIO.BOTH, callback=self.cb, bouncetime=1)

		
	# every time the encoder detects a color switch, inrease count by 1
	def cb(self,channel):
		self.count += 1
		#####################################################	

	# Aufgabe 2
	# 
	# Diese Methode soll die gesamte zurueckgelegte Distanz zurueckgeben.
	def travelledDist(self):
		# Hier die Implementierung definieren
		#####################################################
		# TODO remove code
		self.D = self.count * self.d_click
		return self.D
		#####################################################

	def stop(self):
		GPIO.remove_event_detect(self.pin) 

class SpeedThread(threading.Thread):
	''' Thread-class for holding speed and distance data '''

	speed_r = 0.0
	speed_l = 0.0

	def __init__(self, encoder_r, encoder_l, encoder_fr=None, encoder_fl=None):
		threading.Thread.__init__(self)
		sleep(0.1)
		self.stopped = False

		self.encoder_r = encoder_r
		self.encoder_l = encoder_l

		self.speed_r = 1.0
		self.cur_dist_r = 0.0

		self.speed_l = 1.0
		self.cur_dist_l = 0.0

		self.start()
		print('SpeedThread started')

	# Aufgabe 3
	#
	# Diese Methode soll die aktuelle Geschwindigkeit der beiden Raeder sowie die zurueckgelegte Distanz aktuell halten.
	def run(self):

		while not self.stopped:

			# Hier die Implementierung definieren
			#####################################################
			# TODO remove code
			curr_dist_r = self.encoder_r.travelledDist()
			curr_dist_l = self.encoder_l.travelledDist()
			sleep(0.5)
			self.cur_dist_r = self.encoder_r.travelledDist() - curr_dist_r
			self.cur_dist_l = self.encoder_l.travelledDist() - curr_dist_l
			#self.cur_dist_r = self.encoder_r.travelledDist()
			#self.cur_dist_l = self.encoder_l.travelledDist()
			self.speed_r = self.cur_dist_r * 100 / 0.5			
			self.speed_l = self.cur_dist_l * 100 / 0.5
			#####################################################

			# Aufgabe 4
			#
			# Hier soll die Erkennung und Korrektur der Messfehler erstellt werden.

			# Hier die Implementierung definieren
			##################################################### 


			#####################################################


	def getDist(self, whichOne=None):
		if   whichOne == 'r':
			return self.cur_dist_r
		elif whichOne == 'l':
			return self.cur_dist_l

	def stop(self):
		self.stopped = True

#################################################################################
# Main Thread
#################################################################################	

if __name__ == "__main__":

	# The GPIO pins to which the encoders are connected
	encoder_pin_right = 22
	encoder_pin_left = 23

	# Aufgabe 1
	#
	# Tragen Sie die herausgefundenen i2c Adressen der Sensoren hier ein

	# Hier die Implementierung definieren
	##############################################################
	# TODO remove code

	# The i2c addresses of fornt and rear ultrasound sensors
	ultrasonic_front_i2c_address = 0x70;
	ultrasonic_rear_i2c_address = 0x71;

	# The i2c address of the compass sensor
	compass_i2c_address = 0x60 

	# The i2c address of the infrared sensor
	infrared_i2c_address = 0x4F
	#############################################################


	# Aufgabe 5 
	#
	# In dieser Aufgabe sollen saemtlichen Messwerte auf der Konsole ausgegeben werden.
	# Erstellen Sie eine Schleife die das bewerkstelligt

	
	# Hier die Implementierung definieren
	##############################################################################################
	# TODO remove code

	#################################################################################
	# Ultrasonic
	#################################################################################

	# Threads managing the data from the ultrasound sensors have to be created and started
	ultrasonic_front_thread = UltrasonicThread(ultrasonic_front_i2c_address)
	ultrasonic_front_thread.start()

	ultrasonic_rear_thread = UltrasonicThread(ultrasonic_rear_i2c_address)
	ultrasonic_rear_thread.start()
	
	#################################################################################
	# Compass
	#################################################################################

	# Thread managing the data from the compass sensor has to be created and started
	compass_thread = CompassThread(compass_i2c_address)
	compass_thread.start()
	
	#################################################################################
	# Encoder
	#################################################################################

	# encoder objects to be passed to encoder and infrared threads
	encoder_right = Encoder(encoder_pin_right)
	encoder_left = Encoder(encoder_pin_left)
	
	# Thread managing the data from the encoders
	speed_thread = SpeedThread(encoder_right, encoder_left)
	
	#################################################################################
	# Infrared
	#################################################################################

	# Thread managing the data from the infrared sensor has to be created and started
	infrared_thread = InfraredThread(infrared_i2c_address, encoder_right, encoder_left)
	infrared_thread.start()
	
	# Our program is running while this is true
	running = True
	
	try:
		while running:
			
			# Get the data from the front ultrasound sensor
			light_value_front = ultrasonic_front_thread.light
			range_value_front = ultrasonic_front_thread.range

			# Get the data from the rear ultrasound sensor
			light_value_rear = ultrasonic_rear_thread.light
			range_value_rear = ultrasonic_rear_thread.range

			# Get the data from the infrared sensor
			infrared_value = infrared_thread.ir
			infrared_parkinglot = infrared_thread.parkinglot

			# Get the data from the compass
			bear = compass_thread.bear

			# os.system('clear')
			print('range (%s,%s) cm  -- light(%s,%s) ========== bear: %s degrees ======= IR: %s' % (range_value_front,range_value_rear,light_value_front,light_value_rear,bear,infrared_value))
			# if (bear >= 0 and bear < 45):
			# 	print ('    |    \n')
			# 	print ('    |    \n')
			# 	print ('         \n')
			# 	print ('         \n')
			# elif (bear >= 45 and bear < 90):
			# 	print ('       / \n')
			# 	print ('     /   \n')
			# 	print ('         \n')
			# 	print ('         \n')
			# elif (bear >= 90 and bear < 135):
			# 	print ('         \n')
			# 	print ('     ___ \n')
			# 	print ('         \n')
			# 	print ('         \n')
			# elif (bear >= 135 and bear < 180):
			# 	print ('         \n')
			# 	print ('         \n')
			# 	print ('     \   \n')
			# 	print ('       \ \n')
			# elif (bear >= 180 and bear < 225):
			# 	print ('         \n')
			# 	print ('         \n')
			# 	print ('     |   \n')
			# 	print ('     |   \n')
			# elif (bear >= 225 and bear < 270):
			# 	print ('         \n')
			# 	print ('         \n')
			# 	print ('   /     \n')
			# 	print (' /       \n')
			# elif (bear >= 270 and bear < 315):
			# 	print ('         \n')
			# 	print (' ___     \n')
			# 	print ('         \n')
			# 	print ('         \n')
			# elif (bear >= 315 and bear < 360):
			# 	print (' \       \n')
			# 	print ('   \     \n')
			# 	print ('         \n')
			# 	print ('         \n')
			print('===== Bear: %s =====' % bear)
			print('===== Parkinglot: %s =====' % infrared_parkinglot)

			# Get the distance data from the encoders
			distance_left = speed_thread.getDist('l')
			distance_right = speed_thread.getDist('r')

			# Get the speed data from the encoders
			speed_right = speed_thread.speed_r
			speed_left = speed_thread.speed_l

			print('-- travelled distance: ')
			print('left: %6.2f cm and right: %6.2f -- speed_l  %4.2f speed_r  %4.2f --' % (distance_left, distance_right, speed_left, speed_right))

			sleep(0.1)
			os.system('clear')
	except KeyboardInterrupt:
		print '\nexiting...'
		
		speed_thread.stop()
		ultrasonic_front_thread.stop()
		ultrasonic_rear_thread.stop()
		compass_thread.stop()
		infrared_thread.stop()	
		
		speed_thread.join()
		ultrasonic_rear_thread.join()
		ultrasonic_front_thread.join()
		compass_thread.join()
		infrared_thread.join()
		
		encoder_right.stop()
		encoder_left.stop()
		
		GPIO.cleanup()
		sleep(1)
		print "All Threads stopped"
	##############################################################################################
