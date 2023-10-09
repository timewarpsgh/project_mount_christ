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
            get_worlds = GetWorlds()
            self.client.send(get_worlds)
        else:
            MyMsgWindow(msg='account or password not right!', mgr=self.client.game.gui.mgr)

    def __get_roles_in_world(self, world_id):
        get_roles_in_world = GetRolesInWorld()
        get_roles_in_world.world_id = world_id
        self.client.send(get_roles_in_world)

    async def handle_GetWorldsRes(self, get_worlds_res):
        option_2_callback = {world.name: partial(self.__get_roles_in_world, world.id)
                             for world in get_worlds_res.worlds}

        menu = MyMenuWindow(
            title='choose world',
            option_2_callback=option_2_callback,
            mgr=self.client.game.gui.mgr
        )

    async def handle_GetRolesInWorldRes(self, get_roles_in_world_res):
        option_2_callback = {role.name: 1
                             for role in get_roles_in_world_res.roles}

        menu = MyMenuWindow(
            title='choose role',
            option_2_callback=option_2_callback,
            mgr=self.client.game.gui.mgr
        )

    async def handle_NewRoleRes(self, new_role_res):
        print(f'handle new_role_res')


