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
        datos = segment[1:16]

        parsed = {
            "SYN": 0,
            "ACK": 0,
            "FIN": 0,
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

        if (header == 0):
            parsed["DATOS"] = 1


        return parsed

    def create_segment(parsed_segment):



        return