#!/usr/bin/env python

import rospy
from car_serial.msg import run
import serial

def callback(run):
    data_show = '{:08b}'.format(run.data)
    # if rospy.has_param('serial_switch'):
        # print('serial_switch_yes')
    serial_switch = rospy.get_param('serial_switch')
    # if serial_switch == False:
    #     if ser.isOpen():
    #         ser.close()
    #     # print('serial_close')
    #     rospy.loginfo("Serial is closed.")
    # else:
    #     if not ser.isOpen():
    #         ser.open()
    #     # print('serial_open')
    # if ser.isOpen():
    #     rospy.loginfo("Writing to serial port %s", data_show)
    #     ser.write(chr(run.data))
    rospy.loginfo("Writing to serial port %s", data_show)


if __name__ == '__main__':
    rospy.init_node('car_serial_listener', anonymous=True)
    # ser = serial.Serial("/dev/ttyTHS2", 115200, timeout = 1)
    # if ser.isOpen():
        # rospy.loginfo("Serial Port initialized")
    # rospy.Subscriber('car_serial', run, callback, ser)
    rospy.Subscriber('car_serial', run, callback)
    rospy.spin()
    # ser.close()
