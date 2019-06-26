#!/usr/bin/env python

import rospy
import math
from geometry_msgs.msg import PoseStamped
from vrpn_keyboard_control.msg import poses
import PyKDL as kdl
import threading

agent_num = 4

def callback(msg, car_index):
    global rigidbody_poses
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

    rigidbody_poses[car_index] = (x, y, yaw)

    # rospy.loginfo("RigidBody0%d[coordinate]: Header seq = %d; Position x = %f, y = %f, z = %f; Orientation roll = %f, pitch = %f, yaw = %f.", car_index+1, seq, x, y, z, roll, pitch, yaw)

def ros_thread(agent_num):
    for i in range(agent_num):
        rospy.Subscriber('/vrpn_client_node/RigidBody0' + str(i+1) + '/pose', PoseStamped, callback, i)
    rospy.spin()

if __name__ == '__main__':
    rospy.init_node('vrpn_pose', anonymous=True)
    agent_num = rospy.get_param('agent_num')
    
    rigidbody_poses = [(0.0, 0.0, 0.0) for i in range(agent_num)]

    car_targets = [(0.0, 0.0) for i in range(agent_num)]

    car_targets = rospy.get_param('car_targets')

    t_ros = threading.Thread(target=ros_thread, args=(agent_num, ))
    t_ros.start()

    pub = rospy.Publisher('car_poses_server', poses, queue_size = 10)
    rate = rospy.Rate(50)
    pose_msg = poses()
    seq = 0
    while not rospy.is_shutdown():
        pose_msg.seq = seq
        pose_msg.position_x = [pose[0] for pose in rigidbody_poses]
        pose_msg.position_y = [pose[1] for pose in rigidbody_poses]
        pose_msg.position_yaw = [pose[2] for pose in rigidbody_poses]
        pose_msg.target_x = [target[0] for target in car_targets]
        pose_msg.target_y = [target[1] for target in car_targets]

        # print(pose_msg)
        # rospy.loginfo("car_poses: seq = %d, position_x = %s, position_y = %s, position_yaw = %s, target_x = %s, target_y = %s.", pose_msg.seq, str(pose_msg.position_x), 
            # str(pose_msg.position_y), str(pose_msg.position_yaw), str(pose_msg.target_x), str(pose_msg.target_y))
        pub.publish(pose_msg)
        seq += 1
        rate.sleep()
