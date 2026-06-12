import router

message = b"hola mundo, este mensaje tiene un poco mas de largo para forzar fragmentacion"

parsed = {
    "ip": "127.0.0.1",
    "port": 8881,
    "ttl": 5,
    "id": 42,
    "offset": 0,
    "length": len(message),
    "flag": 0,
    "message": message
}
IP_packet = router.create_packet(parsed)

fragments_1 = router.fragment_IP_packet(IP_packet, 200)
print(f"len(IP_packet) = {len(IP_packet)}, MTU = 200")
print(f"cantidad de fragmentos = {len(fragments_1)}")
print(f"fragments[0] == IP_packet ? {fragments_1[0] == IP_packet}")

print()

fragments_2 = router.fragment_IP_packet(IP_packet, 30)
print(f"len(IP_packet) = {len(IP_packet)}, MTU = 30")
print(f"cantidad de fragmentos = {len(fragments_2)}")
print(f"tamaños de los fragmentos = {[len(f) for f in fragments_2]}")

IP_packet_v1 = router.reassemble_IP_packet(fragments_1)
IP_packet_v2 = router.reassemble_IP_packet(fragments_2)
print("IP_packet_v1 = IP_packet_v2 ? {}".format(IP_packet_v1 == IP_packet_v2))
