import socket 
from threading import Thread
import time
import json


ADDRESS = ('127.0.0.1', 8888) 
 
server = None  

conn_dict = {}
conn_num = 0

# 初始化Server
def init():

    global server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    server.bind(ADDRESS)
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

                if conn_num >= 2:
                    for conn_member in conn_dict:
                        if conn_dict[conn_member] == client:
                            continue
                        member = conn_dict[conn_member]
                        client_info = {}
                        client_info['host_ip'] = info[0]
                        client_info['host_port'] = client_port
                        client_info['host_name'] = client_name
                        jsonstr = json.dumps(client_info)
                        member.sendall(jsonstr.encode(encoding='utf8'))

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
        


if __name__ == '__main__':
    init()

    thread = Thread(target=accept_client)
    thread.setDaemon(True)
    thread.start()

    while True:
        time.sleep(0.1)
