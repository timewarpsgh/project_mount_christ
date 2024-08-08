import pygame
import pygame_gui
from functools import partial
import traceback

# import from dir
import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')

from login_pb2 import *

from my_ui_elements import MyMsgWindow, MyMenuWindow
from dialogs.create_role_dialog import CreateRoleDialog
from dialogs.options_dialog import OptionsDialog
from model import Model, Role, ShipMgr
import model
from graphics import YELLOW


BYPASS_LOGIN = True


class PacketHandler:
    """client"""

    def __init__(self, client):
        self.client = client
        self.world_id = None
        self.is_in_game = False

    async def handle_packet(self, packet):
        packet_name = type(packet).__name__
        print(f'{packet_name=}')
        try:
            await getattr(self, f'handle_{packet_name}')(packet)
        except Exception as e:
            print(f'{packet_name} error: {e}')
            traceback.print_exc()
        else:
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

        # bypass choose world
        if BYPASS_LOGIN:
            self.__get_roles_in_world(1)


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

        # bypass choose role
        if BYPASS_LOGIN:
            self.__enter_world(1)

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

    def __add_ship_to_ship_mgr(self, prot_ship):
        role = self.client.game.graphics.model.role
        role.ship_mgr = ShipMgr(role)

        model_ship = model.Ship(
            id=prot_ship.id,
            role_id=prot_ship.role_id,

            name=prot_ship.name,
            ship_template_id=prot_ship.ship_template_id,

            material_type=prot_ship.material_type,

            now_durability=prot_ship.now_durability,
            max_durability=prot_ship.max_durability,

            tacking=prot_ship.tacking,
            power=prot_ship.power,

            capacity=prot_ship.capacity,


            now_crew=prot_ship.now_crew,
            min_crew=prot_ship.min_crew,
            max_crew=prot_ship.max_crew,

            now_guns=prot_ship.now_guns,
            type_of_guns=prot_ship.type_of_guns,
            max_guns=prot_ship.max_guns,

            water=prot_ship.water,
            food=prot_ship.food,
            material=prot_ship.material,
            cannon=prot_ship.cannon,

            cargo_cnt=prot_ship.cargo_cnt,
            cargo_id=prot_ship.cargo_id,

            captain=prot_ship.captain,
            accountant=prot_ship.accountant,
            first_mate=prot_ship.first_mate,
            chief_navigator=prot_ship.chief_navigator,
        )


        role.ship_mgr.add_ship(model_ship)


    async def handle_EnterWorldRes(self, enter_world_res):
        if enter_world_res.is_ok:
            role = enter_world_res.role_entered

            MyMsgWindow(
                msg=f'{role.name} entered world! {role.map_id=}',
                mgr=self.client.game.gui.mgr
            )

            # clear gui
            self.client.game.gui.mgr.clear_and_reset()

            # init options dialog
            self.client.game.gui.options_dialog = OptionsDialog(self.client.game.gui.mgr, self.client)

            # ini role
            self.client.game.graphics.model.role = Role(
                id=role.id,
                name=role.name,
                x=role.x,
                y=role.y,
            )

            self.client.game.graphics.sp_role.move_to(role.x * 100, role.y * 100)
            self.client.game.graphics.sp_role_name.move_to(role.x * 100, role.y * 100)
            self.client.game.graphics.sp_role_name.change_img(self.client.game.graphics.font.render(role.name, True, YELLOW))


            # init ships
            for prot_ship in role.ships:
                self.__add_ship_to_ship_mgr(prot_ship)


            print(self.client.game.graphics.model.role.ship_mgr.get_ship(1).name)

            self.is_in_game = True

        else:
            MyMsgWindow(
                msg='failed to enter world!',
                mgr=self.client.game.gui.mgr
            )

    async def handle_RoleAppeared(self, role_appeared):
        print(f'!!!!get packet role_appeared for {role_appeared.name}')
        role = Role(
            id=role_appeared.id,
            name=role_appeared.name,
            x=role_appeared.x,
            y=role_appeared.y,
        )

        self.client.game.graphics.model.id_2_role[role_appeared.id] = role
        self.client.game.graphics.add_sp_role(role)

    async def handle_RoleDisappeared(self, role_disappeared):
        del self.client.game.graphics.model.id_2_role[role_disappeared.id]
        self.client.game.graphics.rm_sp_role(role_disappeared.id)

    async def handle_GetAvailableCargosRes(self, get_available_cargos_res):
        print(get_available_cargos_res)

        option_2_callback = {f'{cargo.name} {cargo.price}': ''
                             for cargo in get_available_cargos_res.available_cargos}

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.client.game.gui.mgr
        )

    async def handle_RoleMoved(self, role_moved):
        print('role id', role_moved.id)
        print('my id', self.client.game.graphics.model.role.id)

        if role_moved.id == self.client.game.graphics.model.role.id:

            print('you moved!!')

            role_model = self.client.game.graphics.model.role
            role_model.x = role_moved.x + 300
            role_model.y = role_moved.y + 150

            self.client.game.graphics.sp_role.move_to(role_model.x, role_model.y)
            self.client.game.graphics.sp_role_name.move_to(role_model.x, role_model.y)

        else:
            print('someoneelse moved!!')

            self.client.game.graphics.move_sp_role(role_moved.id, role_moved.x + 300, role_moved.y + 150)