import socket
import sys
import router

if __name__ == "__main__":
    direccion_final = (sys.argv[1], int(sys.argv[2]))
    direccion_envio = (sys.argv[3], int(sys.argv[4]))
    mensaje = sys.argv[5]

    parsed_packet = {
        "ip": direccion_final[0],
        "port": direccion_final[1],
        "message": mensaje.encode()
    }
    packet = router.create_packet(parsed_packet)
    socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socketUDP.sendto(packet, direccion_envio)
    socketUDP.close()
