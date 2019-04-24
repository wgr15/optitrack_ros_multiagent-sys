#!/usr/bin/env python

import rospy
from car_serial.msg import run
import serial

def callback(run):
    data_show = '{:08b}'.format(run.data)
    rospy.loginfo("Writing to serial port %s", data_show)
    ser.write(chr(run.data))


if __name__ == '__main__':
    rospy.init_node('car_serial_listener', anonymous=True)
    ser = serial.Serial("/dev/ttyTHS2", 115200, timeout = 1)
    if ser.isOpen():        
        rospy.loginfo("Serial Port initialized")
    rospy.Subscriber('car_serial', run, callback)
    rospy.spin()
    # ser.close()