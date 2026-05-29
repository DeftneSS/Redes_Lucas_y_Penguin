import socket
import sys
import socketTCP

if __name__ == "__main__":
    debug = "--debug" in sys.argv or "-d" in sys.argv

    # CLIENT
    client_socketTCP = socketTCP.SocketTCP()
    client_socketTCP.set_debug(debug)
    client_socketTCP.connect(("localhost", 1234))
    # test 1
    message = "Mensje de len=16".encode()
    client_socketTCP.send(message, mode="go_back_n")
    # test 2
    message = "Mensaje de largo 19".encode()
    client_socketTCP.send(message, mode="go_back_n")
    # test 3
    message = "Mensaje de largo 19".encode()
    client_socketTCP.send(message, mode="go_back_n")

    #close
    client_socketTCP.recv_close()
    print("Cerrado con éxito")