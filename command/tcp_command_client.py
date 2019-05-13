# coding=UTF-8
import socket
import os
import rospy

HOST = '172.16.0.15'
PORT = 9881

if __name__ == '__main__':
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((HOST, PORT))
    while True:
        cmd = clientSocket.recv(1024).decode('utf-8')
        if cmd == 'run':
            # os.system("roslaunch vrpn_client_ros vrpn_multi.launch &")
            os.system("roslaunch car_serial car_serial.launch &")
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