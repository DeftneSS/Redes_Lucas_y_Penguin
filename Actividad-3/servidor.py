import socket
import socketTCP

if __name__ == "__main__":
    server_socketTCP = socketTCP.SocketTCP()
    server_socketTCP.bind(("localhost", 1234))
    print("Servidor TCP escuchando en localhost:1234")
    connection_socketTCP, new_address = server_socketTCP.accept()
    print("Conexión establecida con:", new_address)