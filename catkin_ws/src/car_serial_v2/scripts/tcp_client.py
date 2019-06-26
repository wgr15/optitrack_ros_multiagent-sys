#!/usr/bin/env python
#coding=UTF-8

import rospy
from car_serial_v2.msg import poses_board
from car_serial_v2.msg import vel
import socket
import struct
import threading
import json

dataBuffer = bytes()

headerSize = 8

agent_num = 4

agent_index = 0

tcp_ip = '172.16.0.15'

tcp_port = 8888

seq = 0


def dataHandle(body):
    global agent_num, agent_index, car_poses, car_targets, car_vel
    data = json.loads(body.decode())
    agent_num = data['agent_num']
    agent_index = data['agent_index']
    car_poses = data['car_poses']
    car_targets = data['car_targets']
    car_vel = data['car_vel']


def tcp_recv(socket):
    global seq, dataBuffer
    while True:
        data = socket.recv(1024)
        if data:
            # 把数据存入缓冲区，类似于push数据
            dataBuffer += data
            while True:
                if len(dataBuffer) < headerSize:
                    # print("数据包（%s Byte）小于消息头部长度，跳出小循环" % len(dataBuffer))
                    break                  
                # 读取包头
                # struct中:!代表Network order，2I代表2个unsigned int数据
                headPack = struct.unpack('!2I', dataBuffer[:headerSize])
                bodySize = headPack[1]
                seq = headPack[0]
                # 分包情况处理，跳出函数继续接收数据
                if len(dataBuffer) < headerSize+bodySize :
                    # print("数据包（%s Byte）不完整（总共%s Byte），跳出小循环" % (len(dataBuffer), headerSize+bodySize))
                    break
                # 读取消息正文的内容
                body = dataBuffer[headerSize:headerSize+bodySize]
                # 数据处理
                dataHandle(body)
                # 粘包情况的处理
                dataBuffer = dataBuffer[headerSize+bodySize:] # 获取下一个数据包，类似于把数据pop出


if __name__ == '__main__':
    try:
        rospy.init_node('tcp_client', anonymous = True)

        tcp_ip = rospy.get_param('~tcp_ip')
        tcp_port = rospy.get_param('~tcp_port')

        car_poses = [(0.0, 0.0, 0.0) for i in range(agent_num)]
        car_targets = [(0.0, 0.0) for i in range(agent_num)]
        car_vel = [0.0, 0.0]

        poses_pub = rospy.Publisher('car_poses_board', poses_board, queue_size = 10)
        vel_pub = rospy.Publisher('car_vel_board', vel, queue_size = 10)
        rate = rospy.Rate(10)

        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.connect((tcp_ip, tcp_port))
        # tcp_socket.setblocking(0)
        t = threading.Thread(target=tcp_recv, args=(tcp_socket,))
        t.start()

        pose_msg = poses_board()
        vel_msg = vel()
        while not rospy.is_shutdown():
            # print("Twist linear x = %s, y = %s, z = %s; angular x = %s, y = %s, z = %s" % (linear_x, linear_y, linear_z, angular_x, angular_y, angular_z))
            # [linear_x, angular_z] = [-0.8, 0.5]
            pose_msg.seq = seq
            pose_msg.agent_num = agent_num
            pose_msg.agent_index = agent_index
            pose_msg.position_x = [pose[0] for pose in car_poses]
            pose_msg.position_y = [pose[1] for pose in car_poses]
            pose_msg.position_yaw = [pose[2] for pose in car_poses]
            pose_msg.target_x = [target[0] for target in car_targets]
            pose_msg.target_y = [target[1] for target in car_targets]

            vel_msg.seq = seq
            vel_msg.vel_linear = car_vel[0]
            vel_msg.vel_angular = car_vel[1]

            # rospy.loginfo("car_poses: seq = %d, agent_num = %d, agent_index = %d, position_x = %s, position_y = %s, position_yaw = %s, target_x = %f, target_y = %f.", pose_msg.seq, 
                # pose_msg.agent_num, pose_msg.agent_index, str(pose_msg.position_x), str(pose_msg.position_y), str(pose_msg.position_yaw), pose_msg.target_x, pose_msg.target_y)
            # rospy.loginfo("car_vel: seq = %d, vel_linear = %f, vel_angular = %f.", vel_msg.seq, vel_msg.vel_linear, vel_msg.vel_angular)

            poses_pub.publish(pose_msg)

            control_by_server = rospy.get_param('control_by_server')
            if control_by_server == True:
                vel_pub.publish(vel_msg)

            rate.sleep()

    except rospy.ROSInterruptException:
        pass


