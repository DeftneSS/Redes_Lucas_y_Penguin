import socket
import socketTCP

if __name__ == "__main__":
    # CLIENT
    client_socketTCP = socketTCP.SocketTCP()
    print("a")
    client_socketTCP.connect(("localhost", 1234))
    print("b")
    # test 1
    message = "Mensje de len=16".encode()
    client_socketTCP.send(message)
    print("aa")
    # test 2
    message = "Mensaje de largo 19".encode()
    client_socketTCP.send(message)
    print("bb")
    # test 3
    message = "Mensaje de largo 19".encode()
    client_socketTCP.send(message)
    print("cc")

    #close
    client_socketTCP.recv_close()
    print("Cerrado con éxito")

    try:
        client_socketTCP.send("Mensaje después de cerrar".encode())
    except Exception as e:
        print("Error al enviar después de cerrar:", e)