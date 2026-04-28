import socket

if __name__ == "__main__":
    buff_size = 1024
    new_socket_address = ('localhost', 8000)

    print('Creando socket - Servidor')
    socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_servidor.bind(new_socket_address)
    print('Esperando cliente...')

    mensaje_recibido = ''

    while True:
        recv_msg_client, client_address = socket_servidor.recvfrom(buff_size)
        mensaje_recibido += recv_msg_client.decode('utf-8')

        print(mensaje_recibido)