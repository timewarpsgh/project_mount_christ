# import from dir
import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')

from login_pb2 import *

from opcodes import OpCodeType


class PacketHandler:

    def __init__(self, session):
        self.session = session

    def handle_packet(self, packet):
        packet_name = type(packet).__name__
        getattr(self, f'_handle_{packet_name}')(packet)

    def _handle_Login(self, login):
        login_res = LoginRes()
        login_res.login_res_type = LoginRes.LoginResType.OK
        self.session.send(login_res)

    def _handle_NewAccount(self, new_account):
        new_account_res = NewAccountRes()
        new_account_res.new_account_res_type = NewAccountRes.NewAccountResType.OK
        self.session.send(new_account_res)

    def _handle_NewRole(self, new_role):
        new_role_res = NewRoleRes()
        new_role_res.new_role_res_type = NewRoleRes.NewRoleResType.OK
        self.session.send(new_role_res)