#!/usr/bin/env python

import rospy
from car_serial.msg import run
import socket
import struct
import threading

linear_x = 0.0
linear_y = 0.0
linear_z = 0.0
angular_x = 0.0
angular_y = 0.0
angular_z = 0.0

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
        rospy.init_node('car_serial_talker', anonymous = True)
        pub = rospy.Publisher('car_serial', run, queue_size = 10)
        rate = rospy.Rate(100)
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.connect(('172.16.0.15', 8888))
        # tcp_socket.setblocking(0)
        t = threading.Thread(target=tcp_recv, args=(tcp_socket,))
        t.start()
        control_8bits = run()
        while not rospy.is_shutdown():
            print("Twist linear x = %s, y = %s, z = %s; angular x = %s, y = %s, z = %s" % (linear_x, linear_y, linear_z, angular_x, angular_y, angular_z))
            # [linear_x, angular_z] = [-0.8, 0.5]
            control_8bits.data = from_model_to_8bits([float(linear_x), float(angular_z)])
            rospy.loginfo("Serial_msg: %d", control_8bits.data)
            pub.publish(control_8bits)
            rate.sleep()

    except rospy.ROSInterruptException:
        pass


