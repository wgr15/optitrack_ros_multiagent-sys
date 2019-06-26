#!/usr/bin/env python

import rospy
from vrpn_keyboard_control.msg import poses
from vrpn_keyboard_control.msg import vels
import socket
import struct
import threading
import json
import time

agent_num = 4

agent_list = []

# car_ips = ['172.16.0.66', '172.16.0.176', '172.16.0.184', '172.16.0.98']

car_ips = ['172.16.0.15']

seq = 0

tcp_ip = '172.16.0.15'

tcp_port = 8888


def pose_callback(poses):
    global car_poses, car_targets
    position_x = poses.position_x
    position_y = poses.position_y
    position_yaw = poses.position_yaw
    target_x = poses.target_x
    target_y = poses.target_y

    car_poses = zip(position_x, position_y, position_yaw)
    car_targets = zip(target_x, target_y)

    # rospy.loginfo("RigidBody0%d[coordinate]: Header seq = %d; Position x = %f, y = %f, z = %f; Orientation roll = %f, pitch = %f, yaw = %f.", car_num+1, seq, x, y, z, roll, pitch, yaw)


def vel_callback(vels):
    global seq, car_vels
    seq = vels.seq
    vel_linear = vels.vel_linear
    vel_angular = vels.vel_angular

    car_vels = zip(vel_linear, vel_angular)


def tcp_thread():
    while True:
        if agent_list == []:
            continue
        for sock in agent_list:
            agent_ip = sock[1][0]
            if agent_ip not in car_ips:
                continue
            else:
                agent_index =  car_ips.index(agent_ip)
            body = dict(agent_num = agent_num, agent_index = agent_index, car_poses = car_poses, car_targets = car_targets, car_vel = list(car_vels[agent_index]))
            body = json.dumps(body)
            header = [seq, body.__len__()]
            headPack = struct.pack("!2I", *header)
            sendData = headPack + body.encode()
            sock[0].send(sendData)
            time.sleep(0.02)


def ros_thread():
    rospy.Subscriber('car_poses_server', poses, pose_callback)
    rospy.Subscriber('car_vels_server', vels, vel_callback)
    rospy.spin()


if __name__ == '__main__':
    rospy.init_node('tcp_server', anonymous=True)

    tcp_ip = rospy.get_param('~tcp_ip')
    tcp_port = rospy.get_param('~tcp_port')
    agent_num = rospy.get_param('agent_num')
    car_ips = rospy.get_param('car_ips')

    car_poses = [(0.0, 0.0, 0.0) for i in range(agent_num)]
    car_targets = [(0.0, 0.0) for i in range(agent_num)]
    car_vels = [(0.0, 0.0) for i in range(agent_num)]

    t_ros = threading.Thread(target=ros_thread)
    t_ros.start()
    
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((tcp_ip, tcp_port))
    tcp_socket.listen(10)
    print('waiting for connection...')

    t = threading.Thread(target=tcp_thread)
    t.start()

    while True:
        sock, addr = tcp_socket.accept()
        # print('TCP connected!')
        print(addr)
        agent_list.append([sock, addr])
