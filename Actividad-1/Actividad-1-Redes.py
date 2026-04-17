import socket
import json


def parse_HTTP_message(http_message):

    msg_head = http_message.split(b'\r\n\r\n')
    head_lines = msg_head[0].split(b'\r\n')

    return head_lines + [msg_head[1]]


def create_HTTP_message(parsed_message, nombre_json):
    
    head1 = b''

    for i in range(0, len(parsed_message) - 1):
        head1 += parsed_message[i] + b'\r\n'

    head1 += f'X-ElQuePregunta: {nombre_json}'.encode('utf-8') + b'\r\n\r\n'

    full_message = head1 + parsed_message[len(parsed_message) - 1]

    return full_message

if __name__ == "__main__":
    buff_size = 1024
    new_socket_address = ('192.168.56.101',8000)
    with open("archivo.json") as file:
        data = json.load(file)
        nom_json = data["nombre"]
    

print('Creando socket- Servidor')

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind(new_socket_address)

server_socket.listen(1)

print('...Esperando cliente')

while True:
    new_socket, new_socket_address = server_socket.accept()

    recv_msg_client = new_socket.recv(buff_size)

    with open('cliente.html', 'r') as f:

        response_message = f.read().encode().decode('unicode_escape').replace("\n", "\r\n")

    recv_message = parse_HTTP_message(response_message.encode('utf-8'))

    http_message = create_HTTP_message(recv_message, nom_json)

    new_socket.send(http_message)

    new_socket.close()
    print(f'Conexión con {new_socket_address} ha sido cerrada')