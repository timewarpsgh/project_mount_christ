import pygame
import pygame_gui
from functools import partial
import json
import traceback
import numpy as np

# import from dir
import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared')

from login_pb2 import *

from my_ui_elements import MyMsgWindow, MyMenuWindow
from dialogs.create_role_dialog import CreateRoleDialog
from dialogs.options_dialog import OptionsDialog
from dialogs.chat_dialog import ChatDialog
from model import Model, Role, ShipMgr, MateMgr, DiscoveryMgr
import model
from graphics import YELLOW
from asset_mgr import sAssetMgr
from object_mgr import sObjectMgr
import constants as c


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
            if 1 in [role.id for role in get_roles_in_world_res.roles]:
                self.__enter_world(1)
            elif 2 in [role.id for role in get_roles_in_world_res.roles]:
                self.__enter_world(2)

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

    def __add_mate_to_mate_mgr(self, prot_mate):
        model_role = self.client.game.graphics.model.role

        model_mate = model.Mate(
            id=prot_mate.id,
            role_id=prot_mate.role_id,

            name=prot_mate.name,
            img_id=prot_mate.img_id,
            nation=prot_mate.nation,

            lv=prot_mate.lv,
            points=prot_mate.points,
            assigned_duty=prot_mate.assigned_duty,
            ship_id=prot_mate.ship_id,

            leadership=prot_mate.leadership,

            navigation=prot_mate.navigation,
            accounting=prot_mate.accounting,
            battle=prot_mate.battle,

            talent_in_navigation=prot_mate.talent_in_navigation,
            talent_in_accounting=prot_mate.talent_in_accounting,
            talent_in_battle=prot_mate.talent_in_battle,
        )

        model_role.mate_mgr.add_mate(model_mate)

    def __add_ship_to_ship_mgr(self, prot_ship):
        model_role = self.client.game.graphics.model.role

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

        model_role.ship_mgr.add_ship(model_ship)


    def __get_matrix_from_64_int32s(self, role):
        matrix = None

        for my_int in role.seen_grids_64_int32s:

            # int to 32 bits
            bin_str = bin(my_int)
            bin_str = bin_str[2:]
            bin_str = '0' * (32 - len(bin_str)) + bin_str

            # turn to a list of ints
            list_of_ints = [int(x) for x in bin_str]
            row = np.array(list_of_ints)
            col = row.reshape(c.SEEN_GRIDS_ROWS, 1)

            if matrix is not None:
                # add one col to the right
                matrix = np.hstack((matrix, col))
            else:
                matrix = col

        return matrix


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

            # init chat dialog
            self.client.game.gui.chat_dialog = ChatDialog(self.client.game.gui.mgr, self.client)

            # ini role
            self.client.game.graphics.model.role = Role(
                id=role.id,
                name=role.name,
                x=role.x,
                y=role.y,
                money=role.money,
            )
            model_role = self.client.game.graphics.model.role
            model_role.ship_mgr = ShipMgr(model_role)
            model_role.mate_mgr = MateMgr(model_role)
            model_role.discovery_mgr = DiscoveryMgr()

            self.client.game.graphics.sp_role.move_to(role.x, role.y)
            self.client.game.graphics.sp_role_name.move_to(role.x, role.y)
            self.client.game.graphics.sp_role_name.change_img(self.client.game.graphics.font.render(role.name, True, YELLOW))


            # init ships
            for prot_ship in role.ships:
                print(f'added ship {prot_ship.id} ######## ')
                self.__add_ship_to_ship_mgr(prot_ship)

            # init mates
            for prot_mate in role.mates:
                print(f'added mate {prot_mate.id} ######## ')
                self.__add_mate_to_mate_mgr(prot_mate)

            # init discoveries
            if role.discovery_ids_json_str:
                discovery_ids = json.loads(role.discovery_ids_json_str)
            else:
                discovery_ids = []
            for discovery_id in discovery_ids:
                model_role.discovery_mgr.add(discovery_id)

            # init seen grids
            model_role.seen_grids = self.__get_matrix_from_64_int32s(role)

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
        self.client.game.gui.options_dialog.show_available_cargos_menu(get_available_cargos_res)

    async def handle_RoleMoved(self, role_moved):
        print('role id', role_moved.id)
        print('my id', self.client.game.graphics.model.role.id)

        if role_moved.id == self.client.game.graphics.model.role.id:

            print('you moved!!')

            role_model = self.client.game.graphics.model.role
            role_model.x = role_moved.x
            role_model.y = role_moved.y

            self.client.game.graphics.sp_role.move_to(role_model.x, role_model.y)
            self.client.game.graphics.sp_role_name.move_to(role_model.x, role_model.y)

        else:
            print('someoneelse moved!!')

            self.client.game.graphics.move_sp_role(role_moved.id, role_moved.x, role_moved.y)

    def __get_role(self):
        return self.client.game.graphics.model.role

    async def handle_MoneyChanged(self, money_changed):
        self.__get_role().money = money_changed.money
        sAssetMgr.sounds['deal'].play()


    async def handle_ShipCargoChanged(self, ship_cargo_changed):
        ship = self.__get_role().ship_mgr.get_ship(ship_cargo_changed.ship_id)
        ship.add_cargo(ship_cargo_changed.cargo_id, ship_cargo_changed.cnt)

    def __get_options_dialog(self):
        return self.client.game.gui.options_dialog

    async def handle_CargoToSellInShip(self, cargo_to_sell_in_ship):
        self.__get_options_dialog().show_cargo_to_sell_in_ship_menu(cargo_to_sell_in_ship)

    async def handle_PopSomeMenus(self, pop_some_menus):
        self.__get_options_dialog().pop_some_menus(pop_some_menus.cnt)

    async def handle_GotChat(self, got_chat):
        self.client.game.gui.chat_dialog.add_chat(
            chat_type=got_chat.chat_type,
            origin_name=got_chat.origin_name,
            text=got_chat.text)

    async def handle_Discovered(self, discovered):
        self.__get_role().discovery_mgr.add(discovered.village_id)
        # play sound
        sAssetMgr.sounds['discover'].play()

    async def handle_MapChanged(self, map_changed):
        role = self.__get_role()

        if map_changed.role_id == role.id:
            role.map_id = map_changed.map_id
            role.x = map_changed.x
            role.y = map_changed.y

            if role.map_id == 0:
                self.client.game.graphics.change_background_sp_to_sea()
            else:
                port = sObjectMgr.get_port(role.map_id)
                print(f'entered port {port.name}')
                self.client.game.graphics.change_background_sp_to_port()


    async def handle_OpenedGrid(self, opened_grid):
        grid_x = opened_grid.grid_x
        grid_y = opened_grid.grid_y
        self.__get_role().seen_grids[grid_x][grid_y] = 1
        print(f'opened grid!!!!! {grid_x} {grid_y}')


    async def handle_EnteredBattleWithNpc(self, entered_battle_with_npc):
        print(f'entered battle with npc {entered_battle_with_npc.npc_id}')


        self.__get_role().battle_npc_id = entered_battle_with_npc.npc_id

        self.client.game.graphics.change_background_sp_to_battle_ground()

    async def handle_EscapedNpcBattle(self, escaped_npc_battle):

        self.__get_role().battle_npc_id = None
        self.client.game.graphics.change_background_sp_to_sea()

    def __proto_ship_2_model_ship(self, ship):
        model_ship = model.Ship(
            id=ship.id,
            role_id=ship.role_id,
            name=ship.name,

            ship_template_id=ship.ship_template_id,
            material_type=ship.material_type,
            now_durability=ship.now_durability,
            max_durability=ship.max_durability,
            tacking=ship.tacking,
            power=ship.power,
            capacity=ship.capacity,
            now_crew=ship.now_crew,
            min_crew=ship.min_crew,
            max_crew=ship.max_crew,
            now_guns=ship.now_guns,
            type_of_guns=ship.type_of_guns,
            max_guns=ship.max_guns,
            water=ship.water,
            food=ship.food,
            material=ship.material,
            cannon=ship.cannon,
            cargo_cnt=ship.cargo_cnt,
            cargo_id=ship.cargo_id,
            captain=ship.captain,
            accountant=ship.accountant,
            first_mate=ship.first_mate,
            chief_navigator=ship.chief_navigator
        )

        return model_ship

    async def handle_YouWonNpcBattle(self, you_won_npc_battle):
        for ship in you_won_npc_battle.ships:
            model_ship = self.__proto_ship_2_model_ship(ship)
            self.__get_role().ship_mgr.add_ship(model_ship)
            print(f'you won ship {ship.name}')


    async def handle_ShipRemoved(self, ship_removed):
        self.__get_role().ship_mgr.rm_ship(ship_removed.id)

    async def handle_ShipsToBuy(self, ships_to_buy):
        print('ships to buy')
        # get options_dialog
        options_dialog = self.__get_options_dialog()
        options_dialog.show_ships_to_buy_menu(ships_to_buy)

    async def handle_GotNewShip(self, got_new_ship):
        print('got new ship')
        model_ship = self.__proto_ship_2_model_ship(got_new_ship.ship)
        self.__get_role().ship_mgr.add_ship(model_ship)

    def __get_graphics(self):
        return self.client.game.graphics

    async def handle_EnteredBattleWithRole(self, entered_battle_with_role):
        self.__get_role().battle_role_id = entered_battle_with_role.role_id

        self.__get_graphics().change_background_sp_to_battle_ground()

    async def handle_EscapedRoleBattle(self, escaped_role_battle):
        self.__get_role().battle_role_id = None
        self.__get_role().battle_timer = None
        self.__get_graphics().change_background_sp_to_sea()

    async def handle_BattleTimerStarted(self, battle_timer_started):
        print('battle_timer_started')
        print(battle_timer_started.battle_timer)
        print(battle_timer_started.role_id)

        self.__get_role().battle_timer = battle_timer_started.battle_timer
        self.__get_role().is_battle_timer_mine = battle_timer_started.role_id == self.__get_role().id

