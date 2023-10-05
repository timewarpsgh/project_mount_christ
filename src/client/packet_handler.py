# import from dir
import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')

from login_pb2 import *


class PacketHandler:
    """client"""

    def __init__(self, session):
        self.session = session

    def handle_packet(self, packet):
        packet_name = type(packet).__name__
        getattr(self, f'_handle_{packet_name}')(packet)
        print()

    def _handle_NewAccountRes(self, new_account_res):
        print(f'handle new_account_res')
        print(new_account_res.new_account_res_type)
        if new_account_res.new_account_res_type == NewAccountRes.NewAccountResType.OK:
            print(f'new account OK!!!')

    def _handle_LoginRes(self, login_res):
        print(f'handle login_res')

    def _handle_NewRoleRes(self, new_role_res):
        print(f'handle new_role_res')