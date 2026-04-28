import socket
import json



def parse_HTTP_message(http_message):

    msg_head = http_message.split(b'\r\n\r\n')
    head_lines = msg_head[0].split(b'\r\n')

    start_line = head_lines[0]
    body = msg_head[1] if len(msg_head) > 1 else b""
    parsed_message = {
        "start_line": start_line,
        "body": body
    }
    for header in head_lines[1:]:
        key, value = header.split(b':',1)
        parsed_message[key.strip().decode()] = value.strip()


    return parsed_message


def create_HTTP_message(parsed_message):
    
    head = b''
    head+= parsed_message["start_line"] + b'\r\n'

    for key, value in parsed_message.items():
        if key not in ("start_line", "body"):
            head += f"{key}: ".encode('utf-8') + value + b'\r\n'
    
    head += b'\r\n'
    body = parsed_message["body"]
    full_message = head + body
    
    return full_message

if __name__ == "__main__":
    buff_size = 50
    new_socket_address = ('10.42.118.126',8000)
    archivo_json= "forbidden.json"
    with open(archivo_json) as file:
        data = json.load(file)
        blocked_web = data["blocked"]
        forbidden_words = data["forbidden_words"]
    whitelist = ["cc4303.bachmann.cl", "10.42.118.126:8000"]    

print('Creando socket- Servidor')

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


server_socket.bind(new_socket_address)

server_socket.listen(1)

print('...Esperando cliente')

while True:
    new_socket, new_socket_address = server_socket.accept()
    recv_msg_client = new_socket.recv(buff_size)

    full_msg_client = recv_msg_client
    while b"\r\n\r\n" not in full_msg_client:
        recv_msg_client = new_socket.recv(buff_size)
        full_msg_client += recv_msg_client

    parsed_message = parse_HTTP_message(full_msg_client)
    client_body = parsed_message["body"]
    if len(client_body)>0:
        client_length = int(parsed_message.get("Content-Length").decode())
        while len(client_body) < client_length:
            rest_body_client = new_socket.recv(buff_size)
            client_body += rest_body_client
        parsed_message["body"] = client_body
    
    direccion_destino= parsed_message["Host"].decode()
    if direccion_destino not in whitelist:
        new_socket.close()
        continue
    print(direccion_destino)
    address = (direccion_destino,80)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    method, URI_servidor, version = parsed_message["start_line"].split()
    print(URI_servidor.decode())
    
    if URI_servidor.decode() in blocked_web:
        client_socket.connect(address)
        #Cambiar IP de src
        html = b"""
        <!DOCTYPE html>
        <html>
        <body>
            <img src="http://10.42.118.126:8000/403.jpg"> 
        </body>
        </html>
        """
        response = b"HTTP/1.1 403 Forbidden\r\n"
        response += b"Content-Type: text/html\r\n"
        response += f"Content-Length: {len(html)}\r\n".encode()
        response += b"\r\n"
        response += html
        print("llego el html")
        new_socket.send(response)
    #Cambiar por IP propia
    elif URI_servidor.decode() == "http://10.42.118.126:8000/403.jpg":
        img_bytes = open("403.jpg", "rb").read()

        response = b"HTTP/1.1 200 OK\r\n"
        response += b"Content-Type: image/jpeg\r\n"
        response += f"Content-Length: {len(img_bytes)}\r\n".encode()
        response += b"\r\n"
        response += img_bytes

        new_socket.send(response)
        print("si llego la imagen")
        client_socket.close()
        new_socket.close()
        
    else:
        client_socket.connect(address)
        parsed_message["X-ElQuePregunta"] = b"Agustin y Lucas"
        http_message = create_HTTP_message(parsed_message)
        client_socket.send(http_message)
        print("... Mensaje enviado")
        
        server_response = client_socket.recv(buff_size)
        full_response = server_response
        while b"\r\n\r\n" not in full_response:
            server_response = client_socket.recv(buff_size)
            full_response += server_response
        print("... Mensaje recibido del servidor")
        server_response_parsed = parse_HTTP_message(full_response)
        server_body = server_response_parsed["body"]
        server_length = int(server_response_parsed["Content-Length"].decode())
        while len(server_body) < server_length:
            rest_body = client_socket.recv(buff_size)
            server_body+=rest_body
        
        server_response_parsed["body"] = server_body
        server_body = server_response_parsed["body"].decode()
        for item in forbidden_words:
            for key, value in item.items():
                server_body = server_body.replace(key, value)
        body_bytes = server_body.encode("utf-8")
        server_response_parsed["body"] = body_bytes
        server_response_parsed["Content-Length"] = str(len(body_bytes)).encode("utf-8")
        server_response = create_HTTP_message(server_response_parsed)
        new_socket.send(server_response)
        client_socket.close()
        new_socket.close()
