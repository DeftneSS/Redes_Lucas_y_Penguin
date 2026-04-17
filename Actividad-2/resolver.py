import binascii
from dnslib import DNSRecord
import socket

def parse_dns(dns_message):

    message = DNSRecord.parse(dns_message)

    msg_dictionary = {"Header": [message.header.id, message.header.a, message.header.auth, message.header.ar],
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
    

    return


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

        print(parse_dns(recv_msg_client))


