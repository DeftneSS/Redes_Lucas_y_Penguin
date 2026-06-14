import socket
import sys
import router

if __name__ == "__main__":

    ip_destino, puerto_destino, ttl, mensaje = sys.argv[1].split(";")
    mensaje_bytes = mensaje.encode()
    direccion_final = (
        ip_destino,
        int(puerto_destino)
    )

    direccion_envio = (
        sys.argv[2],
        int(sys.argv[3])
    )

    parsed_packet = {
        "ip": direccion_final[0],
        "port": direccion_final[1],
        "ttl": int(ttl),
        "id": 347,
        "offset": 0,
        "length": len(mensaje_bytes),
        "flag": 0,
        "message": mensaje_bytes
    }

    packet = router.create_packet(parsed_packet)

    socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    socketUDP.sendto(packet, direccion_envio)

    socketUDP.close()