import binascii
from  dnslib import DNSRecord
import socket

def parse_dns(dns_message):

    message = DNSRecord.parse(dns_message)

    msg_dictionary   =  {"Header": [message.header.id, message.header.a, message.header.auth, message.header.ar],
                        "Question": str(message.get_q().get_qname()),
                        "Answer": message.rr,
                        "Authority": message.auth,
                        "Additional": message.ar
                        }

    

    return msg_dictionary


def resolver(parsed_msg, address_port):

    qname = parsed_msg["Question"]
    query = DNSRecord.question(qname)
    server_address = (address_port)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:

        sock.sendto(bytes(query.pack()), server_address)
        data, _ = sock.recvfrom(1024)
        response = DNSRecord.parse(data)
        data_type = response.rr.rtype
        print(data_type) #número

    finally:
        sock.close()

    return response


if __name__ == "__main__":
    buff_size = 1024
    new_socket_address = ('172.20.10.3',8000)
    root_server = ('192.33.4.12', 53)

    print('Creando socket - Resolver')

    socket_resolver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    socket_resolver.bind(new_socket_address)

    print('...Esperando cliente')

    while True:
        recv_msg_client, client_address = socket_resolver.recvfrom(buff_size)

        print(f'Conexión con {client_address} ha sido establecida')

        resolver(parse_dns(recv_msg_client), root_server)


