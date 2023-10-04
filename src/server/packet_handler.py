# import from dir
import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')

from login_pb2 import \
    Login, LoginRes, \
    NewAccount, NewAccountRes

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
        login_res = LoginRes()
        login_res.login_res_type = LoginRes.LoginResType.OK
        self.session.send(login_res)

    def __handle_new_account(self, new_account):
        new_account_res = NewAccountRes()
        new_account_res.new_account_res_type = NewAccountRes.NewAccountResType.OK
        self.session.send(new_account_res)