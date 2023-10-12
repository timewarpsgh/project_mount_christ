import pygame
import pygame_gui
from functools import partial

# import from dir
import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')

from login_pb2 import *

from my_ui_elements import MyMsgWindow, MyMenuWindow
from dialogs.create_role_dialog import CreateRoleDialog
from model import Model, Role


class PacketHandler:
    """client"""

    def __init__(self, client):
        self.client = client
        self.world_id = None
        self.is_in_game = False

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

        self.world_id = world_id

    async def handle_GetWorldsRes(self, get_worlds_res):
        option_2_callback = {world.name: partial(self.__get_roles_in_world, world.id)
                             for world in get_worlds_res.worlds}

        menu = MyMenuWindow(
            title='choose world',
            option_2_callback=option_2_callback,
            mgr=self.client.game.gui.mgr
        )

    def __enter_world(self, role_id):
        enter_world = EnterWorld()
        enter_world.role_id = role_id
        self.client.send(enter_world)

    def __make_create_role_dialog(self):
        CreateRoleDialog(self.client.game.gui.mgr, self.client, self.world_id)

    async def handle_GetRolesInWorldRes(self, get_roles_in_world_res):
        option_2_callback = {role.name: partial(self.__enter_world, role.id)
                             for role in get_roles_in_world_res.roles}

        option_2_callback['create_role'] = partial(self.__make_create_role_dialog)

        menu = MyMenuWindow(
            title='choose role',
            option_2_callback=option_2_callback,
            mgr=self.client.game.gui.mgr
        )

    async def handle_NewRoleRes(self, new_role_res):
        if new_role_res.new_role_res_type == NewRoleRes.NewRoleResType.OK:
            print(f'new role created!')
            MyMsgWindow(
                msg='new role created!',
                mgr=self.client.game.gui.mgr
            )
        else:
            MyMsgWindow(
                msg='name exits!',
                mgr=self.client.game.gui.mgr
            )

    async def handle_EnterWorldRes(self, enter_world_res):
        if enter_world_res.is_ok:
            role = enter_world_res.role_entered

            MyMsgWindow(
                msg=f'{role.name} entered world! {role.map_id=}',
                mgr=self.client.game.gui.mgr
            )

            self.client.game.gui.mgr.clear_and_reset()

            self.client.game.graphics.model.role = Role(
                name=role.name,
                x=role.x,
                y=role.y,
            )

            self.client.game.graphics.sp_role.move_to(role.x * 100, role.y * 100)

            self.is_in_game = True

        else:
            MyMsgWindow(
                msg='failed to enter world!',
                mgr=self.client.game.gui.mgr
            )
