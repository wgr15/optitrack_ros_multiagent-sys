#!/usr/bin/env python

import rospy
from car_serial_onserver.msg import pose
from car_serial_onserver.msg import run

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

def callback(pose, pub):
    # rospy.loginfo("car_pose_linear: %f, car_pose_angular: %f.", pose.linear, pose.angular)
    control_8bits = run()
    control_8bits.data = from_model_to_8bits([float(pose.linear), float(pose.angular)])
    if not rospy.is_shutdown():
        pub.publish(control_8bits)
        rospy.loginfo("Serial_msg: %d", control_8bits.data)

if __name__ == '__main__':
    try:
        rospy.init_node('pose_to_control', anonymous = True)
        pub = rospy.Publisher('serial_control', run, queue_size = 10)
        rospy.Subscriber('car_pose', pose, callback, pub)
        rospy.spin()
    except rospy.ROSInterruptException:
        pass


