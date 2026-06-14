import sys
import socket

index ={}
def parse_packet(IP_packet):
    ip_bytes = IP_packet[:4]
    port_bytes = IP_packet[4:6]
    ttl_bytes = IP_packet[6]
    id_bytes = IP_packet[7:9]
    offset_bytes = IP_packet[9:11]

    length_bytes = IP_packet[11:15]
    length_int = int.from_bytes(length_bytes, byteorder="big")

    flag_bytes = IP_packet[15]
    message_bytes = IP_packet[16:16 + length_int]

    ip = ".".join(str(byte) for byte in ip_bytes)

    port = int.from_bytes(port_bytes, byteorder="big")

    id = int.from_bytes(id_bytes, byteorder="big")

    offset_int = int.from_bytes(offset_bytes, byteorder="big")

    parsed_packet = {
        "ip": ip,
        "port": port,
        "ttl": ttl_bytes,
        "id": id,
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
    id_bytes = id.to_bytes(2, byteorder="big")
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
    header_size = 16

    if len(IP_packet) <= mtu:
        return [IP_packet]

    parsed = parse_packet(IP_packet)

    base_offset = parsed["offset"]
    original_flag = parsed["flag"]

    message = parsed["message"]

    chunk_size = mtu - header_size

    fragments = []

    offset = 0

    while offset < len(message):

        fragment_message = message[offset:offset + chunk_size]

        parsed_fragment = {
            "ip" : parsed["ip"],
            "port" : parsed["port"],
            "ttl" : parsed["ttl"],
            "id": parsed["id"],
            "offset" : base_offset + offset,
            "length" : len(fragment_message),
            "flag": 1,
            "message": fragment_message
        }

        if original_flag == 1:
            parsed_fragment["flag"] = 1

        else:
            if offset + chunk_size < len(message):
                parsed_fragment["flag"] = 1
            else:
                parsed_fragment["flag"] = 0

        fragments.append(create_packet(parsed_fragment))

        offset += chunk_size

    return fragments

def reassemble_IP_packet(fragment_list):
    parsed_fragments = []
    for fragment in fragment_list:
        parsed_fragment = parse_packet(fragment)
        parsed_fragments.append(parsed_fragment)
    

    parsed_fragments.sort(key=lambda fragment: fragment["offset"])

    if len(parsed_fragments) == 1:

        fragment = parsed_fragments[0]

        if fragment["offset"] == 0 and fragment["flag"] == 0:
            return fragment_list[0]

        return None


    if parsed_fragments[0]["offset"] != 0:
        return None
    if parsed_fragments[len(parsed_fragments)-1]["flag"] != 0:
        return None
    
    expected_offset = 0
    for fragment in parsed_fragments:

        if fragment["offset"] != expected_offset:
            return None

        expected_offset += fragment["length"]

    full_message = b""
    for fragment in parsed_fragments:
        full_message += fragment["message"]
    
    first_fragment = parsed_fragments[0]

    parsed_packet = {
        "ip": first_fragment["ip"],
        "port": first_fragment["port"],
        "ttl": first_fragment["ttl"],
        "id": first_fragment["id"],
        "offset": 0,
        "length": len(full_message),
        "flag": 0,
        "message": full_message
    }

    return create_packet(parsed_packet)

if __name__ == "__main__":
    ip = sys.argv[1]
    puerto = sys.argv[2]
    tabla_de_rutas = sys.argv[3]
    direccion = (ip,int(puerto))
    ID_dictionary = {}

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
        elif packet_ip == ip and packet_port == int(puerto):
            if parsed_packet["id"] not in ID_dictionary:
                ID_dictionary[parsed_packet["id"]] = []
            ID_dictionary[parsed_packet["id"]].append(packet)
            reensamblado = reassemble_IP_packet(ID_dictionary[parsed_packet["id"]])
            if reensamblado is None:
                continue
            mensaje_reensamblado = parse_packet(reensamblado)["message"].decode()
            print(mensaje_reensamblado)
            del ID_dictionary[parsed_packet["id"]]
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


