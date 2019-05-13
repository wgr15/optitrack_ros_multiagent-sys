#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist
import socket
import struct

def send_msg(sock, msg):
    # Prefix each message with a 4-byte id and length (network byte order)
    msg = struct.pack('>I', len(msg)) + msg
    # print(len(msg))
    # print(struct.unpack('>I',struct.pack('>I', len(msg)))[0])
    # print(msg)
    sock.sendall(msg)


def callback(Twist, socket):
    # rospy.loginfo("Listener: Twist linear x = %f, y = %f, z = %f; angular x = %f, y = %f, z = %f", Twist.linear.x, Twist.linear.y,
    	# Twist.linear.z, Twist.angular.x, Twist.angular.y, Twist.angular.z)
    
    data = ""
    linear_x = str(Twist.linear.x)
    linear_y = str(Twist.linear.y)
    linear_z = str(Twist.linear.z)
    angular_x = str(Twist.angular.x)
    angular_y = str(Twist.angular.y)
    angular_z = str(Twist.angular.z)

    data += linear_x + "," + linear_y+ "," + linear_z + "," + angular_x + "," + angular_y+ "," + angular_z

    # print(data)
    send_msg(socket, data)

if __name__ == '__main__':
    rospy.init_node('robot_keyboard_listener', anonymous=True)
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind(('172.16.0.15', 8888))
    tcp_socket.listen(10)
    print('waiting for connection...')
    sock, addr = tcp_socket.accept()
    print('TCP connected!')
    print(addr)
    rospy.Subscriber('keyboard_robot', Twist, callback, sock)
    rospy.spin()
