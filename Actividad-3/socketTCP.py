import socket
import random

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
        sequence = segment[1:5]
        datos = segment[5:21]

        parsed = {
            "SYN": 0,
            "ACK": 0,
            "FIN": 0,
            "SEQ": int.from_bytes(sequence, 'big'),
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


    @staticmethod
    def create_segment(parsed_segment):

        segment = bytearray(21)

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
        segment[1:5] = parsed_segment["SEQ"].to_bytes(4, 'big')
        segment[5:21] = parsed_segment["DATOS"]

        return segment
    
    def bind(self, address):
        self.socketUDP.bind(address)
        self.direccionOrigen = address

    def connect(self, address):
        self.direccionDestino = address
        self.seq = random.randint(0, 100)

        parsed = {
            "SYN": 1,
            "ACK": 0,
            "FIN": 0,
            "SEQ": self.seq,
            "DATOS": b''
        }

        mensaje = self.create_segment(parsed)

        self.socketUDP.sendto(mensaje, self.direccionDestino)

        respuesta, add = self.socketUDP.recvfrom(1024)
        parsed_respuesta = self.parse_segment(respuesta)

        if parsed_respuesta["SYN"] == 1 and parsed_respuesta["ACK"] == 1 and parsed_respuesta["FIN"] == 0 and parsed_respuesta["SEQ"] == self.seq + 1:
            self.seq = parsed_respuesta["SEQ"] + 1

            parsed_ack = {
                "SYN": 0,
                "ACK": 1,
                "FIN": 0,
                "SEQ": self.seq,
                "DATOS": parsed_respuesta["DATOS"]
            }

            mensaje_ack = self.create_segment(parsed_ack)
            self.socketUDP.sendto(mensaje_ack, self.direccionDestino)

        else: 
            print("Error en la conexión")

    
    def accept(self):
        mensaje, add = self.socketUDP.recvfrom(1024)
        parsed_mensaje = self.parse_segment(mensaje)

        if parsed_mensaje["SYN"] == 1 and parsed_mensaje["ACK"] == 0 and parsed_mensaje["FIN"] == 0:
            self.direccionDestino = add
            self.seq = parsed_mensaje["SEQ"] + 1

            parsed_syn_ack = {
                "SYN": 1,
                "ACK": 1,
                "FIN": 0,
                "SEQ": self.seq,
                "DATOS": b''
            }

            mensaje_syn_ack = self.create_segment(parsed_syn_ack)
            self.socketUDP.sendto(mensaje_syn_ack, self.direccionDestino)

            respuesta, add = self.socketUDP.recvfrom(1024)
            parsed_respuesta = self.parse_segment(respuesta)

            if parsed_respuesta["SYN"] == 0 and parsed_respuesta["ACK"] == 1 and parsed_respuesta["FIN"] == 0 and parsed_respuesta["SEQ"] == self.seq + 1:

                next_socket = SocketTCP()
                direccion_ip, puerto = self.direccionOrigen
                next_socket.bind((direccion_ip, 0)) #Explicar en el informe el puerto 0 (automático)
                
                return next_socket, next_socket.direccionOrigen


            else:
                print("Error en la conexión")

        else:
            print("Error en la conexión")


    def send(self, message):

        message_length = str(len(message)).encode("utf-8")
        byte_length = len(message_length)
        parsed_length = {
            "SYN": 0,
            "ACK": 0,
            "FIN": 0,
            "SEQ": self.seq,
            "DATOS": message_length.ljust(16, b'\x00')
        }

        mensaje = self.create_segment(parsed_length)
        self.socketUDP.settimeout(5)

        while True:
            self.socketUDP.sendto(mensaje, self.direccionDestino)
            try:
                respuesta, add = self.socketUDP.recvfrom(1024)
                respuesta_parsed = self.parse_segment(respuesta)
                if respuesta_parsed["SYN"] == 0 and respuesta_parsed["ACK"] == 1 and respuesta_parsed["FIN"] == 0 and respuesta_parsed["SEQ"] == self.seq + byte_length:
                    break


            except socket.timeout:
                continue

        contador = 0
        while contador < len(message):
            particion = message[contador:contador+16]
            particion_length = len(particion)

            parsed_particion = {
                "SYN": 0,
                "ACK": 0,
                "FIN": 0,
                "SEQ": self.seq,
                "DATOS": particion.ljust(16, b'\x00')  #Rellena con ceros para llegar a 16 bytes (explicar en informe)
            }
            mensaje_particion = self.create_segment(parsed_particion)

            while True:
                self.socketUDP.sendto(mensaje_particion, self.direccionDestino)
                try:
                    respuesta, add = self.socketUDP.recvfrom(1024)
                    respuesta_parsed = self.parse_segment(respuesta)
                    if respuesta_parsed["SYN"] == 0 and respuesta_parsed["ACK"] == 1 and respuesta_parsed["FIN"] == 0 and respuesta_parsed["SEQ"] == self.seq + particion_length:
                        self.seq += particion_length
                        contador += particion_length
                        break

                except socket.timeout:
                    continue
