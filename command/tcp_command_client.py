# coding=UTF-8
import socket
import os
import rospy
import time
import datetime

HOST = '172.16.0.15'
PORT = 9881

if __name__ == '__main__':
    fid = open('/home/nvidia/python_command.log','w+')
    fid.write('hello\n')
    fid.write( datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n' )
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # clientSocket.connect((HOST, PORT))
    connect_flag = 1
    while connect_flag != 0:
        connect_flag = clientSocket.connect_ex((HOST, PORT))
        # fid.write(str(connect_flag) + '\n')
        time.sleep(1)
    fid.write('connect success\n')
    fid.flush()
    try:
        while True:
            fid.flush()
            cmd = clientSocket.recv(1024).decode('utf-8')
            if cmd == 'run':
                # os.system("roslaunch vrpn_client_ros vrpn_multi.launch &")
                os.system("roslaunch car_serial_v2 car_serial_v2.launch &")
                resData = 'roslaunch success'.encode('utf-8')
            elif cmd == 'kill':
                os.system("ps aux|grep python|grep -v grep|grep -v tcp_command|cut -c 9-15|xargs kill -9")
                resData = 'ros kill'.encode('utf-8')
            elif cmd == 'open':
                rospy.set_param('serial_switch', True)
                resData = 'serial open'.encode('utf-8')
            elif cmd == 'close':
                rospy.set_param('serial_switch', False)
                resData = 'serial close'.encode('utf-8')
            elif cmd == 'byserver':
                rospy.set_param('control_by_server', True)
                resData = 'car is controlling by server'.encode('utf-8')
            elif cmd == 'bycar':
                rospy.set_param('control_by_server', False)
                resData = 'car is controlling by itself'.encode('utf-8')
            elif cmd == 'shutdown':
                os.system("ps aux|grep python|grep -v grep|cut -c 9-15|xargs kill -9")
                resData = 'python kill'.encode('utf-8')
            elif cmd == 'reboot':
                os.system("sudo reboot")
            elif cmd == '':
                continue
            else:         
                resData = 'unrecognized command'.encode('utf-8')
            clientSocket.send(resData)
    except:
        clientSocket.close()

