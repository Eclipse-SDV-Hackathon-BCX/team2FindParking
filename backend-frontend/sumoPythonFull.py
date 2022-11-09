#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  8 11:55:03 2022

@author: edmir
"""

import json

import socket
ClientMultiSocket = socket.socket()
host = '127.0.0.1'
port = 8081
print('Waiting for connection response')
try:
    ClientMultiSocket.connect((host, port))
    print('stuck here')

except socket.error as e:
    print(str(e))
res = ClientMultiSocket.recv(port)



#    res = ClientMultiSocket.recv(1024)
#    print(res.decode('utf-8'))

from time import sleep
import os, sys
if 'SUMO_HOME' in os.environ:
	tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
	sys.path.append(tools)
else:
	sys.exit("please declare environment variable 'SUMO_HOME'")

sumoBinary = "/home/edmir/src/manProProject/sumo-1.8.0/bin/sumo-gui"
sumoCmd = [sumoBinary, "-c", "/home/edmir/src/manProProject/plexe-veins/examples/mergingManeuver/s/s/58.sumocfg"]

import traci
import traci.constants as tc
traci.start(sumoCmd)
step =0
vehID = "mainline.0"
while step < 1000:
    if step%10 == 0:
        print(traci.vehicle.getIDList())
        idLst = traci.vehicle.getIDList()
        for car in idLst:
            pos = str(traci.vehicle.getPosition(car)[0])+" "+str(traci.vehicle.getPosition(car)[1])
            data = json.dumps([car, {'position': pos}])


            print(pos)
            ClientMultiSocket.send(str.encode(data))
        traci.simulationStep()

        #   traci.vehicle.subscribe("mainline.0", (tc.VAR_ROAD_ID, tc.VAR_LANEPOSITION))
        #   print(traci.vehicle.getSpeed(vehID))
        #   if traci.inductionloop.getLastStepVehicleNumber("0") > 0:
        #       traci.trafficlight.setRedYellowGreenState("0", "GrGr")
    step += 1

    sleep(0.1)
ClientMultiSocket.close()
traci.close()
