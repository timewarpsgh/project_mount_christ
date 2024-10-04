from functools import partial
import json
import traceback
import numpy as np
import asyncio

# import from dir
import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared')

from login_pb2 import *
import login_pb2 as pb
from my_ui_elements import MyMsgWindow, MyMenuWindow
from dialogs.create_role_dialog import CreateRoleDialog
from dialogs.options_dialog import OptionsDialog
from dialogs.chat_dialog import ChatDialog
from model import Role, ShipMgr, MateMgr, DiscoveryMgr, Npc
import model
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
            elif 3 in [role.id for role in get_roles_in_world_res.roles]:
                self.__enter_world(3)

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

        model_mate = model.Mate(prot_mate)

        model_role.mate_mgr.add_mate(model_mate)

    def __add_ship_to_ship_mgr(self, prot_ship):
        model_role = self.client.game.graphics.model.role

        model_ship = model.Ship(prot_ship)

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
            # rename pack
            role = enter_world_res.role_entered

            # ini role
            self.__get_model().role = Role(
                id=role.id,
                name=role.name,
                x=role.x,
                y=role.y,
                dir=role.dir,
                money=role.money,
                items=json.loads(role.items),
                notorities=json.loads(role.notorities),

                graphics = self.client.game.graphics,
            )
            model_role = self.__get_role()
            self.__get_graphics().sp_role.role = model_role
            model_role.ship_mgr = ShipMgr(model_role)
            model_role.mate_mgr = MateMgr(model_role)
            model_role.discovery_mgr = DiscoveryMgr()

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

            # init auras
            model_role.auras = set()

            # clear gui
            self.client.game.gui.mgr.clear_and_reset()
            # init options dialog
            self.client.game.gui.options_dialog = OptionsDialog(self.client.game.gui.mgr, self.client)
            # init chat dialog
            self.client.game.gui.chat_dialog = ChatDialog(self.client.game.gui.mgr, self.client)

            # set is_in_game for client
            self.is_in_game = True

        else:
            MyMsgWindow(
                msg='failed to enter world!',
                mgr=self.client.game.gui.mgr
            )

    async def handle_RoleAppeared(self, role_appeared):
        print(f'!!!!get packet role_appeared for '
              f'{role_appeared.name}  {role_appeared.x} {role_appeared.y}')
        role = Role(
            id=role_appeared.id,
            name=role_appeared.name,
            map_id=self.__get_role().map_id,
            dir=self.__get_role().dir,
            x=role_appeared.x,
            y=role_appeared.y,
            graphics=self.client.game.graphics,
        )

        self.client.game.graphics.model.add_role(role)

        if role_appeared.id in self.client.game.graphics.id_2_sp_role:
            self.client.game.graphics.rm_sp_role(role_appeared.id)
        self.client.game.graphics.add_sp_role(role)

    async def handle_RoleDisappeared(self, role_disappeared):
        if role_disappeared.id not in self.client.game.graphics.model.id_2_role:
            return

        del self.client.game.graphics.model.id_2_role[role_disappeared.id]
        self.client.game.graphics.rm_sp_role(role_disappeared.id)

    async def handle_GetAvailableCargosRes(self, get_available_cargos_res):
        self.client.game.gui.options_dialog.show_available_cargos_menu(get_available_cargos_res)

    async def handle_RoleMoved(self, role_moved):

        # self move
        if role_moved.id == self.client.game.graphics.model.role.id:

            # update role

            role_model = self.__get_role()

            role_model.last_x = role_model.x
            role_model.last_y = role_model.y


            role_model.x = role_moved.x
            role_model.y = role_moved.y
            role_model.dir = role_moved.dir_type

            # at sea
            if role_model.map_id == 0:
                sp_role = self.__get_graphics().sp_role
                sp_role.change_img(sp_role.frames['at_sea'][role_model.dir][0])
                self.__get_graphics().move_sea_bg(role_model.x, role_model.y)

            # in port
            else:
                sp_role = self.__get_graphics().sp_role
                if sp_role.now_frame == 0:
                    sp_role.now_frame = 1
                else:
                    sp_role.now_frame = 0

                sp_role.change_img(sp_role.frames['in_port'][role_model.dir][sp_role.now_frame])
                self.__get_graphics().move_port_bg(role_model.x, role_model.y)

        # other role move
        else:
            self.__get_graphics().move_sp_role(role_moved.id, role_moved.x, role_moved.y)

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
            # update model
            role.map_id = map_changed.map_id
            role.x = map_changed.x
            role.y = map_changed.y

            # to sea
            if role.is_at_sea():
                self.__get_graphics().sp_background.stop_moving()
                self.client.game.graphics.change_background_sp_to_sea(role.x, role.y)
                self.__get_options_dialog().pop_some_menus(5)
                self.__get_graphics().remove_port_npcs()
                self.__get_graphics().remove_dynamic_port_npcs()
                self.__get_graphics().remove_sp_building_bg()

                self.__get_role().has_treated = False
                self.__get_role().has_told_story = False

            # to port
            elif role.is_in_port():
                port = sObjectMgr.get_port(role.map_id)
                print(f'entered port {port.name}')
                self.__get_graphics().add_port_npcs(role.map_id)
                self.__get_graphics().add_dynamic_port_npcs(role.map_id)
                self.client.game.graphics.change_background_sp_to_port(role.map_id, role.x, role.y)


    async def handle_OpenedGrid(self, opened_grid):
        grid_x = opened_grid.grid_x
        grid_y = opened_grid.grid_y
        self.__get_role().seen_grids[grid_x][grid_y] = 1
        print(f'opened grid!!!!! {grid_x} {grid_y}')


    async def handle_EnteredBattleWithNpc(self, entered_battle_with_npc):
        print(f'entered battle with npc {entered_battle_with_npc.npc_id}')

        npc_id = entered_battle_with_npc.npc_id
        self.__get_role().battle_npc_id = npc_id

        print(f'{npc_id=}')

        print(f' id_2_npc {self.__get_model().id_2_npc}')

        # init npc if not in model yet, add npc to model
        if npc_id not in self.__get_model().id_2_npc:
            npc = Npc(
                id=npc_id,
            )
            self.__get_model().add_npc(npc)

        enemy_npc = self.__get_model().get_npc_by_id(npc_id)
        enemy_npc.ship_mgr = ShipMgr(enemy_npc)

        ships_prots = entered_battle_with_npc.ships
        for ship_prot in ships_prots:
            ship = model.Ship(ship_prot)

            enemy_npc.ship_mgr.add_ship(ship)
            print(f'added enemy ship {ship.name}')

        self.client.game.graphics.change_background_sp_to_battle_ground()


    async def handle_EscapedNpcBattle(self, escaped_npc_battle):
        role = self.__get_role()

        role.battle_npc_id = None
        role.battle_timer = None

        self.__get_graphics().change_background_sp_to_sea(role.x, role.y)

    async def handle_YouWonNpcBattle(self, you_won_npc_battle):
        for ship in you_won_npc_battle.ships:
            model_ship = model.Ship(ship)
            self.__get_role().ship_mgr.add_ship(model_ship)
            print(f'you won ship {ship.name}')


    async def handle_ShipRemoved(self, ship_removed):
        print('ship id removed!!')
        print(ship_removed.id)
        if self.__get_role().ship_mgr.has_ship(ship_removed.id):
            self.__get_role().ship_mgr.rm_ship(ship_removed.id)
        else:
            self.__get_role().get_enemy().ship_mgr.rm_ship(ship_removed.id)

    async def handle_ShipsToBuy(self, ships_to_buy):
        print('ships to buy')
        # get options_dialog
        options_dialog = self.__get_options_dialog()
        options_dialog.show_ships_to_buy_menu(ships_to_buy)

    async def handle_GotNewShip(self, got_new_ship):
        print('got new ship')
        model_ship = model.Ship(got_new_ship.ship)
        print(f'new ship name: {model_ship.name}')
        print(model_ship)

        self.__get_role().ship_mgr.add_ship(model_ship)

        print(self.__get_role().ship_mgr.id_2_ship)

    def __get_graphics(self):
        return self.client.game.graphics

    def __get_model(self):
        return self.client.game.graphics.model

    async def handle_EnteredBattleWithRole(self, entered_battle_with_role):

        self.__get_role().is_moving = False
        self.__get_graphics().sp_background.start_time = None

        # change model
        self.__get_role().battle_role_id = entered_battle_with_role.role_id

        role = Role(
            id=entered_battle_with_role.role_id,
            name=None,
            map_id=0,
            dir=self.__get_role().dir,
            x=self.__get_role().x,
            y=self.__get_role().y,
            graphics=self.client.game.graphics,
        )
        self.__get_model().add_role(role)


        enemy_role = self.__get_model().get_role_by_id(entered_battle_with_role.role_id)
        enemy_role.ship_mgr = ShipMgr(enemy_role)

        ships_prots = entered_battle_with_role.ships
        for ship_prot in ships_prots:
            ship = model.Ship(ship_prot)

            enemy_role.ship_mgr.add_ship(ship)
            print(f'added enemy ship {ship.name}')
            print(f'{entered_battle_with_role.role_id}=')

        # change graphics
        self.__get_graphics().change_background_sp_to_battle_ground()


    async def handle_EscapedRoleBattle(self, escaped_role_battle):
        role = self.__get_role()

        role.battle_role_id = None
        role.battle_timer = None

        self.__get_graphics().change_background_sp_to_sea(role.x, role.y)

    async def handle_BattleTimerStarted(self, battle_timer_started):
        print('battle_timer_started')
        print(battle_timer_started.battle_timer)
        print(battle_timer_started.role_id)

        self.__get_role().battle_timer = battle_timer_started.battle_timer
        self.__get_role().is_battle_timer_mine = battle_timer_started.role_id == self.__get_role().id
        if self.__get_role().is_battle_timer_mine:
            self.__get_role().has_attacked = False
        else:
            self.__get_role().has_attacked = True
            self.__get_graphics().clear_marks()

    async def handle_ShipAttacked(self, ship_attacked):


        # engage
        if ship_attacked.attack_method_type == pb.AttackMethodType.ENGAGE:
            # show cannon_ball
            # show ship attacked damage
            src_id = ship_attacked.src_id
            dst_id = ship_attacked.dst_id
            dst_damage = ship_attacked.dst_damage
            src_damage = ship_attacked.src_damage

            print(f'ships engaged {src_id} {dst_id} {src_damage} {dst_damage}')

            src_ship = self.__get_model().get_ship_in_battle_by_id(src_id)
            dst_ship = self.__get_model().get_ship_in_battle_by_id(dst_id)
            my_flag_ship = self.__get_role().get_flag_ship()

            # modify model
            src_ship.now_crew -= src_damage
            dst_ship.now_crew -= dst_damage

            if src_ship.now_crew <= 0:
                src_ship.now_crew = 0

            if dst_ship.now_crew <= 0:
                dst_ship.now_crew = 0

            # show graphics
            pixels = c.BATTLE_TILE_SIZE

            src_x, src_y = src_ship.get_screen_xy(my_flag_ship)
            dst_x, dst_y = dst_ship.get_screen_xy(my_flag_ship)

            sAssetMgr.sounds['engage'].play()
            self.__get_graphics().show_engage_sign(dst_x, dst_y)
            self.__get_graphics().show_engage_sign(src_x, src_y)

            self.__get_graphics().show_damage(dst_damage, dst_x, dst_y, color=c.WHITE)
            self.__get_graphics().show_damage(src_damage, src_x, src_y, color=c.WHITE)

        # shoot
        elif ship_attacked.attack_method_type == pb.AttackMethodType.SHOOT:

            # show cannon_ball
            # show ship attacked damage
            src_id = ship_attacked.src_id
            dst_id = ship_attacked.dst_id
            dst_damage = ship_attacked.dst_damage


            src_ship = self.__get_model().get_ship_in_battle_by_id(src_id)
            dst_ship = self.__get_model().get_ship_in_battle_by_id(dst_id)
            my_flag_ship = self.__get_role().get_flag_ship()

            # modify model
            dst_ship.now_durability -= dst_damage
            if dst_ship.now_durability <= 0:
                dst_ship.now_durability = 0

            # show graphics
            pixels = c.BATTLE_TILE_SIZE
            half_ps = pixels // 2

            src_x, src_y = src_ship.get_screen_xy(my_flag_ship)
            dst_x, dst_y = dst_ship.get_screen_xy(my_flag_ship)
            self.__get_graphics().show_cannon(src_x + half_ps,
                                              src_y + half_ps,
                                              dst_x + half_ps,
                                              dst_y + half_ps)
            sAssetMgr.sounds['shoot'].play()
            await asyncio.sleep(0.6)
            self.__get_graphics().show_damage(dst_damage, dst_x, dst_y)
            sAssetMgr.sounds['explosion'].play()
            self.__get_graphics().show_explosion(dst_x, dst_y)

    async def handle_ShipMoved(self, ship_moved):
        id = ship_moved.id
        x = ship_moved.x
        y = ship_moved.y
        dir = ship_moved.dir
        steps_left = ship_moved.steps_left

        ship = self.__get_model().get_ship_in_battle_by_id(id)
        ship.x = x
        ship.y = y
        ship.dir = dir
        ship.steps_left = steps_left

    async def handle_StartedMoving(self, started_moving):
        id = started_moving.id
        src_x = started_moving.src_x
        src_y = started_moving.src_y
        dir = started_moving.dir
        speed = started_moving.speed

        if id == self.__get_role().id:
            role = self.__get_role()
            role.is_moving = True
            role.speed = speed
            role.dir = dir

            print('handling pack StartedMoving')
        else:
            role = self.__get_model().get_role_by_id(id)
            role.map_id = self.__get_role().map_id
            role.x = src_x
            role.y = src_y
            role.dir = dir
            role.is_moving = True
            role.speed = speed
            # role.move_timer = 0


    async def handle_StoppedMoving(self, stopped_moving):
        id = stopped_moving.id
        src_x = stopped_moving.src_x
        src_y = stopped_moving.src_y
        dir = stopped_moving.dir

        print(f'{id} stopped moving at {src_x} {src_y}')

        if id == self.__get_role().id:
            role = self.__get_role()
            role.stopped_moving(src_x, src_y, dir)
        else:
            role = self.__get_model().get_role_by_id(id)

            role.x = src_x
            role.y = src_y
            role.dir = dir
            role.is_moving = False

            # change sp dir
            sp_role = self.__get_graphics().get_sp_role(id)
            if self.__get_role().is_at_sea():
                sp_role.change_img(sp_role.frames['others_at_sea'][role.dir][0])
            else:
                sp_role.change_img(sp_role.frames['in_port'][role.dir][0])

            # move sp to final position
            x, y = role.get_x_y_between_roles(role, self.__get_role())
            self.__get_graphics().move_sp_role(id, x, y, role.calc_move_timer())

    async def handle_AllShipsTargetSet(self, all_ships_target_set):
        target_ship_id = all_ships_target_set.ship_id
        self.__get_role().set_all_ships_target(target_ship_id)

    async def handle_FleetInfo(self, fleet_info):
        self.__get_options_dialog().show_fleet_info(fleet_info.ships_template_ids)

    async def handle_MateInPort(self, mate_in_port):
        mate_template_id = mate_in_port.mate_template_id
        if mate_template_id:
            mate_template = sObjectMgr.get_mate_template(mate_template_id)
            print('found mate in port')
            print(mate_template.name)
            self.__get_options_dialog().show_mates_in_port_menu(mate_template)
        else:
            print('no mate in this port')
            self.__get_options_dialog().show_mates_in_port_menu()

    async def handle_HireMateRes(self, hire_mate_res):
        if hire_mate_res.is_ok:
            mate = model.Mate(hire_mate_res.mate)
            self.__get_role().mate_mgr.add_mate(mate)

            speech = f"I'm glad to join you guys!"
            self.__get_options_dialog().pop_some_menus(2)
            self.__get_options_dialog().show_mate_speech(mate, speech)
        else:
            print('failed to hire mate')

    def get_mate_mgr(self):
        return self.__get_role().mate_mgr

    async def handle_MateFired(self, mate_fired):
        mate_id = mate_fired.mate_id
        mate = self.get_mate_mgr().get_mate(mate_id)
        self.__get_options_dialog().pop_some_menus(3)
        self.__get_options_dialog().show_mate_speech(mate,
             'Farewell, captain, I will you and your crew all the best!')
        self.get_mate_mgr().rm_mate(mate_id)

    async def handle_DutyAssigned(self, duty_assigned):
        mate_id = duty_assigned.mate_id
        ship_id = duty_assigned.ship_id
        duty_type = duty_assigned.duty_type

        self.get_mate_mgr().assign_duty(mate_id, ship_id, duty_type)

        self.__get_options_dialog().pop_some_menus(3)

    def __get_chat_dialog(self):
        return self.client.game.gui.chat_dialog

    async def handle_XpEarned(self, xp_earned):
        mate_id = xp_earned.mate_id
        duty_type = xp_earned.duty_type
        amount = xp_earned.amount

        mate = self.get_mate_mgr().get_mate(mate_id)
        mate.xp_earned(duty_type, amount)
        text = f"{mate.name} earned {amount} xp in {c.INT_2_DUTY_NAME[duty_type]}"
        self.__get_chat_dialog().add_chat(pb.ChatType.SYSTEM, text)

    async def handle_LvUped(self, lv_uped):
        mate_id = lv_uped.mate_id
        duty_type = lv_uped.duty_type
        lv = lv_uped.lv
        xp = lv_uped.xp
        value = lv_uped.value

        mate = self.get_mate_mgr().get_mate(mate_id)
        mate.lv_uped(duty_type, lv, xp, value)

        # play sound lv_up
        sAssetMgr.sounds['lv_up'].play()

        # show chat
        text = f"{mate.name} lv uped to {lv} in {c.INT_2_DUTY_NAME[duty_type]}"
        self.__get_chat_dialog().add_chat(pb.ChatType.SYSTEM, text)

    async def handle_SeasonChanged(self, season_changed):
        season = season_changed.season
        wind_dir = season_changed.wind_dir
        wind_speed = season_changed.wind_speed
        current_dir = season_changed.current_dir
        current_speed = season_changed.current_speed


        self.client.game.graphics.model.season_mgr.change_season(
            season,
            wind_dir,
            wind_speed,
            current_dir,
            current_speed
        )

    async def handle_ShipRepaired(self, ship_repaired):
        ship_id = ship_repaired.ship_id
        max_durability = ship_repaired.max_durability

        ship = self.__get_role().ship_mgr.get_ship(ship_id)
        ship.max_durability = max_durability
        ship.now_durability = max_durability

        self.__get_options_dialog().building_speak(
            f"{ship.name} has been fixed. It's max_durability is now {max_durability}. "
            f"We have tried our best.")

    async def handle_ShipRenamed(self, ship_renamed):
        id = ship_renamed.id
        name = ship_renamed.name

        ship = self.__get_role().ship_mgr.get_ship(id)
        ship.name = name
        self.__get_options_dialog().pop_some_menus(2)

    async def handle_ShipCapacityChanged(self, pack):
        id = pack.id
        max_crew = pack.max_crew
        max_guns = pack.max_guns
        useful_capacity = pack.useful_capacity
        now_crew = pack.now_crew
        now_guns = pack.now_guns

        ship = self.__get_role().ship_mgr.get_ship(id)
        ship.max_crew = max_crew
        ship.max_guns = max_guns
        ship.useful_capacity = useful_capacity
        ship.now_crew = now_crew
        ship.now_guns = now_guns

        self.__get_options_dialog().pop_some_menus(2)

    async def handle_ShipWeaponChanged(self, pack):
        ship_id = pack.ship_id
        cannon_id = pack.cannon_id

        ship = self.__get_role().ship_mgr.get_ship(ship_id)
        ship.type_of_guns = cannon_id
        ship.now_guns = ship.max_guns

        self.__get_options_dialog().pop_some_menus(2)

    async def handle_CrewRecruited(self, pack):
        ship_id = pack.ship_id
        cnt = pack.cnt

        ship = self.__get_role().ship_mgr.get_ship(ship_id)
        ship.now_crew += cnt

        self.__get_options_dialog().pop_some_menus(2)

    async def handle_CrewDismissed(self, pack):
        ship_id = pack.ship_id
        cnt = pack.cnt

        ship = self.__get_role().ship_mgr.get_ship(ship_id)
        ship.now_crew -= cnt

        self.__get_options_dialog().pop_some_menus(2)

    async def handle_SupplyChanged(self, pack):
        ship_id = pack.ship_id
        supply_name = pack.supply_name
        cnt = pack.cnt

        ship = self.__get_role().ship_mgr.get_ship(ship_id)
        setattr(ship, supply_name, cnt)

        self.__get_options_dialog().pop_some_menus(2)

    async def handle_OneDayPassedAtSea(self, pack):
        days_at_sea = pack.days_at_sea
        self.__get_role().days_at_sea = days_at_sea

    async def handle_SupplyConsumed(self, pack):
        ship_id = pack.ship_id
        supply_name = pack.supply_name
        now_cnt = pack.now_cnt

        ship = self.__get_role().ship_mgr.get_ship(ship_id)
        setattr(ship, supply_name, now_cnt)

    async def handle_YouStarvedToDeath(self, pack):
        self.__get_chat_dialog().add_chat(pb.ChatType.SYSTEM, 'You starved to death!')

    async def handle_ShipFieldChanged(self, pack):
        ship_id = pack.ship_id
        key = pack.key
        int_value = pack.int_value
        str_value = pack.str_value

        ship = self.__get_role().ship_mgr.get_ship(ship_id)
        if str_value:
            setattr(ship, key, str_value)
        else:
            setattr(ship, key, int_value)

    async def handle_RoleFieldSet(self, pack):
        key = pack.key
        int_value = pack.int_value
        str_value = pack.str_value

        role = self.__get_role()
        if str_value:
            setattr(role, key, str_value)
        else:
            setattr(role, key, int_value)

        if key == 'ration':
            self.__get_options_dialog().pop_some_menus(2)

    async def handle_PortInfo(self, pack):
        price_index = pack.price_index
        economy_index = pack.economy_index
        industry_index = pack.industry_index
        allied_nation = pack.allied_nation

        self.__get_options_dialog().show_port_info(
            price_index, economy_index, industry_index, allied_nation
        )

    async def handle_NationAlliedPorts(self, pack):
        port_ids = pack.port_ids
        price_indexes = pack.price_indexes
        nation_id = pack.nation_id

        self.__get_options_dialog().pop_some_menus(2)
        self.__get_options_dialog().show_nation_allied_ports(port_ids, price_indexes, nation_id)

    async def handle_NationsInvestments(self, pack):
        investments = pack.investments
        self.__get_options_dialog().show_nations_investments(investments)

    async def handle_PersonsInvestments(self, pack):
        persons_investments = pack.persons_investments
        self.__get_options_dialog().show_persons_investments(persons_investments)

    async def handle_AvailableItems(self, pack):
        items_ids = pack.items_ids
        prices = pack.prices
        self.__get_options_dialog().show_available_items(items_ids, prices)

    async def handle_ItemAdded(self, pack):
        item_id = pack.item_id

        role = self.__get_role()
        role.items.append(item_id)

        self.__get_options_dialog().pop_some_menus(3)

        if item_id in [c.Item.TAX_FREE_PERMIT.value, c.Item.LETTER_OF_MARQUE.value]:
            self.__get_options_dialog().building_speak(
                'Please take good care of these documents. '
                'I hear mice like them and they break easily if they get wet.'
            )

    async def handle_ItemSellPrice(self, pack):
        item_id = pack.item_id
        price = pack.price

        self.__get_options_dialog().show_item_sell_price(item_id, price)

    async def handle_ItemRemoved(self, pack):
        item_id = pack.item_id

        role = self.__get_role()
        role.items.remove(item_id)

        self.__get_options_dialog().pop_some_menus(4)

    async def handle_FleetsInvestigated(self, pack):
        fleets_investigated = pack.fleets_investigated
        self.__get_options_dialog().show_fleets_investigated(fleets_investigated)

    async def handle_ItemEquipped(self, pack):
        item_id = pack.item_id

        role = self.__get_role()
        role.equip_item(item_id)

        self.__get_options_dialog().pop_some_menus(3)
        self.__get_options_dialog().show_items()

        # play sound
        sAssetMgr.sounds['equip'].play()

    async def handle_ItemUnequipped(self, pack):
        item_id = pack.item_id

        role = self.__get_role()
        role.unequip_item(item_id)

        self.__get_options_dialog().pop_some_menus(3)
        self.__get_options_dialog().show_items()

        # play sound
        sAssetMgr.sounds['equip'].play()

    async def handle_ItemUsed(self, pack):
        item_id = pack.item_id

        role = self.__get_role()
        role.items.remove(item_id)

        self.__get_options_dialog().pop_some_menus(3)
        self.__get_options_dialog().show_items()

    async def handle_AuraAdded(self, pack):
        aura_id = pack.aura_id

        role = self.__get_role()
        role.auras.add(aura_id)

        if aura_id in [c.Aura.PRAYER.value, c.Aura.DONATION.value]:
            return

        mate = self.get_mate_mgr().get_random_mate()
        aura = sObjectMgr.get_aura(aura_id)
        self.__get_options_dialog().show_mate_speech(mate, f'Captain, we got {aura.name}.')

    async def handle_AuraRemoved(self, pack):
        aura_id = pack.aura_id

        role = self.__get_role()
        role.auras.remove(aura_id)

    async def handle_AuraCleared(self, pack):
        role = self.__get_role()
        role.auras.clear()

    async def handle_NotorityChanged(self, pack):
        nation_id = pack.nation_id
        now_value = pack.now_value

        role = self.__get_role()
        role.notorities[nation_id - 1] = now_value

    async def handle_CannotEnterPort(self, pack):
        reason = pack.reason

        mate = self.get_mate_mgr().get_random_mate()
        self.__get_options_dialog().show_mate_speech(mate, f'{reason}')

    async def handle_DonationMade(self, pack):
        self.__get_options_dialog().pop_some_menus(2)
        self.__get_options_dialog().building_speak('Thank you for your donation!')

    async def handle_YourBalance(self, pack):
        balance = pack.balance
        self.__get_options_dialog().building_speak(f'Your balance is {balance}.')

    async def handle_Deposited(self, pack):
        balance = pack.balance
        self.__get_options_dialog().pop_some_menus(2)
        self.__get_options_dialog().building_speak(f'Thank you! Now your balance is {balance}.')

    async def handle_Withdrawn(self, pack):
        balance = pack.balance
        self.__get_options_dialog().pop_some_menus(2)
        self.__get_options_dialog().building_speak(f'Here you are! Now your balance is {balance}.')

    async def handle_Invested(self, pack):
        self.__get_options_dialog().pop_some_menus(2)
        self.__get_options_dialog().building_speak(f"Thank you so much! We'll definitely put that to good use!")

    async def handle_CrewTreated(self, pack):
        recruited_crew_cnt = pack.recruited_crew_cnt

        self.__get_options_dialog().pop_some_menus(2)
        self.__get_options_dialog().building_speak(
            f'Your crew were grateful for your hospitality. '
            f'In addition, {recruited_crew_cnt} local sailors seem willing to join your crew.')

    async def handle_Slept(self, pack):
        self.__get_options_dialog().building_speak('Did you have a good sleep last night?')

    async def handle_BuildingSpeak(self, pack):
        text = pack.text
        self.__get_options_dialog().building_speak(text)

    async def handle_MateSpeak(self, pack):
        mate_template_id = pack.mate_template_id
        text = pack.text

        self.__get_options_dialog().pop_some_menus(2)
        mate = sObjectMgr.get_mate_template(mate_template_id)
        self.__get_options_dialog().show_mate_speech(mate, text)

    async def handle_Treated(self, pack):
        self.__get_role().has_treated = True

    async def handle_WaitressSeen(self, pack):
        self.__get_options_dialog().show_waitress_menu()