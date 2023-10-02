import socket

import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')

from login_pb2 import Login


def main():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 12345))
    server_socket.listen(1)

    print("Waiting for a connection...")
    connection, address = server_socket.accept()
    print("Connected by", address)

    data = connection.recv(1024)


    print(data)
    opcode_bytes = data[:2]
    print(f'opcode_bytes: {opcode_bytes}')
    obj_len_bytes = data[2:4]
    print(f'obj_len_bytes: {obj_len_bytes}')
    obj_bytes = data[4:]

    print(f'obj_bytes: {obj_bytes}')
    login2 = Login()
    login2.ParseFromString(obj_bytes)
    print(login2.account)
    print(login2.password)


    connection.sendall(b"Hello, you are connected to the server!")

    connection.close()
    server_socket.close()


if __name__ == '__main__':
    main()