#!/usr/bin/env python

import rospy
import math
from vrpn_keyboard_control.msg import poses
from vrpn_keyboard_control.msg import vels
from algorithm.Pytorch_DRL.HNRN import test_real_car
from algorithm.Pytorch_DRL.HNRN import utils

agent_num = 4

LASER_RANGE = 3.5

ROBOT_LENGTH = 0.25


def callback(poses, pub):
    seq = poses.seq
    position_x = poses.position_x
    position_y = poses.position_y
    position_yaw = poses.position_yaw
    target_x = poses.target_x
    target_y = poses.target_y

    car_poses = zip(position_x, position_y, position_yaw)
    car_targets = zip(target_x, target_y)

    using_keyboard = rospy.get_param('using_keyboard')

    if using_keyboard == False:
    	
        for i in range(agent_num):
            vel = alg_inference(car_poses, car_targets, i)
            vel_linear[i] = vel[0]
            vel_angular[i] = vel[1]
        
        vels_msg = vels()
        vels_msg.seq = seq
        vels_msg.vel_linear = vel_linear
        vels_msg.vel_angular = vel_angular

        pub.publish(vels_msg)
        # rospy.loginfo("car_vels: seq = %d, vel_linear = %s, vel_angular = %s.", vels_msg.seq, str(vels_msg.vel_linear), str(vels_msg.vel_angular))
    

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
    rospy.init_node('RL_onserver', anonymous=True)
    agent_num = rospy.get_param('agent_num')
    using_keyboard = rospy.get_param('using_keyboard')
    vel_linear = [0.0 for i in range(agent_num)]
    vel_angular = [0.0 for i in range(agent_num)]
    LASER_RANGE = rospy.get_param('~LASER_RANGE')
    ROBOT_LENGTH = rospy.get_param('~ROBOT_LENGTH')
    pub = rospy.Publisher('car_vels_server', vels, queue_size = 10)
    rospy.Subscriber('car_poses_server', poses, callback, pub)
    rospy.spin()
