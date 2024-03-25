#! /usr/bin/env python3

import socket
import sys
import os

# Constants
HEADER_LENGTH = 10
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345
BUFFER_SIZE = 1024

# Set up the client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_HOST, SERVER_PORT))
client_socket.setblocking(True)

def send_request(filename):
    request = filename.encode('utf-8')
    request_header = f"{len(request):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(request_header + request)

def save_response(filename):
    while True:
        file_chunk_header = client_socket.recv(HEADER_LENGTH)
        if not file_chunk_header:
            print("Connection closed by the server")
            sys.exit()
        file_chunk_length = int(file_chunk_header.decode('utf-8').strip())
        if file_chunk_length == 0:
            break  # End of file
        file_chunk = client_socket.recv(file_chunk_length)
        if file_chunk.startswith(b'ERROR'):
            print(file_chunk.decode('utf-8'))
            break
        with open(f'received_{filename}', 'ab') as file:
            file.write(file_chunk)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: file_transfer_client.py <filename>")
        sys.exit(1)
    filename = sys.argv[1]
    send_request(filename)
    save_response(filename)
    client_socket.close()
