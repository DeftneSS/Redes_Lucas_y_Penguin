import socket
import sys
import socketTCP

if __name__ == "__main__":
    debug = "--debug" in sys.argv or "-d" in sys.argv

    # SERVER
    server_socketTCP = socketTCP.SocketTCP()
    server_socketTCP.set_debug(debug)
    print("a")
    server_socketTCP.bind(("localhost", 1234))
    print("b")
    connection_socketTCP, new_address = server_socketTCP.accept()
    print("c")

    # test 1
    buff_size = 16
    full_message = connection_socketTCP.recv(buff_size, mode="go_back_n")
    print("Test 1 received:", full_message)
    if full_message == "Mensje de len=16".encode(): print("Test 1: Passed")
    else: print("Test 1: Failed")

    # test 2
    buff_size = 19
    full_message = connection_socketTCP.recv(buff_size, mode="go_back_n")
    print("Test 2 received:", full_message)
    if full_message == "Mensaje de largo 19".encode(): print("Test 2: Passed")
    else: print("Test 2: Failed")

    # test 3
    buff_size = 14
    message_part_1 = connection_socketTCP.recv(buff_size, mode="go_back_n")
    message_part_2 = connection_socketTCP.recv(buff_size, mode="go_back_n")
    print("Test 3 received:", message_part_1 + message_part_2)
    if (message_part_1 + message_part_2) == "Mensaje de largo 19".encode(): print("Test 3: Passed")
    else: print("Test 3: Failed")

    #close
    server_socketTCP.close()
    print("Cerrado con éxito")