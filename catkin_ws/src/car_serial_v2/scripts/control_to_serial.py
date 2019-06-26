#!/usr/bin/env python

import rospy
from car_serial_v2.msg import run
import serial

def callback(run):
    data_show = '{:08b}'.format(run.data)
    seq = run.seq
    # if rospy.has_param('serial_switch'):
    #     print('serial_switch_yes')
    serial_switch = rospy.get_param('serial_switch')
    if serial_switch == False:
        if ser.isOpen():
            ser.write(chr(0))
            ser.close()
        # print('serial_close')
        rospy.loginfo("Serial is closed.")
    else:
        if not ser.isOpen():
            ser.open()
        # print('serial_open')
    if ser.isOpen():
        rospy.loginfo("Seq: %d, Writing to serial port %s", seq, data_show)
        ser.write(chr(run.data))


if __name__ == '__main__':
    try:
        rospy.init_node('control_to_serial', anonymous=True)
        ser = serial.Serial("/dev/ttyTHS2", 115200, timeout = 1)
        if ser.isOpen():
            rospy.loginfo("Serial Port initialized")
        rospy.Subscriber('serial_control', run, callback)
        rospy.spin()
        # ser.close()
    except rospy.ROSInterruptException:
        pass