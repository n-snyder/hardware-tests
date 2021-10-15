#!/usr/bin/env python3
# Arm, takeoff, hover, land.


import dataclasses
from threading import Condition
import rospy

from dr_hardware_tests import Drone, FlightMode, SensorSynchronizer
from dr_hardware_tests import is_data_available, is_armed, make_func_is_alt_reached, is_loiter_mode
from dr_hardware_tests import is_disarmed, is_on_ground
from dr_hardware_tests import start_RC_failsafe_watchdog, sleep


def log(msg):
    rospy.loginfo(f"hover test: {msg}")


def main():
    drone = Drone()
    drone.start()
    sensors = SensorSynchronizer()
    sensors.start()

    log("waiting for sensor data to come online")
    sensors.await_condition(is_data_available, 30)

    log("sending arm command")
    drone.arm()

    log("waiting for drone to arm")
    sensors.await_condition(is_armed, 30)

    log("setting takeoff altitude to 7.0 meters")
    drone.set_param('MIS_TAKEOFF_ALT', real_value=7.0)

    log("sending takeoff command")
    drone.set_mode(FlightMode.TAKEOFF)
    is_takeoff_alt_reached = make_func_is_alt_reached(7.0)
    sensors.await_condition(is_takeoff_alt_reached, 30)

    log("hover in loiter mode")
    drone.set_mode(FlightMode.LOITER)
    sensors.await_condition(is_loiter_mode, 5)

    log("hover for 30 seconds")
    sleep(30)

    log("send land command")
    drone.set_mode(FlightMode.LAND)

    log("waiting to reach the ground")
    sensors.await_condition(is_on_ground)

    log("sending disarm command")
    drone.disarm()
    log("waiting for drone to disarm")
    sensors.await_condition(is_disarmed, 30)

    log("SUCCESS")


if __name__ == "__main__":
    rospy.init_node("test_hover")
    main()
    rospy.signal_shutdown("finished")
