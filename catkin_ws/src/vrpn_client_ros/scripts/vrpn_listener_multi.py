#!/usr/bin/env python

import rospy
import math
from geometry_msgs.msg import PoseStamped
from vrpn_client_ros.algorithm.Pytorch_DRL.HNRN import test_real_car
from vrpn_client_ros.algorithm.Pytorch_DRL.HNRN import utils
import socket
import struct
import PyKDL as kdl
import threading
import argparse

agent_num = 2

car_poses = []

# car_poses = [(0.0, 0.0, 0.0) for i in range(agent_num)]

car_target = []

# car_target = [(3.84, 1.17), (1.57, 3.98)]

LASER_RANGE = 3.5

ROBOT_LENGTH = 0.25

# tcp_ip = '172.16.0.15'

# tcp_port = [8888, 9999]

def send_msg(sock, msg):
    # Prefix each message with a 4-byte id and length (network byte order)
    msg = struct.pack('>I', len(msg)) + msg
    # print(len(msg))
    # print(struct.unpack('>I',struct.pack('>I', len(msg)))[0])
    # print(msg)
    sock.sendall(msg)

def callback(msg, car_num):
    global car_poses
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

    if(yaw > math.pi):
        yaw = yaw - 2 * math.pi
    elif(yaw <= -math.pi):
        yaw = yaw + 2 * math.pi

    car_poses[car_num] = (x, y, yaw)

    # rospy.loginfo("RigidBody0%d[coordinate]: Header seq = %d; Position x = %f, y = %f, z = %f; Orientation roll = %f, pitch = %f, yaw = %f.", car_num+1, seq, x, y, z, roll, pitch, yaw)

def tcp_send(ip, port, car_num):
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((ip, port))
    tcp_socket.listen(10)
    print('waiting for connection...')
    sock, addr = tcp_socket.accept()
    print('TCP connected!')
    print(addr)
    while True:
        car_state = []
        for i in range(agent_num):
            temp_state = test_real_car.state_struct([float("inf") for _ in range(360)], car_poses[i][0], car_poses[i][1], car_poses[i][2], car_target[i][0], car_target[i][1])
            car_state.append(temp_state)
        car_state = utils.generate_laser_from_pos(car_state, LASER_RANGE, ROBOT_LENGTH)    
        action = test_real_car.inference(car_state[car_num])
        if utils.distance(car_poses[car_num][0], car_poses[car_num][1], car_target[car_num][0], car_target[car_num][1]) < 0.5:
            action = (0.0, 0.0)
        rospy.loginfo("RigidBody0%d[RL algorithm]: Action linear = %f, angular = %f.", car_num+1, action[0], action[1])
        data = ""
        linear_x = str(action[0])
        linear_y = str(0.0)
        linear_z = str(0.0)
        angular_x = str(0.0)
        angular_y = str(0.0)
        angular_z = str(action[1])
        data += linear_x + "," + linear_y + "," + linear_z + "," + angular_x + "," + angular_y + "," + angular_z
        send_msg(sock, data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--node_name", help="Name of node", type=str)
    parser.add_argument('args', nargs=argparse.REMAINDER)
    config = parser.parse_args()
    rospy.init_node(config.node_name, anonymous=True)
    tcp_ip = rospy.get_param('~tcp_ip')
    tcp_port = rospy.get_param('~tcp_port')
    agent_num = rospy.get_param('~agent_num')
    car_poses = [(0.0, 0.0, 0.0) for i in range(agent_num)]
    car_target = rospy.get_param('~car_target')
    LASER_RANGE = rospy.get_param('~LASER_RANGE')
    ROBOT_LENGTH = rospy.get_param('~ROBOT_LENGTH')
    for i in range(agent_num):
        rospy.Subscriber('/vrpn_client_node/RigidBody0' + str(i+1) + '/pose', PoseStamped, callback, i)
    for i in range(agent_num):
        t = threading.Thread(target=tcp_send, args=(tcp_ip, tcp_port[i], i))
        t.start()
    rospy.spin()
