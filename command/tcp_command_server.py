# coding=UTF-8
import socket
import threading
import sys
import os

HOST = '172.16.0.15'
PORT = 9881

client_list = []

flag = 1

def manager_thread():
    global flag
    while True:
    	if flag == 0:
            command_init = raw_input('Please type "yes" to initial the system.').split()
            if len(command_init) == 1 and command_init[0] == 'yes':
                print('System initialized, vrpn server started.')
                os.system("roslaunch vrpn_keyboard_control rl_control.launch &")
                flag = 1
            else:
                print('Waiting for system initializing, please retry.')
        else:
            if client_list == []:
                continue
            client_address = [sock[1][0] for sock in client_list]
            client_dict = {index: ip for index, ip in zip(range(1, len(client_address)+1), client_address)}
            print('Existing agents: ' + str(client_dict))
            sys.stdout.flush()
            command_input = raw_input('Command:').split()
            if len(command_input) == 1:
                if command_input == 'using_keyboard':
                    rospy.set_param('using_keyboard', True)
                    print('Cars are controlling by the keyboard.')
                elif command_input == 'using_alg':
                    rospy.set_param('using_keyboard', False)
                    print('Cars are controlling by the RL algorithm.')
                elif command_input == 'kill_ros':
                    os.system("ps aux|grep python|grep -v grep|grep -v tcp_command|cut -c 9-15|xargs kill -9")
                    print('Ros has been killed.')
                    flag = 0
                else:
                    print('Unrecognized command.')
            elif len(command_input) == 2:
                client_index, cmd_send = command_input
                print('Client index: ' + str(client_index) + ', command: ' + str(cmd_send))
                if client_index == 'all':
                    for sock in client_list:
                        sock[0].send(cmd_send)
                        recvData = sock[0].recv(1024).decode('utf-8')
                        print("Command execute result:", recvData)
                elif int(client_index) not in range(1, len(client_address)+1):
                    print('Client not exist')
                else:
                    client_sock = client_list[int(client_index)-1][0]
                    client_sock.send(cmd_send)
                    recvData = client_sock.recv(1024).decode('utf-8')
                    print("Command execute result:", recvData)
            else:
                print('Unrecognized command.')

        
        # print('Existing agents ip: ' + str(client_address))
        # client_ip, cmd_send = raw_input('client ip & command:').split()
        # print('client ip: ' + str(client_ip) + ', command: ' + str(cmd_send))
        # if client_ip == 'all':
        #     for sock in client_list:
        #         sock[0].send(cmd_send)
        #         recvData = sock[0].recv(1024).decode('utf-8')
        #         print("Command execute result:", recvData)
        # elif client_ip not in client_address:
        #     print('client not exist')
        # else:
        #     client_index = client_address.index(client_ip)
        #     client_sock = client_list[client_index][0]
        #     client_sock.send(cmd_send)
        #     recvData = client_sock.recv(1024).decode('utf-8')
        #     print("Command execute result:", recvData)


def tcp_command(clientSocket, address):
    while True:
        cmd_send = raw_input('client address: ' + address[0] + ', command:')
        clientSocket.send(cmd_send)
        recvData = clientSocket.recv(1024).decode('utf-8')
        print("Command execute result:", recvData)

        

if __name__ == '__main__':
    # os.system("roslaunch vrpn_client_ros vrpn_multi.launch &")
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((HOST, PORT))
    serverSocket.listen(10)
    print("server is listening %d......." %(PORT))
    t = threading.Thread(target=manager_thread)
    t.start()
    while True:
        clientSocket, address = serverSocket.accept()
        # print(address)
        client_list.append([clientSocket, address])
        # t = threading.Thread(target=tcp_command, args=(clientSocket, address))
        # t.start()