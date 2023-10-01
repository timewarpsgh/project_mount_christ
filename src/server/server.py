import socket
from login_pb2 import Login


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 12345))
server_socket.listen(1)

print("Waiting for a connection...")
connection, address = server_socket.accept()
print("Connected by", address)

data = connection.recv(1024)

login2 = Login()

login2.ParseFromString(data)
print("Received from client: ")
print(login2.account)
print(login2.password)


connection.sendall(b"Hello, you are connected to the server!")

connection.close()
server_socket.close()
