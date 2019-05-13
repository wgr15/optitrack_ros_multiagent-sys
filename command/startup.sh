#!/bin/bash
#
touch /tmp/start0
sleep 10
touch /tmp/start10
source /opt/ros/kinetic/setup.bash
source /home/nvidia/catkin_ws/devel/setup.bash
python /home/nvidia/tcp_command_client.py > /home/nvidia/test.log 2>&1
# python /home/nvidia/test.py > /home/nvidia/test0.log 2>&1
