import sys
import socket

index ={}
def parse_packet(IP_packet):
    ip_bytes = IP_packet[:4]
    port_bytes = IP_packet[4:6]
    ttl_bytes = IP_packet[6]
    id_bytes = IP_packet[7]
    offset_bytes = IP_packet[8:10]

    length_bytes = IP_packet[10:14]
    length_int = int.from_bytes(length_bytes, byteorder="big")

    flag_bytes = IP_packet[14]
    message_bytes = IP_packet[15:15 + length_int]

    ip = ".".join(str(byte) for byte in ip_bytes)

    port = int.from_bytes(port_bytes, byteorder="big")

    offset_int = int.from_bytes(offset_bytes, byteorder="big")

    parsed_packet = {
        "ip": ip,
        "port": port,
        "ttl": ttl_bytes,
        "id": id_bytes,
        "offset": offset_int,
        "length": length_int,
        "flag": flag_bytes,
        "message": message_bytes
    }
    return parsed_packet

def create_packet(parsed_packet):
    ip = parsed_packet["ip"]
    port = parsed_packet["port"]
    ttl = parsed_packet["ttl"]
    id = parsed_packet["id"]
    offset = parsed_packet["offset"]
    length = parsed_packet["length"]
    flag = parsed_packet["flag"]
    message = parsed_packet["message"]

    ip_bytes = bytes(int(num) for num in ip.split("."))
    port_bytes = port.to_bytes(2, byteorder="big")
    ttl_bytes = ttl.to_bytes(1, byteorder="big")
    id_bytes = id.to_bytes(1, byteorder="big")
    offset_bytes = offset.to_bytes(2, byteorder="big")
    length_bytes = length.to_bytes(4, byteorder="big")
    flag_bytes = flag.to_bytes(1, byteorder="big")
    IP_packet = ip_bytes + port_bytes + ttl_bytes + id_bytes + offset_bytes + length_bytes + flag_bytes + message

    return IP_packet



def check_routes(routes_file_name, destination_addres):
    global index
    ip_destino, puerto_destino = destination_addres
    routes = []
    with open(routes_file_name, "r") as file:
        for line in file:
            line = line.strip()
            if line == "" or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 5:
                continue

            direccion_fin = parts[0]
            puerto_ini = int(parts[1])
            puerto_fin = int(parts[2])
            direccion_sig = parts[3]
            puerto_sig = int(parts[4])
            if len(parts) >= 6:
                mtu = int(parts[5])
            else:
                mtu = None

            ip_fin = direccion_fin.split("/")[0]
            if ip_fin != ip_destino:
                continue

            if puerto_ini <= puerto_destino <= puerto_fin:
                routes.append((direccion_sig, puerto_sig, mtu))
    if len(routes) == 0:
        return None
    end = destination_addres
    if end not in index:
        index[end] = 0
    direccion_sig, puerto_sig, mtu = routes[index[end]]
    index[end] = (index[end] + 1) % len(routes)

    act_route = (direccion_sig, puerto_sig)
    return act_route, mtu


def fragment_IP_packet(IP_packet, mtu):
    header_size = 15
    if len(IP_packet) <= mtu:
        return [IP_packet]

    message = IP_packet[header_size:]
    message_length = len(message)
    chunk_size = mtu - header_size

    fragments = []
    offset = 0
    while offset < message_length:
        fragment_message = message[offset:offset + chunk_size]
        fragment_length = len(fragment_message)
        fragment_offset = offset // chunk_size

        if offset + chunk_size < message_length:
            flag = 1
        else:
            flag = 0

        fragment_header = bytearray(IP_packet[:header_size])
        fragment_header[8:10] = fragment_offset.to_bytes(2, byteorder="big")
        fragment_header[10:14] = fragment_length.to_bytes(4, byteorder="big")
        fragment_header[14] = flag

        fragments.append(bytes(fragment_header) + fragment_message)
        offset += chunk_size

    return fragments

def reassemble_IP_packet(fragment_list):
    if not fragment_list:
        return None

    header_size = 15

    by_offset = {}
    headers_by_offset = {}
    for fragment in fragment_list:
        parsed = parse_packet(fragment)
        by_offset[parsed["offset"]] = parsed
        headers_by_offset[parsed["offset"]] = fragment[:header_size]

    total = len(fragment_list)

    if total == 1:
        fragment = by_offset[next(iter(by_offset))]
        if fragment["offset"] == 0 and fragment["flag"] == 0:
            return fragment_list[0]
        return None
    
    for i in range(total):
        if i not in by_offset:
            return None
        if i == total - 1:
            expected_flag = 0
        else:
            expected_flag = 1
        if by_offset[i]["flag"] != expected_flag:
            return None

    full_message = b"".join(by_offset[i]["message"] for i in range(total))

    nuevo_header = bytearray(headers_by_offset[0])
    nuevo_header[8:10] = (0).to_bytes(2, byteorder="big")
    nuevo_header[10:14] = len(full_message).to_bytes(4, byteorder="big")
    nuevo_header[14] = 0

    return bytes(nuevo_header) + full_message


if __name__ == "__main__":
    ip = sys.argv[1]
    puerto = sys.argv[2]
    tabla_de_rutas = sys.argv[3]
    direccion = (ip,int(puerto))

    socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socketUDP.bind(direccion)
    while True:
        packet, sender_add = socketUDP.recvfrom(1024)
        parsed_packet = parse_packet(packet)
        packet_ip = parsed_packet["ip"]
        packet_port = parsed_packet["port"]
        destino_final = (packet_ip, packet_port)
        if parsed_packet["ttl"] == 0:
            print(f"Se recibió paquete {packet_ip} con ttl 0")
        if packet_ip == ip and packet_port == int(puerto):
            mensaje = parsed_packet["message"].decode()
            print(mensaje)
        else:
            result = check_routes(tabla_de_rutas, destino_final)
            if result is not None:
                act_route, mtu = result
                print(f"Redirigiendo paquete {packet} con destino final {destino_final} desde {direccion} hacia {act_route} (MTU={mtu})")
                parsed_packet["ttl"] = parsed_packet["ttl"] - 1
                packet = create_packet(parsed_packet)
                fragments = fragment_IP_packet(packet, mtu)
                for fragment in fragments:
                    socketUDP.sendto(fragment, act_route)
            else:
                print(f"No hay rutas hacia {destino_final} para paquete {packet}")


