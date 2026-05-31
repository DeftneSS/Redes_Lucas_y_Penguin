import binascii
from  dnslib import DNSRecord
from dnslib import CLASS, QTYPE
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


def resolver(parsed_msg, address_port, debug=False):
    qname = parsed_msg["Question"]
    query = DNSRecord.question(qname)
    server_address = address_port

    if debug:
        print(f"(debug) Consultando '{qname}' a '.' con dirección IP '{address_port[0]}'")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        sock.sendto(bytes(query.pack()), server_address)
        data, _ = sock.recvfrom(1024)
        response = DNSRecord.parse(data)
        if (response.header.a >= 1):
            for rr in response.rr:
                if (QTYPE[rr.rtype] == "A"): #Busca tipo A en Answer
                    return response
        elif (response.header.auth >= 1):
            for rr in response.auth:
                if (QTYPE[rr.rtype] == "NS"): #Busca tipo NS en Authority
                    ns_name = str(rr.rdata)
                    ns_ip = None
                    for ar in response.ar:
                        if (QTYPE[ar.rtype] == "A"): #Busca tipo A en Additional
                            ns_ip = str(ar.rdata)
                            break
                    if (ns_ip):
                        return resolver(parsed_msg, (ns_ip, 53), debug)  # ✅ pasa debug
                    else:
                        ns_parsed = {"Question": ns_name}
                        ns_response = resolver(ns_parsed, address_port, debug)  # ✅ pasa debug
                        for rr in ns_response.rr:
                            if (QTYPE[rr.rtype] == "A"):
                                ns_ip = str(rr.rdata)
                                break
                        return resolver(parsed_msg, (ns_ip, 53), debug)
                else:
                    return None

    finally:
        sock.close()

    return response


if __name__ == "__main__":
    buff_size = 1024
    new_socket_address = ('192.168.1.118',8000)
    root_server = ('192.33.4.12', 53)

    print('Creando socket - Resolver')

    socket_resolver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    socket_resolver.bind(new_socket_address)

    print('...Esperando cliente')

    while True:
        recv_msg_client, client_address = socket_resolver.recvfrom(buff_size)
        parsed = parse_dns(recv_msg_client)
        original_id = parsed["Header"][0]
        
        response = resolver(parsed, root_server, debug=True)
        
        if response:
            response.header.id = original_id
            socket_resolver.sendto(response.pack(), client_address)


