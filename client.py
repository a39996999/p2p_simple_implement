import socket  
import json
import os
import random
from threading import Thread

server = None
client_name = None
client_port = None
ADDRESS = ('127.0.0.1', 8888) 
conn_dict = {}
conn_num = 0

def init():
    global server
    global client_port

    client_port = random.randint(15000, 20000)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    server.bind(('127.0.0.1', client_port))
    server.listen(5)

    print("server start，wait for client connecting...")

# 接收client連線
def accept_client():

    while True:
        client, info = server.accept() #等待連線

        thread = Thread(target=message_handle, args=(client, info))
        thread.setDaemon(True)
        thread.start()
        global conn_num
        conn_num = conn_num+1 
        print('目前連接數量:', conn_num)

 # 處理訊息
def message_handle(client, info):
    client.sendall("connect server successfully!".encode(encoding='utf8'))

    while True:
        try:
            bytes = client.recv(1024)
            msg = bytes.decode(encoding='utf8')
            jd = json.loads(msg)
            cmd = jd['command']
            client_name = jd['client_name']
            client_port = jd['client_port']

            if 'connect' == cmd:
                conn_dict[client_name] = client
                print('on client connect: ' + client_name, info)

            elif 'send_data' == cmd:
                print('recv client msg: ' + client_name, jd['data'])

        except Exception as e:
            print(e)
            remove_client(client_name)
            break

def remove_client(client_name):
    client = conn_dict[client_name]
    if None != client:
        client.close()
        conn_dict.pop(client_name)
        global conn_num
        conn_num = conn_num-1
        print("client offline: " + client_name)
        print('目前連接數量:', conn_num)

###################################################################################################

def send_data(client, cmd, **data):
    global client_name
    jd = {}
    jd['command'] = cmd
    jd['client_name'] = client_name
    jd['data'] = data
    jd['client_port'] = client_port

    jsonstr = json.dumps(jd)
    print('send: ' + jsonstr)
    client.sendall(jsonstr.encode('utf8'))

def new_message_recv(client):
    while True:
        try:
            bytes = client.recv(1024)
            msg = bytes.decode(encoding='utf8')
            msg = json.loads(msg)
            host_ip = msg['host_ip']
            host_port = msg['host_port']
            host_name = msg['host_name']
            print()
            print('新成員加入：', host_ip, host_port, host_name)
            
            try:
                client.close()
                client = socket.socket()
                client.connect((host_ip, host_port))
                print(client.recv(1024).decode(encoding='utf8'))
                
                send_data(client, 'connect')
                
                a='Hello!! '+host_name
                send_data(client, 'send_data', data=a)
                
            except Exception as e:
                print(e)
                break
            '''
            client = socket.socket() 
            client.connect((host_ip, host_port))
            print(client.recv(1024).decode(encoding='utf8'))
            send_data(client, 'connect')
            '''

        except Exception as e:
            break


if '__main__' == __name__:
    init()

    thread = Thread(target=accept_client)
    thread.setDaemon(True)
    thread.start()

    client_name = input("輸入名字 :")
    client = socket.socket() 
    client.connect(ADDRESS)
    print(client.recv(1024).decode(encoding='utf8'))
    send_data(client, 'connect')
    
    thread = Thread(target=new_message_recv, args = (client,))
    thread.setDaemon(True)
    thread.start()

    while True:
        a=input("輸入傳送訊息:")
        send_data(client, 'send_data', data=a)
