import asyncio
 
import websockets
import threading

from time import sleep
import os, sys
import json

class globals:
    data = "sample data"
    targetPS = "pa-1"
    parkingSpaces = []
    infoRecv = False
    parkStatus = -1
    lastUpdate = -1
    

if 'SUMO_HOME' in os.environ:
	tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
	sys.path.append(tools)
else:
	sys.exit("please declare environment variable 'SUMO_HOME'")

sumoBinary = "/usr/bin/sumo-gui"
sumoCmd = [sumoBinary, "-c", "/home/shule/Desktop/bcx22/bcx22/Sumo-parking-Town01/Town01_1.sumocfg"]

import traci
import traci.constants as tc

traci.start(sumoCmd)

class ParkingSpace():
    def __init__(self, name, lanePosition, status,lstUpdate):
        self.name = name    # instance variable unique to each instance
        self.lane =  lanePosition
        self.status = status
        self.lstUpdate = lstUpdate

    def changeStatus(self, status, lstUpdate):
        self.status = status
        self.lstUpdate = lstUpdate

def paExists(parkArea):
    for pS in globals.parkingSpaces:
        if pS.name == parkArea:
            return True
    return False

def updateStatus(parkArea, status, lstUpdate):
    for pS in globals.parkingSpaces:
        if pS.name == parkArea:
            pS.changeStatus(status, lstUpdate)

def updateParkingStatus(parkArea):
    lstUpdate = traci.simulation.getTime()
    sts = False    
    infoRecv = False

    paCapacity = traci.simulation.getParameter(parkArea, "parkingArea.capacity")
    paOccupancy = traci.parkingarea.getVehicleCount(parkArea)
    paLane = traci.parkingarea.getLaneID(parkArea)
    if paOccupancy < int(paCapacity):
        sts = True
    if paExists(parkArea):
        updateStatus(parkArea, sts, lstUpdate)
    else:
        globals.parkingSpaces.append(ParkingSpace(parkArea,paLane, sts, lstUpdate))

def parking(car):
    detectCarPos = traci.vehicle.getLanePosition(car)
    detectCarLane = traci.vehicle.getLaneID(car)
    parkingAreas = traci.parkingarea.getIDList()
    for parkArea in parkingAreas:
        parkAreaLane = traci.parkingarea.getLaneID(parkArea)
        if parkAreaLane == detectCarLane:
            startPark = traci.parkingarea.getStartPos(parkArea)
            endPark =   traci.parkingarea.getEndPos(parkArea)
            if startPark < detectCarPos < endPark:
                print('car Passed through')
                updateParkingStatus(parkArea)

def egoCarUpdate():
    if paExists(globals.targetPS):
        globals.infoRecv = True
        for ps in globals.parkingSpaces:
            if ps.name == globals.targetPS:
                globals.parkStatus = ps.status
                globals.lastUpdate = ps.lstUpdate

def thread_function(name):
    step = 0
    vehID = "mainline.0"

    
    while step < 10000:
        if step%1 == 0:
            #print(traci.vehicle.getIDList())
            idLst = traci.vehicle.getIDList()
            #print(traci.parkingarea.getIDList())
            dataArray = []
            for car in idLst:
                #pos = str(traci.vehicle.getPosition(car)[0])+" "+str(traci.vehicle.getPosition(car)[1])
                routeId = traci.vehicle.getRoute(car)
                print("routeId: " + str(routeId) + "\n")
                #distanceToEnd = 
                pos = (traci.vehicle.getPosition(car)[0], traci.vehicle.getPosition(car)[1])
                print('speed ' + str(traci.vehicle.getSpeed(car) * 3.6))
                if car[:4] == 'dete':
                    parking(car)
                if car[:3] == 'ego':
                    egoCarUpdate()
                    lastUpdateTime = -1
                    if globals.lastUpdate != -1:
                        lastUpdateTime = traci.simulation.getTime()-globals.lastUpdate
                    parked = False
                    if(traci.vehicle.getStopState(car) > 0):
                        parked = True
                    dataArray.append([car, {'position': pos, 'speed': traci.vehicle.getSpeed(car) * 3.6, 'infoReceived': globals.infoRecv, 'status': globals.parkStatus, 'lastUpdate': globals.lastUpdate, 'lastUpdateTime': lastUpdateTime, 'parked': parked}])

            globals.data = json.dumps(dataArray)
                #print(pos)
            traci.simulationStep()
            
            #   traci.vehicle.subscribe("mainline.0", (tc.VAR_ROAD_ID, tc.VAR_LANEPOSITION))
            #   print(traci.vehicle.getSpeed(vehID))
            #   if traci.inductionloop.getLastStepVehicleNumber("0") > 0:
            #       traci.trafficlight.setRedYellowGreenState("0", "GrGr")
        step += 1

        #sleep(0.001)

 
# create handler for each connection
 
async def handler(websocket, path):
 
    #recvd = await websocket.recv()
    
    #reply = f"Data recieved as:  {data}!"
    async for msg in websocket:
        print(msg)
        reply = globals.data
        print("reply: " + reply + "\n")
        await websocket.send(reply)

x = threading.Thread(target=thread_function, args=(1,))
x.start()
 
start_server = websockets.serve(handler, "localhost", 8000)

asyncio.get_event_loop().run_until_complete(start_server)
 
asyncio.get_event_loop().run_forever()



 
 
 
