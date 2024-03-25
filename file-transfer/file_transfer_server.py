#! /usr/bin/env python3

import socket
import select
import os

# Constants
HEADER_LENGTH = 10
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 12345
BUFFER_SIZE = 1024

# Set up the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen()
server_socket.setblocking(False)

# Lists for tracking sockets
sockets_list = [server_socket]
clients = {}

def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length = int(message_header.decode('utf-8').strip())
        return {'header': message_header, 'data': client_socket.recv(message_length)}
    except:
        return False

def send_file_contents(client_socket, file_path):
    if not os.path.exists(file_path):
        error_message = 'ERROR: File not found\n'
        client_socket.send(f"{len(error_message):<{HEADER_LENGTH}}".encode('utf-8') + error_message.encode('utf-8'))
        return
    
    with open(file_path, 'rb') as file:
        while True:
            bytes_read = file.read(BUFFER_SIZE)
            if not bytes_read:
                break  # File sending is done
            message = f"{len(bytes_read):<{HEADER_LENGTH}}".encode('utf-8') + bytes_read
            client_socket.send(message)

print(f'Listening for connections on {SERVER_HOST}:{SERVER_PORT}...')

while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()
            print(f"Accepted new connection from {client_address[0]}:{client_address[1]}")
            sockets_list.append(client_socket)
            clients[client_socket] = {'header': None, 'data': None}
        else:
            message = receive_message(notified_socket)
            if message is False:
                print(f"Closed connection from {clients[notified_socket]['data'].decode('utf-8')}")
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue
            user = clients[notified_socket]
            user['header'] = message['header']
            user['data'] = message['data']
            file_name = message['data'].decode('utf-8')
            print(f"Received file request for: {file_name} from {notified_socket.getpeername()}")
            send_file_contents(notified_socket, file_name)
    
    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
