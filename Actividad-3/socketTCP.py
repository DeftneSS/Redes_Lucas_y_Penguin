import socket

class SocketTCP():
    def __init__(self):
        
        self.socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.direccionDestino = None
        self.direccionOrigen = None
        self.seq = 0
        self.ack = 0

    @staticmethod
    def parse_segment(segment):

        segment


        return


    def create_segment(parsed_segment):



        return