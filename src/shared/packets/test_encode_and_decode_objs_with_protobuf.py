import login_pb2

# encode
login = login_pb2.Login()

login.account = '1234'
login.password = '222'
print(login.account)
print(login.password)

bytes = login.SerializeToString()
print(bytes)

# decode
login2 = login_pb2.Login()

login2.ParseFromString(bytes)
print(login2.account)
print(login2.password)