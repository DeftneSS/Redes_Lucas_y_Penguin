import socket
import socketTCP

if __name__ == "__main__":
    client_socketTCP = socketTCP.SocketTCP()
    client_socketTCP.connect(("localhost", 1234))