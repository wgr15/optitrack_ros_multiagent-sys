#!/usr/bin/env python

import rospy
from car_serial_onserver.msg import pose
import socket
import struct
import threading

linear_x = 0.0
linear_y = 0.0
linear_z = 0.0
angular_x = 0.0
angular_y = 0.0
angular_z = 0.0

#message proto
# length | data
def recv_msg(sock):
    try:
        # Read message length and unpack it into an integer
        raw_msglen = recvall(sock, 4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        # print(msglen)
        # Read the message data
        return recvall(sock, msglen)
    except Exception ,e:
        return None

def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = ''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    # print(data)
    return data

def tcp_recv(socket):
    while True:
        global linear_x, linear_y, linear_z, angular_x, angular_y, angular_z
        linear_x, linear_y, linear_z, angular_x, angular_y, angular_z = recv_msg(socket).split(',')
        # data = recv_msg(socket)
        # print(data)
        # print "xkf"

if __name__ == '__main__':
    try:
        rospy.init_node('tcp_to_pose', anonymous = True)
        pub = rospy.Publisher('car_pose', pose, queue_size = 10)
        rate = rospy.Rate(10)
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.connect(('172.16.0.15', 8888))
        # tcp_socket.setblocking(0)
        t = threading.Thread(target=tcp_recv, args=(tcp_socket,))
        t.start()
        car_pose = pose()
        while not rospy.is_shutdown():
            # print("Twist linear x = %s, y = %s, z = %s; angular x = %s, y = %s, z = %s" % (linear_x, linear_y, linear_z, angular_x, angular_y, angular_z))
            # [linear_x, angular_z] = [-0.8, 0.5]
            car_pose.x = [0.0, 0.0]
            car_pose.y = [0.0, 0.0]
            car_pose.linear = float(linear_x)
            car_pose.angular = float(angular_z)
            rospy.loginfo("car_pose_linear: %f, car_pose_angular: %f.",  car_pose.linear, car_pose.angular)
            pub.publish(car_pose)
            rate.sleep()

    except rospy.ROSInterruptException:
        pass


