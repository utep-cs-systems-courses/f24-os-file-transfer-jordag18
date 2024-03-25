#! /usr/bin/env python3

# File transfer server program

import socket, sys, re, os, time
sys.path.append("../lib")  # Adjust if necessary for your folder structure
import params

# Parse server parameters
switchesVarDefaults = (
    (('-l', '--listenPort'), 'listenPort', 50001),
    (('-?', '--usage'), "usage", False),  # boolean (set if present)
)
paramMap = params.parseParams(switchesVarDefaults)
listenPort = paramMap['listenPort']
listenAddr = ''  # Symbolic name meaning all available interfaces
pidAddr = {}  # Maps pid to client address for active connections

if paramMap['usage']:
    params.usage()

# Server code to be run by child process
def serveFile(connAddr):
    sock, addr = connAddr
    print(f'Child: pid={os.getpid()} serving client at {addr}')
    try:
        # Receive file request
        fileName = sock.recv(1024).decode().strip()
        if fileName and os.path.isfile(fileName):
            with open(fileName, 'rb') as f:
                while chunk := f.read(1024):
                    sock.sendall(chunk)
        else:
            msg = 'ERROR: File not found or invalid request\n'
            sock.sendall(msg.encode('utf-8'))
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.shutdown(socket.SHUT_WR)
        sock.close()
        sys.exit(0)  # Terminate child

# Initialize listener socket
listenSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listenSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listenSock.settimeout(5)
listenSock.bind((listenAddr, listenPort))
listenSock.listen(1)
print(f'Listening for file requests on {listenAddr}:{listenPort}...')

while True:
    # Reap zombie child processes
    while pidAddr:
        if (waitResult := os.waitid(os.P_ALL, 0, os.WNOHANG | os.WEXITED)):
            zPid = waitResult.si_pid
            if zPid in pidAddr:
                print(f'Zombie process reaped: pid={zPid}, connected to {pidAddr[zPid]}')
                del pidAddr[zPid]
            else:
                print(f'Notice: Untracked child reaped: pid={zPid}')
        else:
            break

    # Accept new client connections
    try:
        connSockAddr = listenSock.accept()
    except socket.timeout:
        continue

    # Fork a new process for each client
    pid = os.fork()
    if pid == 0:
        listenSock.close()
        serveFile(connSockAddr)
    else:
        sock, addr = connSockAddr
        sock.close()
        pidAddr[pid] = addr
        print(f"Accepted file request from {addr}")

    
