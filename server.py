import socket
import threading
import json

lock = threading.Lock()
connections = {}
nick_n = {
    ('127.0.0.1', 3535): 'Nikodim',
    ('127.0.0.1', 0): 'server_info',
    ('127.0.0.1', 3536): 'Petr',
}


def user_quit(connection, client_address, *args, **kwargs):
    if client_address not in nick_n:
        return
    user_name = nick_n[client_address]
    nick_n.pop(client_address)
    connections.pop(client_address)
    send_all(connection, ('127.0.0.1', 0), f'{user_name} left chat')


def send_all(connection, client_address, text, *args, **kwargs):
    user_name = nick_n[client_address]
    message = f'{user_name} say: {text}'
    for k, v in connections.items():
        if client_address != k:
            send_to_user(v, message)


def set_nickname(connection, client_address, nick_name, *args, **kwargs):
    lock.acquire()
    print(len(nick_name), nick_n.values())
    if len(nick_name) > 2 and nick_name not in nick_n.values():
        nick_n[client_address] = nick_name
        ok = True
    else:
        ok = False
    lock.release()
    if ok:
        send_to_user(connection, 'you are logined', cmd='NICK_ALLOWED')
    else:
        send_to_user(connection, 'wrong nick', cmd='NICK_NOT_ALLOWED')


def send_to_user(connection, text, **kwargs):
    d = json.dumps({'txt': text, **kwargs}).encode()
    print(d)
    connection.sendall(d)


allowed_command = {'quit': user_quit, 'send_all': send_all, 'set_nickname': set_nickname}
# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 65432)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

# Listen for incoming connections
sock.listen(10)


def handle_user_conn(connection, client_address):
    while True:
        try:
            data = connection.recv(1024)
        except:
            user_quit(connection, client_address)
            break
        if data:
            data = json.loads(data.decode())
            print(data)
            if 'cmd' in data and data['cmd'] in allowed_command:
                try:
                    allowed_command[data['cmd']](connection, client_address, *data['params']['args'],
                                                 **data['params']['kwargs'])
                except:
                    send_to_user(connection, 'wrong command')
            else:
                send_to_user(connection, 'no command')


while True:
    # Wait for a connection
    print('waiting for a connection')
    connection, client_address = sock.accept()
    threading.Thread(target=handle_user_conn, args=(connection, client_address)).start()
    connections[client_address] = connection
