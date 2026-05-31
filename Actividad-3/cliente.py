import sys
import socketTCP

host = sys.argv[1]
puerto = int(sys.argv[2])

if __name__ == "__main__":
    client_socket = socketTCP.SocketTCP()
    contenido = sys.stdin.buffer.read()
    client_socket.connect((host, puerto))
    print("Conexion exitosa")
    client_socket.send(contenido)
    print("Contenido enviado")
    client_socket.close()
    print("socket cerrado")
