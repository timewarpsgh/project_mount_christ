import socket

import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')


from login_pb2 import Login
from opcodes import OpCodeType

class Packet:

    def __init__(self, probuf_obj):
        two_bytes_for_opcode = OpCodeType.C_LOGIN.value.to_bytes(2)
        bytes_for_obj = probuf_obj.SerializeToString()
        two_bytes_for_obj_len = len(bytes_for_obj).to_bytes(2)
        self.bytes = two_bytes_for_opcode + two_bytes_for_obj_len + bytes_for_obj
        print(f'packet bytes: {self.bytes}')


def main():

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 12345))

    # encode object
    login = Login()

    login.account = '1234哈哈'
    login.password = '222'
    print(login.account)
    print(login.password)

    bytes = login.SerializeToString()
    print(bytes)
    print(f'len fo bytes: {len(bytes)}')

    packet = Packet(login)

    client_socket.sendall(packet.bytes)

    data = client_socket.recv(1024)
    print("Received from server: " + data.decode())

    client_socket.close()


if __name__ == '__main__':
    main()



