import router

# Construimos IP_packet_v1 manualmente respetando la estructura:
# ip(4) + port(2) + ttl(1) + id(1) + offset(1) + length(4) + flag(1) + message(length)

ip_bytes     = bytes([127, 0, 0, 1])                  # 127.0.0.1
port_bytes   = (8881).to_bytes(2, byteorder="big")
ttl_bytes    = (5).to_bytes(1, byteorder="big")
id_bytes     = (42).to_bytes(1, byteorder="big")
offset_bytes = (0).to_bytes(2, byteorder="big")
message      = b"hola mundo"
length_bytes = len(message).to_bytes(4, byteorder="big")
flag_bytes   = (1).to_bytes(1, byteorder="big")

IP_packet_v1 = (
    ip_bytes
    + port_bytes
    + ttl_bytes
    + id_bytes
    + offset_bytes
    + length_bytes
    + flag_bytes
    + message
)

parsed_IP_packet = router.parse_packet(IP_packet_v1)
IP_packet_v2 = router.create_packet(parsed_IP_packet)

print("parsed_IP_packet:", parsed_IP_packet)
print("IP_packet_v1:", IP_packet_v1)
print("IP_packet_v2:", IP_packet_v2)
print("IP_packet_v1 == IP_packet_v2 ? {}".format(IP_packet_v1 == IP_packet_v2))
