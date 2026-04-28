import socket

if __name__ == "__main__":
    new_socket_address = ('localhost', 8000)

    print('Creando socket - Cliente')
    socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print('Esperando servidor...')

    while True:
        archivo = input('Archivo a enviar: ')
        with open(archivo, 'rb') as file:
            while True:
                data = file.read(16)
                if not data:
                    break
                socket_cliente.sendto(data, new_socket_address)