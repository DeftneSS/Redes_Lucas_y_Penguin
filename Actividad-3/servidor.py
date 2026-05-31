import sys
import socketTCP



if __name__ == "__main__":
    buff_size = 1024
    new_socket_address = ('localhost', 8000)

    print('Creando socket - Servidor')

    socket_servidor = socketTCP.SocketTCP()
    socket_servidor.bind(new_socket_address)

    print('Esperando cliente...')
    

    new_socket, new_address = socket_servidor.accept()
    mensaje_recibido1 = new_socket.recv(70)
    mensaje_recibido2 = new_socket.recv(70)

    print(mensaje_recibido1 + mensaje_recibido2)

    new_socket.recv_close()
    print("Se cerro el socket")