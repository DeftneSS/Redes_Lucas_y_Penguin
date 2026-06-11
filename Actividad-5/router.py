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
            if line == "":
                continue
            direccion_fin, puerto_ini, puerto_fin, direccion_sig, puerto_sig, mtu = line.split()

            puerto_ini = int(puerto_ini)
            puerto_fin = int(puerto_fin)
            puerto_sig = int(puerto_sig)
            mtu = int(mtu)

            ip_fin = direccion_fin.split("/")[0]
            if ip_fin != ip_destino:
                continue

            if puerto_ini <= puerto_destino <= puerto_fin:
                routes.append((direccion_sig, puerto_sig))
    if len(routes) == 0:
        return None
    end = destination_addres
    if end not in index:
        index[end] = 0
    act_route = routes[index[end]]
    index[end] = (index[end] + 1) % len(routes)

    return act_route, mtu

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
            next_dir = check_routes(tabla_de_rutas, destino_final)
            if next_dir is not None:
                print(f"Redirigiendo paquete {packet} con destino final {destino_final} desde {direccion} hacia {next_dir}")
                parsed_packet["ttl"] = parsed_packet["ttl"] - 1
                packet = create_packet(parsed_packet)
                socketUDP.sendto(packet, next_dir)
            else:
                print(f"No hay rutas hacia {destino_final} para paquete {packet}")


