#!/usr/bin/env python
#coding=UTF-8

import rospy
import math
from car_serial_v2.msg import poses_board
from car_serial_v2.msg import vel

from algorithm.Pytorch_DRL.HNRN import test_real_car
from algorithm.Pytorch_DRL.HNRN import utils
# from algorithm import test

agent_num = 4

LASER_RANGE = 3.5

ROBOT_LENGTH = 0.25


def callback(poses_board, pub):
    seq = poses_board.seq
    agent_num = poses_board.agent_num
    agent_index = poses_board.agent_index
    position_x = poses_board.position_x
    position_y = poses_board.position_y
    position_yaw = poses_board.position_yaw
    target_x = poses_board.target_x
    target_y = poses_board.target_y

    car_poses = zip(position_x, position_y, position_yaw)
    car_targets = zip(target_x, target_y)

    control_by_server = rospy.get_param('control_by_server')

    if control_by_server == False:

        car_vel = alg_inference(car_poses, car_targets, agent_index)
        # car_vel = test.alg_inference(car_poses, car_targets, agent_index, agent_num, LASER_RANGE, ROBOT_LENGTH)
    
        vel_msg = vel()
        vel_msg.seq = seq
        vel_msg.vel_linear = car_vel[0]
        vel_msg.vel_angular = car_vel[1]

        pub.publish(vel_msg)
        # rospy.loginfo("car_vel: seq = %d, vel_linear = %f, vel_angular = %f.", vel_msg.seq, vel_msg.vel_linear, vel_msg.vel_angular)
    

def alg_inference(car_poses, car_targets, car_index):
    car_state = []
    for i in range(agent_num):
        temp_state = test_real_car.state_struct([float("inf") for _ in range(360)], car_poses[i][0], car_poses[i][1], car_poses[i][2], car_targets[i][0], car_targets[i][1])
        car_state.append(temp_state)
    car_state = utils.generate_laser_from_pos(car_state, LASER_RANGE, ROBOT_LENGTH)    
    action = test_real_car.inference(car_state[car_index])
    # if car_index == 3:
    #     action[0] = action[0] * 0.8
    if abs(action[0]) < 1.0/14:
        action[0] = (1.0/14 + 0.001 if(action[0]>0) else -1.0/14 - 0.001)
    if utils.distance(car_poses[car_index][0], car_poses[car_index][1], car_targets[car_index][0], car_targets[car_index][1]) < 0.4:
        action = (0.0, 0.0)
        # rospy.loginfo("RigidBody0%d[RL algorithm]: Action linear = %f, angular = %f.", car_index+1, action[0], action[1])
    return action


if __name__ == '__main__':
    rospy.init_node('RL_onboard', anonymous=True)

    control_by_server = rospy.get_param('control_by_server')

    car_poses = [(0.0, 0.0, 0.0) for i in range(agent_num)]
    car_target = [(0.0, 0.0) for i in range(agent_num)]
    car_vel = [0.0, 0.0]

    LASER_RANGE = rospy.get_param('~LASER_RANGE')
    ROBOT_LENGTH = rospy.get_param('~ROBOT_LENGTH')

    pub = rospy.Publisher('car_vel_board', vel, queue_size = 10)
    rospy.Subscriber('car_poses_board', poses_board, callback, pub)
    rospy.spin()
