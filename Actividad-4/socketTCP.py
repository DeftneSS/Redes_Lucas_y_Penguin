import socket
import random
from socketUDP import SocketUDP
from slidingWindowCC import SlidingWindowCC as swcc

class SocketTCP():
    def __init__(self):
        
        self.socketUDP = SocketUDP()
        self.direccionDestino = None
        self.direccionOrigen = None
        self.seq = 0
        self.ack = 0
        self.fin = 0
        self.msg_perdido = None
        self.in_mensaje = 0
        self.return_length = 0
        self.recibido_total = 0
        self.mensaje_recibido = b''

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
        self.socketUDP.settimeout(5)

        while True:
            self.socketUDP.sendto(mensaje, self.direccionDestino)

            try:
                respuesta, add = self.socketUDP.recvfrom(1024)
                parsed_respuesta = self.parse_segment(respuesta)

                if parsed_respuesta["SYN"] == 1 and parsed_respuesta["ACK"] == 1 and parsed_respuesta["FIN"] == 0 and parsed_respuesta["SEQ"] == self.seq + 1:
                    self.seq = parsed_respuesta["SEQ"] + 1
                    break

            except socket.timeout:
                continue

        parsed_ack = {
            "SYN": 0, 
            "ACK": 1, 
            "FIN": 0,
            "SEQ": self.seq, 
            "DATOS": b''
            }        
        
        mensaje_ack = self.create_segment(parsed_ack)
        self.socketUDP.sendto(mensaje_ack, self.direccionDestino)

    
    def accept(self):

        while True:
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

                break

        mensaje_syn_ack = self.create_segment(parsed_syn_ack)
        self.socketUDP.settimeout(5)

        while True:
            self.socketUDP.sendto(mensaje_syn_ack, self.direccionDestino)

            try:
                respuesta, add = self.socketUDP.recvfrom(1024)
                parsed_respuesta = self.parse_segment(respuesta)

                if parsed_respuesta["SYN"] == 0 and parsed_respuesta["ACK"] == 1 and parsed_respuesta["FIN"] == 0 and parsed_respuesta["SEQ"] == self.seq + 1:
                    self.seq = parsed_respuesta["SEQ"]
                    return self, self.direccionOrigen
                
                if parsed_respuesta["SYN"] == 0 and parsed_respuesta["ACK"] == 0 and parsed_respuesta["FIN"] == 0:
                    self.seq = parsed_respuesta["SEQ"]
                    self.msg_perdido = parsed_respuesta
                    return self, self.direccionOrigen


            except socket.timeout:
                continue



    def send(self, message, mode="stop_and_wait"):
        if mode == "stop_and_wait":
            self.send_using_stop_and_wait(message)
        elif mode == "go_back_n":
            self.send_using_go_back_n(message)


    def recv(self, buff_size, mode="stop_and_wait"):
        if mode == "stop_and_wait":
            return self.recv_using_stop_and_wait(buff_size)
        elif mode == "go_back_n":
            return self.recv_using_go_back_n(buff_size)

        
    
    def close(self):
        self.socketUDP.settimeout(5)

        parsed_fin = {
            "SYN": 0, 
            "ACK": 0, 
            "FIN": 1,
            "SEQ": self.seq, 
            "DATOS": b''
            }
        
        mensaje_fin = self.create_segment(parsed_fin)

        intentos = 0
        fin_recibido = False

        while intentos < 3 and not fin_recibido:
            self.socketUDP.sendto(mensaje_fin, self.direccionDestino)
            try:
                respuesta, _ = self.socketUDP.recvfrom(1024)
                parsed = self.parse_segment(respuesta)

                if (parsed["FIN"] == 1 and parsed["ACK"] == 1 and parsed["SEQ"] == self.seq + 1):
                    self.seq = parsed["SEQ"] + 1
                    fin_recibido = True

            except socket.timeout:
                intentos += 1

        if fin_recibido:
            parsed_ack = {
                "SYN": 0, 
                "ACK": 1, 
                "FIN": 0,
                "SEQ": self.seq, 
                "DATOS": b''
                }
            
            mensaje_ack = self.create_segment(parsed_ack)

            for i in range(3):
                self.socketUDP.sendto(mensaje_ack, self.direccionDestino)
                if i < 2:
                    try:
                        self.socketUDP.recvfrom(1024) 
                    except socket.timeout:
                        pass

        self.socketUDP.close()


    def recv_close(self):

        self.socketUDP.settimeout(5)

        while True:
            mensaje, _ = self.socketUDP.recvfrom(1024)
            parsed = self.parse_segment(mensaje)
            if (parsed["FIN"] == 1 and parsed["ACK"] == 0):
                self.seq = parsed["SEQ"] + 1
                break

        parsed_ack = {
            "SYN": 0, 
            "ACK": 1, 
            "FIN": 1,
            "SEQ": self.seq, 
            "DATOS": b''
            }
        
        mensaje_ack = self.create_segment(parsed_ack)
        self.socketUDP.sendto(mensaje_ack, self.direccionDestino)
        intentos = 0

        while intentos < 3:
            try:
                mensaje, _ = self.socketUDP.recvfrom(1024)
                parsed = self.parse_segment(mensaje)

                if (parsed["FIN"] == 0 and parsed["ACK"] == 1 and parsed["SEQ"] == self.seq + 1):
                    break

                if (parsed["FIN"] == 1 and parsed["ACK"] == 0):
                    self.socketUDP.sendto(mensaje_ack, self.direccionDestino)

            except socket.timeout:
                intentos += 1

        self.socketUDP.close()

    def send_using_stop_and_wait(self, message):

        message_length = str(len(message)).encode("utf-8")

        parsed_length = {
            "SYN": 0,
            "ACK": 0,
            "FIN": 0,
            "SEQ": self.seq,
            "DATOS": message_length
        }

        byte_length = len(message_length)
        mensaje = self.create_segment(parsed_length)
        self.socketUDP.settimeout(5)

        while True:
            self.socketUDP.sendto(mensaje, self.direccionDestino)
            try:
                respuesta, add = self.socketUDP.recvfrom(1024)
                respuesta_parsed = self.parse_segment(respuesta)
                if respuesta_parsed["SYN"] == 0 and respuesta_parsed["ACK"] == 1 and respuesta_parsed["FIN"] == 0 and respuesta_parsed["SEQ"] == self.seq + byte_length:
                    self.seq += byte_length
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

    def recv_using_stop_and_wait(self, buff_size):

        if self.in_mensaje == 0:
            while True:
                if self.msg_perdido is not None:
                    parsed_mensaje = self.msg_perdido
                    self.msg_perdido = None
                else:
                    mensaje, _ = self.socketUDP.recvfrom(1024)
                    parsed_mensaje = self.parse_segment(mensaje)

                if parsed_mensaje["SEQ"] == self.seq:
                    break

                parsed_duplicado = {
                    "SYN": 0,
                    "ACK": 1,
                    "FIN": 0,
                    "SEQ": self.seq,
                    "DATOS": b''
                }

                mensaje_duplicado = self.create_segment(parsed_duplicado)
                self.socketUDP.sendto(mensaje_duplicado, self.direccionDestino)

            datos = parsed_mensaje["DATOS"].rstrip(b'\x00')
            byte_length = len(datos)
            int_length = int(datos.decode("utf-8"))

            self.return_length = int_length
            self.recibido_total = 0
            self.buffer = b''
            self.seq = parsed_mensaje["SEQ"] + byte_length

            parsed_ack = {
                "SYN":0,
                "ACK":1, 
                "FIN":0, 
                "SEQ": self.seq, 
                "DATOS": b''
                }
            
            mensaje_ack = self.create_segment(parsed_ack)
            self.socketUDP.sendto(mensaje_ack, self.direccionDestino)
            self.in_mensaje = 1


        while len(self.buffer) < buff_size and self.recibido_total < self.return_length:

            mensaje, _ = self.socketUDP.recvfrom(1024)
            parsed_mensaje = self.parse_segment(mensaje)

            if parsed_mensaje["SEQ"] == self.seq:
                bytes_restantes = self.return_length - self.recibido_total
                particion = min(16, bytes_restantes)
                self.buffer += parsed_mensaje["DATOS"][:particion]
                self.recibido_total += particion
                self.seq += particion

                parsed_ack = {
                    "SYN":0, 
                    "ACK":1, 
                    "FIN":0, 
                    "SEQ": self.seq, 
                    "DATOS": b''
                    }
                
                mensaje_ack = self.create_segment(parsed_ack)
                self.socketUDP.sendto(mensaje_ack, self.direccionDestino)

            else:
                parsed_duplicado = {
                    "SYN": 0,
                    "ACK": 1,
                    "FIN": 0,
                    "SEQ": self.seq,
                    "DATOS": b''
                }

                mensaje_duplicado = self.create_segment(parsed_duplicado)
                self.socketUDP.sendto(mensaje_duplicado, self.direccionDestino)

        msg_buffer = self.buffer[:buff_size]
        self.buffer = self.buffer[buff_size:]

        if self.recibido_total >= self.return_length and len(self.buffer) == 0:
            self.in_mensaje = 0

        return msg_buffer

    def send_using_go_back_n(self, message):
        
        message_length = str(len(message)).encode("utf-8")

        data_list = [message[i:i+16] for i in range(0, len(message), 16)]
        initial_seq = self.seq
        data_to_send = swcc(4, [message_length] + data_list, initial_seq)

        current_data = data_to_send.get_data(0)
        current_seq = data_to_send.get_sequence_number(0)
        
        current_segment = {
            "SYN": 0,
            "ACK": 0,
            "FIN": 0,
            "SEQ": current_seq,
            "DATOS": current_data.ljust(16, b'\x00')
        }

        mensaje = self.create_segment(current_segment)
        self.socketUDP.settimeout(5)

        for i in range(4):

            data_i = data_to_send.get_data(i)
            if data_i is None:
                break
            seq_i = data_to_send.get_sequence_number(i)

            parsed_i = {
                "SYN":0,
                "ACK":0,
                "FIN":0,
                "SEQ":seq_i,
                "DATOS":data_i.ljust(16, b'\x00')
            }

            self.socketUDP.sendto(self.create_segment(parsed_i), self.direccionDestino)

        while current_data is not None:
            try:
                respuesta, _ = self.socketUDP.recvfrom(1024)
                respuesta_parsed = self.parse_segment(respuesta)

                if not (respuesta_parsed["ACK"] == 1 and respuesta_parsed["SYN"] == 0 and respuesta_parsed["FIN"] == 0):
                    continue

                ack_seq = respuesta_parsed["SEQ"]

                steps = 0
                for i in range(4):
                    seq_i = data_to_send.get_sequence_number(i)
                    data_i = data_to_send.get_data(i)
                    if seq_i is None or data_i is None:
                        break
                    if ack_seq == seq_i + len(data_i):
                        steps = i + 1

                if steps > 0:
                    self.socketUDP.stop_timer()
                    data_to_send.move_window(steps)

                    timer_restarted = False
                    for i in range(4 - steps, 4):
                        new_data = data_to_send.get_data(i)
                        if new_data is None:
                            continue
                        new_seq = data_to_send.get_sequence_number(i)
                        parsed_new = {
                            "SYN": 0,
                            "ACK": 0,
                            "FIN": 0,
                            "SEQ": new_seq,
                            "DATOS": new_data.ljust(16, b'\x00')
                        }
                        self.socketUDP.sendto(self.create_segment(parsed_new), self.direccionDestino)
                        timer_restarted = True

                    if not timer_restarted and data_to_send.get_data(0) is not None:
                        prim_datos = data_to_send.get_data(0)
                        prim_seq = data_to_send.get_sequence_number(0)
                        parsed = {
                            "SYN": 0,
                            "ACK": 0,
                            "FIN": 0,
                            "SEQ": prim_seq,
                            "DATOS": prim_datos.ljust(16, b'\x00')
                        }
                        self.socketUDP.sendto(self.create_segment(parsed), self.direccionDestino)

                    # ack_seq es el próximo byte esperado (cumulative ACK).
                    # Lo guardamos como self.seq así el próximo send arranca desde la
                    # posición correcta, incluso si la ventana se vació.
                    self.seq = ack_seq
                    current_data = data_to_send.get_data(0)

            except TimeoutError:
                self.socketUDP.stop_timer()
                for i in range(4):
                    data_i = data_to_send.get_data(i)
                    if data_i is None:
                        break
                    seq_i = data_to_send.get_sequence_number(i)
                    parsed_i = {
                        "SYN": 0,
                        "ACK": 0,
                        "FIN": 0,
                        "SEQ": seq_i,
                        "DATOS": data_i.ljust(16, b'\x00')
                    }
                    self.socketUDP.sendto(self.create_segment(parsed_i), self.direccionDestino)


    def recv_using_go_back_n(self, buff_size):

        # Limpiar timer pendiente del handshake (o operación previa) y deshabilitar
        # la creación de timers en el receiver (los ACKs no necesitan timeout)
        try:
            self.socketUDP.stop_timer(timer_index=0)
        except AttributeError:
            pass
        self.socketUDP.settimeout(0)

        if self.in_mensaje == 0:
            while True:
                if self.msg_perdido is not None:
                    parsed_mensaje = self.msg_perdido
                    self.msg_perdido = None
                else:
                    mensaje, _ = self.socketUDP.recvfrom(1024)
                    parsed_mensaje = self.parse_segment(mensaje)

                if parsed_mensaje["SEQ"] == self.seq:
                    break

                # SEQ fuera de orden: ACK acumulativo del último SEQ esperado
                parsed_duplicado = {
                    "SYN": 0,
                    "ACK": 1,
                    "FIN": 0,
                    "SEQ": self.seq,
                    "DATOS": b''
                }
                mensaje_duplicado = self.create_segment(parsed_duplicado)
                self.socketUDP.sendto(mensaje_duplicado, self.direccionDestino)

            # Procesar el segmento del largo
            datos = parsed_mensaje["DATOS"].rstrip(b'\x00')
            byte_length = len(datos)
            int_length = int(datos.decode("utf-8"))

            self.return_length = int_length
            self.recibido_total = 0
            self.buffer = b''
            self.seq = parsed_mensaje["SEQ"] + byte_length

            parsed_ack = {
                "SYN": 0,
                "ACK": 1,
                "FIN": 0,
                "SEQ": self.seq,
                "DATOS": b''
            }
            mensaje_ack = self.create_segment(parsed_ack)
            self.socketUDP.sendto(mensaje_ack, self.direccionDestino)
            self.in_mensaje = 1

        while len(self.buffer) < buff_size and self.recibido_total < self.return_length:

            mensaje, _ = self.socketUDP.recvfrom(1024)
            parsed_mensaje = self.parse_segment(mensaje)

            if parsed_mensaje["SEQ"] == self.seq:
                bytes_restantes = self.return_length - self.recibido_total
                particion = min(16, bytes_restantes)
                self.buffer += parsed_mensaje["DATOS"][:particion]
                self.recibido_total += particion
                self.seq += particion

                parsed_ack = {
                    "SYN": 0,
                    "ACK": 1,
                    "FIN": 0,
                    "SEQ": self.seq,
                    "DATOS": b''
                }
                mensaje_ack = self.create_segment(parsed_ack)
                self.socketUDP.sendto(mensaje_ack, self.direccionDestino)

            else:
                parsed_duplicado = {
                    "SYN": 0,
                    "ACK": 1,
                    "FIN": 0,
                    "SEQ": self.seq,
                    "DATOS": b''
                }
                mensaje_duplicado = self.create_segment(parsed_duplicado)
                self.socketUDP.sendto(mensaje_duplicado, self.direccionDestino)

        msg_buffer = self.buffer[:buff_size]
        self.buffer = self.buffer[buff_size:]

        if self.recibido_total >= self.return_length and len(self.buffer) == 0:
            self.in_mensaje = 0

        return msg_buffer


