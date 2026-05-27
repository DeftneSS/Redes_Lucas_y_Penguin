import socket
import sys
import socketTCP

if __name__ == "__main__":
    debug = "--debug" in sys.argv or "-d" in sys.argv

    # CLIENT
    client_socketTCP = socketTCP.SocketTCP()
    client_socketTCP.set_debug(debug)
    print("a")
    client_socketTCP.connect(("localhost", 1234))
    print("b")
    # test 1
    message = "Mensje de len=16".encode()
    client_socketTCP.send(message, mode="go_back_n")
    print("aa")
    # test 2
    message = "Mensaje de largo 19".encode()
    client_socketTCP.send(message, mode="go_back_n")
    print("bb")
    # test 3
    message = "Mensaje de largo 19".encode()
    client_socketTCP.send(message, mode="go_back_n")
    print("cc")

    #close
    client_socketTCP.recv_close()
    print("Cerrado con éxito")

    try:
        client_socketTCP.send("Mensaje después de cerrar".encode(), mode="go_back_n")
    except Exception as e:
        print("Error al enviar después de cerrar:", e)