import socket
from login_pb2 import Login


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


client_socket.sendall(bytes)

data = client_socket.recv(1024)
print("Received from server: " + data.decode())

client_socket.close()



