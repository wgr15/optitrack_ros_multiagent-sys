#!/usr/bin/env python

import rospy
import math
from geometry_msgs.msg import PoseStamped
from vrpn_client_ros.algorithm.Pytorch_DRL.HNRN import test_real_car
import socket
import struct
import PyKDL as kdl
import argparse
import sys


def send_msg(sock, msg):
    # Prefix each message with a 4-byte id and length (network byte order)
    msg = struct.pack('>I', len(msg)) + msg
    # print(len(msg))
    # print(struct.unpack('>I',struct.pack('>I', len(msg)))[0])
    # print(msg)
    sock.sendall(msg)

# def callback(msg, socket):
def callback(msg, (socket, config)):
    seq = msg.header.seq
    x = msg.pose.position.x
    y = msg.pose.position.y
    z = msg.pose.position.z
    qx = msg.pose.orientation.x
    qy = msg.pose.orientation.y
    qz = msg.pose.orientation.z
    qw = msg.pose.orientation.w

    rotation_matrix = kdl.Rotation.Quaternion(qx, qy, qz, qw)

    yaw, pitch, roll = rotation_matrix.GetEulerZYX()

    if(yaw <= -math.pi):
    	yaw = yaw + 2 * math.pi
    elif(yaw >= math.pi):
    	yaw = yaw - 2 * math.pi

    # yaw = yaw - math.pi/2

    # if(yaw > math.pi):
    #     yaw = yaw - 2 * math.pi
    # elif(yaw < -math.pi):
    #     yaw = yaw + 2 * math.pi

    # roll = math.atan2(2 * (qw * qx + qy * qz), 1 - 2 * (qx * qx + qy * qy))
    # pitch = math.asin(2 * (qw * qy - qz * qz))
    # yaw = math.atan2(2 * (qw * qz + qx * qy), 1 - 2 * (qz * qz + qy * qy))
    
    rospy.loginfo("%s[coordinate]: Header seq = %d; Position x = %f, y = %f, z = %f; Orientation roll = %f, pitch = %f, yaw = %f.", config.node_name, seq, x, y, z, roll, pitch, yaw)

    # rospy.loginfo("Vrpn_listener: Header seq = %d; Position x = %f, y = %f, z = %f; Orientation roll = %f, pitch = %f, yaw = %f.", seq, x, y, z, roll, pitch, yaw)

    temp_target = [3.84, 1.17]

    temp_state = test_real_car.state_struct([float("inf") for _ in range(360)], x, y, yaw, temp_target[0], temp_target[1])

    action = test_real_car.inference(temp_state)
    
    # rospy.loginfo("Vrpn_listener: Position x = %f, y = %f, z = %f; Orientation roll = %f, yaw = %f.", x, y, z, roll, yaw)

    rospy.loginfo("%s[RL algorithm]: Action linear = %f, angular = %f.",config.node_name, action[0], action[1])

    # rospy.loginfo("RL algorithm: Action linear = %f, angular = %f.", action[0], action[1])

    data = ""
    linear_x = str(action[0])
    linear_y = str(0.0)
    linear_z = str(0.0)
    angular_x = str(0.0)
    angular_y = str(0.0)
    angular_z = str(action[1])

    data += linear_x + "," + linear_y+ "," + linear_z + "," + angular_x + "," + angular_y+ "," + angular_z

    # print(data)
    send_msg(socket, data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--node_name", help="Name of node", type=str)
    parser.add_argument('args', nargs=argparse.REMAINDER)
    config = parser.parse_args()
    rospy.init_node(config.node_name, anonymous=True)
    # rospy.init_node("vrpn_listener_01", anonymous=True)
    tcp_ip = rospy.get_param('~tcp_ip')
    tcp_port = rospy.get_param('~tcp_port')
    topic_name = rospy.get_param('~topic_name')
    rate = rospy.Rate(10)
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((tcp_ip, tcp_port))
    # tcp_socket.bind(('172.16.0.15', 8888))
    tcp_socket.listen(10)
    print('waiting for connection...')
    sock, addr = tcp_socket.accept()
    print('TCP connected!')
    print(addr)
    rospy.Subscriber(topic_name, PoseStamped, callback, (sock, config))
    # rospy.Subscriber('/vrpn_client_node/RigidBody01/pose', PoseStamped, callback, sock)
    rate.sleep()
    rospy.spin()