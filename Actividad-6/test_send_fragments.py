import socket
import sys
import router

def armar(mensaje, packet_id):
    return router.create_packet({
        "ip": "127.0.0.1",
        "port": 8881,
        "ttl": 5,
        "id": packet_id,
        "offset": 0,
        "length": len(mensaje),
        "flag": 0,
        "message": mensaje
    })

frags_1 = router.fragment_IP_packet(armar(b"primer mensaje largo para fragmentar", 1), 30)
frags_2 = router.fragment_IP_packet(armar(b"segundo mensaje largo para fragmentar", 2), 30)

modo = sys.argv[1] if len(sys.argv) >= 2 else "orden"
direccion = ("127.0.0.1", 8881)

if modo == "orden":
    envio = frags_1 + frags_2
elif modo == "desorden":
    envio = list(reversed(frags_1)) + list(reversed(frags_2))
elif modo == "intercalado":
    envio = []
    for i in range(max(len(frags_1), len(frags_2))):
        if i < len(frags_1): envio.append(frags_1[i])
        if i < len(frags_2): envio.append(frags_2[i])

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
for f in envio:
    sock.sendto(f, direccion)
sock.close()
print(f"enviado modo={modo}, total fragmentos={len(envio)}")
