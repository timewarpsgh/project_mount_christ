# import from dir
import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')

from login_pb2 import Login, NewAccount
from opcodes import OpCodeType


class PacketHandler:

    def __init__(self, session):
        self.session = session

    def handle_packet(self, packet):

        if isinstance(packet, Login):
            self.__handle_login(packet)
        elif isinstance(packet, NewAccount):
            self.__handle_new_account(packet)

    def __handle_login(self, login):
        print(f'__handle_login')

    def __handle_new_account(self, new_account):
        print(f'__handle_new_account')

        login = Login()
        login.account = '111'
        login.password = '222'
        self.session.send(login)