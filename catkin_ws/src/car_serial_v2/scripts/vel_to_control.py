#!/usr/bin/env python

import rospy
from car_serial_v2.msg import vel
from car_serial_v2.msg import run

def from_model_to_8bits(action):
    # velocity
    vel = int(round(abs(action[0] * 7)))
    if vel is not 0:
        vel += int(action[0] < 0) << 3
    # angular
    angle = int(round(abs(action[1] * 7)))
    if angle is not 0:
        angle += int(action[1] < 0) << 3
    control_8bits = (angle << 4) + vel
    return control_8bits

def callback(vel, pub):
    # rospy.loginfo("car_vel: seq = %d, vel_linear = %f, vel_angular = %f.", vel.seq, vel.vel_linear, vel.vel_angular)
    control_8bits = run()
    control_8bits.data = from_model_to_8bits([vel.vel_linear, vel.vel_angular])
    control_8bits.seq = vel.seq
    if not rospy.is_shutdown():
        pub.publish(control_8bits)
        rospy.loginfo("Serial_msg: %d", control_8bits.data)

if __name__ == '__main__':
    try:
        rospy.init_node('vel_to_control', anonymous = True)
        pub = rospy.Publisher('serial_control', run, queue_size = 10)
        rospy.Subscriber('car_vel_board', vel, callback, pub)
        rospy.spin()
    except rospy.ROSInterruptException:
        pass


