# import from dir
import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')

from login_pb2 import *


class PacketHandler:
    """client"""

    def __init__(self, session):
        self.session = session

    async def handle_packet(self, packet):
        packet_name = type(packet).__name__
        print(f'{packet_name=}')
        await getattr(self, f'handle_{packet_name}')(packet)
        print()

    async def handle_NewAccountRes(self, new_account_res):
        print(f'handle new_account_res')
        print(new_account_res.new_account_res_type)
        if new_account_res.new_account_res_type == NewAccountRes.NewAccountResType.OK:
            print(f'new account OK!!!')
        else:
            print(f'account name exits!!!')

    async def handle_LoginRes(self, login_res):
        print(f'handle login_res')

    async def handle_NewRoleRes(self, new_role_res):
        print(f'handle new_role_res')