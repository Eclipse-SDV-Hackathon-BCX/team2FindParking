#!/usr/bin/python
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import io
import os

import threading

from math import acos, sqrt, degrees


# This Part of the code offers an index.html file at port 8081
##############################################################################################
#port definition
from tornado.options import define, options
define("port", default=8081, help="run on the given port", type=int)


class IndexHandler(tornado.web.RequestHandler):
	#tornado.web.asynchronous
	def get(self):
		self.render("index.html")
##############################################################################################

# Aufgabe 3
#
# Der Tornado Webserver muss eine Liste der clients verwalten.
# Erweitern Sie hierfuer die Methoden 'open' und 'close'

class WebSocketHandler(tornado.websocket.WebSocketHandler):
	'''Definition der Operationen des WebSocket Servers'''

	# print "hello WebSocketHandler"

	def open(self):
		# Hier die Implementierung definieren
		##############################################################################################
		# TODO remove code
		print('new connection from: {}'.format(self.request.remote_ip))
		clients.append(self)
		##############################################################################################

	def on_message(self, message):
		print('message received %s' % message)
		# if message == 'StartParking':
		# # 	# Start Parking
        #     print("start Parking")
		# if message == 'StopParking':
        #     print("stop Parking")

	def on_close(self):
		# Hier die Implementierung definieren
		##############################################################################################
		# TODO remove code
		print('connection closed from: {}'.format(self.request.remote_ip))
		clients.remove(self)
		##############################################################################################

	def check_origin(self, origin):
    		return True


	# def run(self):
##### clientss write on socket
		# for c in clients:
		# 	c.write_message(data)

		 # "All Threads stopped"

if __name__ == "__main__":

	try:

		# Aufgabe 3
		#
		# Erstellen Sie hier eine Instanz des DataThread und starten Sie den Webserver

		# Hier die Implementierung definieren
		##############################################################################################
		# TODO remove code
		clients = []
		tornado.options.parse_command_line()
		app = tornado.web.Application(handlers=[(r"/ws", WebSocketHandler), (r"/", IndexHandler), (r'/(.*)', tornado.web.StaticFileHandler, {'path': os.path.dirname(__file__)}),])
		# print "app", app
		httpServer = tornado.httpserver.HTTPServer(app)
		# print "httpServer", httpServer
		httpServer.listen(options.port)
		# print "Listening on port:", options.port
		tornado.ioloop.IOLoop.instance().start()


	except KeyboardInterrupt:
		# print '\nexiting...'

		tornado.ioloop.IOLoop.instance().stop()
		sleep(1)
		# print "End of Code"
