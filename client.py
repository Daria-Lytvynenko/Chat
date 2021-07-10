import threading
import socket
import json
import time

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432  # The port used by the server
login_state = 0


def listen(s):
    global login_state
    while True:
        try:
            inf = s.recv(1024).decode()
        except:
            break
        data = json.loads(inf)
        if 'txt' in data:
            print(data['txt'])
        if 'cmd' in data:
            if data['cmd'] == 'NICK_NOT_ALLOWED':
                login_state = 1
            if data['cmd'] == 'NICK_ALLOWED':
                login_state = 2



def send_to_server(cmd_name, *args, **kwargs):
    d = {'cmd': cmd_name, 'params': {'args': args, 'kwargs': kwargs}}
    s.sendall(json.dumps(d).encode())


def login():
    global login_state
    name = input("Input your name")
    send_to_server('set_nickname', name)
    while login_state != 2:
        while login_state == 0:
            time.sleep(0.1)
        if login_state == 1:
            name = input("Input your name")
            send_to_server('set_nickname', name)
            login_state = 0


if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        threading.Thread(target=listen, args=(s,)).start()
        login()
        user_input = (input("Input message"))
        while user_input != 'quit':
            send_to_server('send_all', user_input)
            user_input = (input("Input message"))
        send_to_server('quit')
