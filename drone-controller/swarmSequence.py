# -*- coding: utf-8 -*-
#  Based on swarmSequence.py from Bitcraze crazyflie-lib-python library
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  Please see LICENSE.md for license file

"""
Version of the AutonomousSequence.py example connecting to 10 Crazyflies.
The Crazyflies go straight up, hover a while and land but the code is fairly
generic and each Crazyflie has its own sequence of setpoints that it files
to.

The layout of the positions (windowed formation):

y4


          2     3

y0    0      1
  x0                  x4

"""


import time
import socket
import json
import requests
import droneUtils

import cflib.crtp
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.swarm import CachedCfFactory
from cflib.crazyflie.swarm import Swarm
from cflib.crazyflie.syncLogger import SyncLogger
from cflib.positioning.motion_commander import MotionCommander
from cflib.crazyflie.mem import MemoryElement

from math import cos, sin

# Change uris and sequences according to your setup
URI0 = 'radio://1/120/2M/E7E7E7E700'
URI1 = 'radio://1/120/2M/E7E7E7E701'
URI2 = 'radio://0/80/2M/E7E7E7E702'
URI3 = 'radio://0/80/2M/E7E7E7E703'

# data = '[ { "droneId": 0,"podName": "details-v1-6865b9b99d-8tjxj","location": { "x": 0.825, "y": 0.6666666666666666, "z": 0 },"color": { "r": 189, "g": 110, "b": 205 } },{ "droneId": 1,"podName": "name","location": { "x": 1.65, "y": 0.6666666666666666, "z": 0 },"color": { "r": 31, "g": 114, "b": 12 } },{ "droneId": 2,"podName": "details-v1-6865b9b99d-8tjxj2","location": { "x": -2.4749999999999996, "y": 0.6666666666666666, "z": 0 },"color": { "r": 0, "g": 0, "b": 254 } },{ "droneId": 3,"podName": null,"location": { "x": 1.0999999999999999, "y": 1.3333333333333333, "z": 0 },"color": {"r": 199, "g": 93, "b": 48 } }]'
# data = '[{"droneId":0,"podName":"details-v1-6865b9b99d-8tjxj","location":{"x":1.4,"y":0.6,"z":0.4}},{"droneId":1,"podName":"productpage-v1-f8c8fb8-p5tsm","location":{"x":1.4,"y":1.2,"z":0.6}},{"droneId":2,"podName":"ratings-v1-77f657f55d-thrxb","location":{"x":0.6,"y":1.2,"z":0.4}},{"droneId":3,"podName":"reviews-v1-6b7f6db5c5-xfrvn","location":{"x":3,"y":1,"z":1}},{"droneId":4,"podName":"reviews-v2-7ff5966b99-q5lfz","location":{"x":4,"y":1,"z":1}},{"droneId":5,"podName":"reviews-v3-5df889bcff-qkb76","location":{"x":5,"y":1,"z":1}},{"droneId":6,"podName":null,"location":{"x":6,"y":1,"z":0}},{"droneId":7,"podName":null,"location":{"x":7,"y":1,"z":0}},{"droneId":8,"podName":null,"location":{"x":8,"y":1,"z":0}},{"droneId":9,"podName":null,"location":{"x":9,"y":1,"z":0}}]'
# json_data = json.loads(data)

#    x   y   z  status r, g, b
# TODO: improve data structure
drone_data = {
    URI0: [[0, 0, 0, 0, 0, 0, 0]],
    URI1: [[0, 0, 0, 0, 0, 0, 0]],
    URI2: [[0, 0, 0, 0, 0, 0, 0]],
    URI3: [[0, 0, 0, 0, 0, 0, 0]],
}

min_x = 0.0
min_y = 0.0
max_x = 3.33
max_y = 2.0

drone_URIs = [URI0, URI1, URI2, URI3]

uris = {
    URI0,
    URI1,
    URI2,
    URI3
}

def log_position(scf):
    lg_pos = LogConfig(name='LoPoTab2', period_in_ms=10)
    lg_pos.add_variable('kalman.stateX', 'float')
    lg_pos.add_variable('kalman.stateY', 'float')
    try:
        with SyncLogger(scf, lg_pos) as logger:
            first = next(logger)
            timestamp = first[0]
            data = first[1]
            print('[%d]: %s' % (timestamp, data))
            current_x = data['kalman.stateX']
            current_y = data['kalman.stateY']
            # check if drone out of bounds
            # make rest call to node for out of bound drone
            if (current_x < min_x or current_x > max_x or current_y < min_y or current_y > max_y):
                droneId = drone_URIs.index(scf.cf.link_uri)
                scf.cf.commander.send_stop_setpoint()
                getDeleteDrone(droneId)
                time.sleep(0.1)
    except Exception as e:
        print("log position exception")
        print(e)

