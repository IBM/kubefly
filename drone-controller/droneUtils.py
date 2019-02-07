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

import time
from cflib.crazyflie.mem import MemoryElement

# code for waiting on position nodes to calibrate
def wait_for_position_estimator(scf):
    print('Waiting for estimator to find position...')

    log_config = LogConfig(name='Kalman Variance', period_in_ms=500)
    log_config.add_variable('kalman.varPX', 'float')
    log_config.add_variable('kalman.varPY', 'float')
    log_config.add_variable('kalman.varPZ', 'float')

    var_y_history = [1000] * 10
    var_x_history = [1000] * 10
    var_z_history = [1000] * 10

    threshold = 0.001

    with SyncLogger(scf, log_config) as logger:
        for log_entry in logger:
            data = log_entry[1]

            var_x_history.append(data['kalman.varPX'])
            var_x_history.pop(0)
            var_y_history.append(data['kalman.varPY'])
            var_y_history.pop(0)
            var_z_history.append(data['kalman.varPZ'])
            var_z_history.pop(0)

            min_x = min(var_x_history)
            max_x = max(var_x_history)
            min_y = min(var_y_history)
            max_y = max(var_y_history)
            min_z = min(var_z_history)
            max_z = max(var_z_history)

            if (max_x - min_x) < threshold and (
                    max_y - min_y) < threshold and (
                    max_z - min_z) < threshold:
                break

# download params
def wait_for_param_download(scf):
    while not scf.cf.param.is_updated:
        time.sleep(1.0)
    print('Parameters downloaded for', scf.cf.link_uri)
    time.sleep(0.2)


# provided code for updating the estimation of position
def reset_estimator(scf):
    cf = scf.cf
    cf.param.set_value('kalman.resetEstimation', '1')
    time.sleep(0.1)
    cf.param.set_value('kalman.resetEstimation', '0')

    wait_for_position_estimator(cf)

# callback for LED write
def _led_write_done(mem, addr):
    print("LED write done callback")

# set color of LED board
def set_color(cf, color):
    try:
        # get the memory elements of type LED
        mems = cf.mem.get_mems(MemoryElement.TYPE_DRIVER_LED)
        mem = None
        # confirm length > 0 before indexing
        if len(mems) > 0:
            mem = mems[0]
        # loop through LEDs, setting each one
        for led in mem.leds:
            led.set(r=color[0], g=color[1], b=color[2])
        mem.write_data(_led_write_done)
    except Exception as e:
        print("exception setting color")
        print(e)

# fly the drone in a circle - TODO: needs increased landing_time
def circle(cf, position):
    landing_time = 3.0
    sleep_time = 0.1
    steps = int(landing_time / sleep_time)
    angle = 360/steps
    radius = 0.25
    for i in range(steps):
        x = (radius * cos(angle * i)) + position[0]
        y = (radius * sin(angle * i)) + position[1]
        cf.commander.send_position_setpoint(x, y, position[2], 0)
        time.sleep(sleep_time)

# take off
def take_off(cf, position):
    try:
        take_off_time = 3.0
        sleep_time = 0.1
        steps = int(take_off_time / sleep_time)
        vz = position[2] / take_off_time

        # for each step in the range of steps, go upwards
        for i in range(steps):
            print(i)
            cf.commander.send_velocity_world_setpoint(0, 0, vz, 0)
            time.sleep(sleep_time)

        # immediately go to first position
        cf.commander.send_position_setpoint(
            position[0], position[1], position[2], 0)
    except Exception as e:
        print("exception taking off")
        print(e)


# function to first go to latest position (x,y), and then land a drone
def land(cf, position):
    try:
        landing_time = 1.5
        move_time = 1.5
        sleep_time = 0.1
        move_steps = int(move_time / sleep_time)
        land_steps = int(landing_time / sleep_time)
        vzland = -1.0/landing_time

        # take 1s to move toward the latest point
        for i in range(move_steps):
            cf.commander.send_position_setpoint(position[0], position[1], 1.0, 0)
            time.sleep(sleep_time)

        # take 2s to land
        for j in range(land_steps):
            cf.commander.send_velocity_world_setpoint(0, 0, vzland, 0)
            time.sleep(sleep_time)

        # turn the drone off
        cf.commander.send_stop_setpoint()

        # Make sure that the last packet leaves before the link is closed
        # since the message queue is not flushed before closing
        time.sleep(0.1)
    except Exception as e:
        print("exception landing")
        print(e)
