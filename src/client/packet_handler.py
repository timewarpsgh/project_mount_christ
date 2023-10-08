import pygame
import pygame_gui
from functools import partial

# import from dir
import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')

from login_pb2 import *

from my_ui_elements import MyMsgWindow, MyMenuWindow


class PacketHandler:
    """client"""

    def __init__(self, client):
        self.client = client

    async def handle_packet(self, packet):
        packet_name = type(packet).__name__
        print(f'{packet_name=}')
        await getattr(self, f'handle_{packet_name}')(packet)
        print()

    async def handle_NewAccountRes(self, new_account_res):
        if new_account_res.new_account_res_type == NewAccountRes.NewAccountResType.OK:
            MyMsgWindow(msg='new account created!', mgr=self.client.game.gui.mgr)
        else:
            MyMsgWindow(msg='account name exists!', mgr=self.client.game.gui.mgr)

    async def handle_LoginRes(self, login_res):
        if login_res.login_res_type == LoginRes.LoginResType.OK:
            MyMsgWindow(msg='login OK!', mgr=self.client.game.gui.mgr)

            get_worlds = GetWorlds()
            get_worlds.any_str = '1'
            self.client.send(get_worlds)

        else:
            MyMsgWindow(msg='account or password not right!', mgr=self.client.game.gui.mgr)

    def func(self, world):
        print(f'deal with {world}')
        MyMsgWindow(msg=world, mgr=self.client.game.gui.mgr)

    async def handle_GetWorldsRes(self, get_worlds_res):
        option_2_callback = {world: partial(self.func, world)
                             for world in get_worlds_res.worlds}

        menu = MyMenuWindow(
            title='choose world',
            option_2_callback=option_2_callback,
            mgr=self.client.game.gui.mgr
        )

    async def handle_NewRoleRes(self, new_role_res):
        print(f'handle new_role_res')