def set_position(scf, data):
    # set crazyflie
    cf = scf.cf

    #set ring.effect to 13 for light settings
    try:
        cf.param.set_value("ring.effect", "13")
    except Exception as e:
        print("ring connection exception")
        print(cf.link_uri)
        print(e)

    # status of 0 = landed, status of 1 = needs to take off, status of 2 = flying
    # status of -1 = needs to land
    if (data[3] == -1):  # drone needs to land
        drone_data[cf.link_uri][0][3] = 0  # status is landed
        droneUtils.set_color(cf, data[4:7])  # setcolor
        droneUtils.land(cf, data)  # land drone
        droneUtils.set_color(cf, [0, 0, 0])
    elif (data[3] == 1):  # drone needs to take off
        droneUtils.take_off(cf, data)  # take off drone
        droneUtils.set_color(cf, data[4:7])  # setcolor
    elif (data[3] == 2):  # data[3] == 2, drone already flying
        # comment back in to include logging code
        # log_position(scf)
        landing_time = 3.0
        sleep_time = 0.5
        steps = int(landing_time / sleep_time)
        droneUtils.set_color(cf, data[4:7])  # set color
        try:
            for i in range(steps):
                # keep sending the same point for 3 seconds while other threads complete
                cf.commander.send_position_setpoint(data[0], data[1], data[2], 0)
                time.sleep(sleep_time)
        except Exception as e:
            print("setting position failed")
            print(e)

# call api for drone delete
def getDeleteDrone(droneId):
    url = 'http://localhost:3000/dead-drone/{}'.format(str(droneId))
    requests.request("GET", url, data="", headers={})
    # TODO : error handling. return empty array

# call api for drone data
def getDroneData():
    url = "http://localhost:3000"
    jsonData = ''
    try:
        response = requests.request("GET", url, data="", headers={})
        jsonData = json.loads(response.text)
    except Exception as reqErr:
        print("request error, using default data")
        data = '[ { "droneId": 0,"podName": null,"location": { "x": 0.825, "y": 0.6666666666666666, "z": 0 },"color": { "r": 189, "g": 110, "b": 205 } },{ "droneId": 1,"podName": null,"location": { "x": 1.65, "y": 0.6666666666666666, "z": 0 },"color": { "r": 31, "g": 114, "b": 12 } },{ "droneId": 2,"podName": null,"location": { "x": -2.4749999999999996, "y": 0.6666666666666666, "z": 0 },"color": { "r": 0, "g": 0, "b": 254 } },{ "droneId": 3,"podName": null,"location": { "x": 1.0999999999999999, "y": 1.3333333333333333, "z": 0 },"color": {"r": 199, "g": 93, "b": 48 } }]'
        jsonData = json.loads(data)
    # TODO : error handling. return empty array
    return jsonData


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    cflib.crtp.init_drivers(enable_debug_driver=False)

    factory = CachedCfFactory(rw_cache='./cache')
    with Swarm(uris, factory=factory) as swarm:
        # If the copters are started in their correct positions this is
        # probably not needed. The Kalman filter will have time to converge
        # any way since it takes a while to start them all up and connect. We
        # keep the code here to illustrate how to do it.
        swarm.parallel(droneUtils.reset_estimator)

        # The current values of all parameters are downloaded as a part of the
        # connections sequence. Since we have 10 copters this is clogging up
        # communication and we have to wait for it to finish before we start
        # flying.
        print('Waiting for parameters to be downloaded...')
        swarm.parallel(droneUtils.wait_for_param_download)
        while True:
            # data = json_data
            data = getDroneData()
            for drone in data:
                droneId = drone['droneId']
                drone_URI = drone_URIs[droneId]
                status = drone_data[drone_URI][0][3]
                # TODO status should be an enum
                position = (
                    drone['location']['x'], drone['location']['y'], drone['location']['z'])
                color = (
                    drone['color']['r'], drone['color']['g'], drone['color']['b'])

                # set position and color in drone data structure
                drone_data[drone_URI][0][0] = position[0]
                drone_data[drone_URI][0][1] = position[1]
                drone_data[drone_URI][0][2] = position[2]
                drone_data[drone_URI][0][4] = color[0]
                drone_data[drone_URI][0][5] = color[1]
                drone_data[drone_URI][0][6] = color[2]

                # status of 0 = landed, status of 1 = needs to take off, status of 2 = flying
                # status of -1 = needs to land
                # if there is no pod, and drone is flying, then land it.
                if ((drone['podName'] == None) and (status > 0)):
                    # set status as "needs to land"
                    drone_data[drone_URI][0][3] = -1
                # drone has a pod, but is landed -- needs to takeoff
                elif ((drone['podName'] != None) and (status == 0)):
                    # status was 0, but pod is assigned
                    # set status as "needs to takeoff"
                    drone_data[drone_URI][0][3] = 1
                # drone has a pod, and is flying -- just send new point
                elif ((drone['podName'] != None) and (status == 1 or status == 2)):
                    # status was 1, and pod is assigned
                    # just set the new position for this drone.
                    drone_data[drone_URI][0][3] = 2
            swarm.parallel(set_position, args_dict=drone_data)
