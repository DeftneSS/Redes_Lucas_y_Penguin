import socket
import sys
import router

if __name__ == "__main__":


    ip_destino, puerto_destino, ttl = sys.argv[1].split(";")

    direccion_final = (
        ip_destino,
        int(puerto_destino)
    )

    direccion_envio = (
        sys.argv[2],
        int(sys.argv[3])
    )
    socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    with open("archivo_prueba.txt", "r") as f:
        for linea in f:
            mensaje = linea.encode()
            parsed_packet = {
            "ip": direccion_final[0],
            "port": direccion_final[1],
            "ttl": int(ttl),
            "message": mensaje
            }
            packet = router.create_packet(parsed_packet)

            socketUDP.sendto(packet, direccion_envio)

    socketUDP.close()