import socket

class SocketTCP():
    def __init__(self):
        
        self.socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.direccionDestino = None
        self.direccionOrigen = None
        self.seq = 0
        self.ack = 0
        self.fin = 0

    @staticmethod
    def parse_segment(segment):

        header = segment[0]
        sequence = segment[1:4]
        datos = segment[5:20]

        parsed = {
            "SYN": 0,
            "ACK": 0,
            "FIN": 0,
            "SEQ": sequence,
            "DATOS": datos
        }

        if  (header == 4):
            parsed["SYN"] = 1

        if (header == 2):
            parsed["ACK"] = 1

        if (header == 6):
            parsed["SYN"] = 1
            parsed["ACK"] = 1

        if (header == 1):
            parsed["FIN"] = 1

        if (header == 3):
            parsed["FIN"] = 1
            parsed["ACK"] = 1

        return parsed


    def create_segment(parsed_segment):

        segment = bytearray(20)

        if parsed_segment["SYN"] == 1 and parsed_segment["ACK"] == 0 and parsed_segment["FIN"] == 0:
            header = 4

        if parsed_segment["SYN"] == 0 and parsed_segment["ACK"] == 1 and parsed_segment["FIN"] == 0:
            header = 2

        if parsed_segment["SYN"] == 1 and parsed_segment["ACK"] == 1 and parsed_segment["FIN"] == 0:
            header = 6

        if parsed_segment["SYN"] == 0 and parsed_segment["ACK"] == 0 and parsed_segment["FIN"] == 1:
            header = 1

        if parsed_segment["SYN"] == 0 and parsed_segment["ACK"] == 1 and parsed_segment["FIN"] == 1:
            header = 3

        if parsed_segment["SYN"] == 0 and parsed_segment["ACK"] == 0 and parsed_segment["FIN"] == 0:
            header = 0

        segment[0] = header
        segment[1:4] = parsed_segment["SEQ"]
        segment[5:20] = parsed_segment["DATOS"]

        return segment