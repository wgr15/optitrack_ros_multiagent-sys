#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist
from vrpn_keyboard_control.msg import vels

agent_num = 4

seq = 0

def callback(Twist, pub):
    # rospy.loginfo("Listener: Twist linear x = %f, y = %f, z = %f; angular x = %f, y = %f, z = %f", Twist.linear.x, Twist.linear.y,
        # Twist.linear.z, Twist.angular.x, Twist.angular.y, Twist.angular.z)
    global seq
    linear_x = Twist.linear.x
    linear_y = Twist.linear.y
    linear_z = Twist.linear.z
    angular_x = Twist.angular.x
    angular_y = Twist.angular.y
    angular_z = Twist.angular.z

    using_keyboard = rospy.get_param('using_keyboard')

    if using_keyboard == True:

        vels_msg = vels()
        vels_msg.seq = seq
        vels_msg.vel_linear = [linear_x for i in range(agent_num)]
        vels_msg.vel_angular = [angular_z for i in range(agent_num)]

        pub.publish(vels_msg)
        # rospy.loginfo("car_vels: seq = %d, vel_linear = %s, vel_angula = %s.", vels_msg.seq, str(vels_msg.vel_linear), str(vels_msg.vel_angular))
        seq += 1

if __name__ == '__main__':
    rospy.init_node('keyboard_control_listener', anonymous=True)
    agent_num = rospy.get_param('agent_num')
    using_keyboard = rospy.get_param('using_keyboard')
    vel_linear = [0.0 for i in range(agent_num)]
    vel_angular = [0.0 for i in range(agent_num)]
    pub = rospy.Publisher('car_vels', vels, queue_size = 10)
    rospy.Subscriber('keyboard_command', Twist, callback, pub)
    rospy.spin()
