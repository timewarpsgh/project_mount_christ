import time
import asyncio
import json
import traceback
import numpy as np
import random
from concurrent.futures import ThreadPoolExecutor

# import from dir
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared', 'packets'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'models'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from login_pb2 import *
import login_pb2 as pb

import constants as c

from logon_models import Account, World as WorldModel, SESSION as LOGON_SESSION
from role_models import \
    Role as RoleModel, \
    SESSION as ROLE_SESSION, \
    Ship as ShipModel, \
    Mate as MateModel

from object_mgr import sObjectMgr
from npc_mgr import sNpcMgr
from id_mgr import sIdMgr
from map_mgr import sMapMgr
from map_maker import sMapMaker
from season_mgr import sSeasonMgr

import model
import copy


EXECUTOR = ThreadPoolExecutor()


async def run_in_threads(method, packet):
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(EXECUTOR, method, packet)
    return res


class PacketHandler:
    """server"""

    def __init__(self, session):
        self.session = session
        self.account_id = None
        self.account = None
        self.role = None

    async def handle_packet(self, packet):
        packet_name = type(packet).__name__
        try:
            await getattr(self, f'handle_{packet_name}')(packet)
        except Exception as e:
            print(f'{packet_name} error: {e}')
            traceback.print_exc()
        else:
            print()

    def on_disconnect_signal(self, role_to_disappear):
        role_disappeared = RoleDisappeared()
        role_disappeared.id = role_to_disappear.id
        self.session.send(role_disappeared)

    def __get_new_account_res(self, new_account):
        account = LOGON_SESSION.query(Account).\
            filter_by(account=new_account.account).\
            first()

        if account:
            return NewAccountRes.NewAccountResType.ACCOUNT_EXISTS
        else:
            new_obj = Account(
                account=new_account.account,
                password=new_account.password,
            )
            LOGON_SESSION.add(new_obj)
            LOGON_SESSION.commit()
            return NewAccountRes.NewAccountResType.OK

    async def handle_NewAccount(self, new_account):
        # add new account to db
        res_type = await run_in_threads(self.__get_new_account_res, new_account)

        new_account_res = NewAccountRes()
        new_account_res.new_account_res_type = res_type
        self.session.send(new_account_res)

    def __get_login_res(self, login):
        if login.version != c.VERSION:
            return LoginRes.LoginResType.VERSION_NOT_RIGHT


        account = LOGON_SESSION.query(Account).filter_by(
            account=login.account,
            password=login.password).first()

        if account:
            self.account_id = account.id
            self.account = account
            return LoginRes.LoginResType.OK
        else:
            return LoginRes.LoginResType.WRONG_PASSWORD_OR_ACCOUNT

    async def handle_Login(self, login):
        res_type = await run_in_threads(self.__get_login_res, login)

        login_res = LoginRes()
        login_res.login_res_type = res_type
        self.session.send(login_res)

    def __get_worlds(self, any):
        worlds_models = LOGON_SESSION.query(WorldModel).all()
        worlds = []
        for world_model in worlds_models:
            world = World()
            world.id = world_model.id
            world.name = world_model.name

            worlds.append(world)
        return worlds

    async def handle_GetWorlds(self, get_worlds):
        worlds = await run_in_threads(self.__get_worlds, '')

        get_worlds_res = GetWorldsRes()
        get_worlds_res.worlds.extend(worlds)
        self.session.send(get_worlds_res)

    def __get_roles(self, get_roles_in_world):
        world_id = get_roles_in_world.world_id
        account_id = self.account_id

        roles_models = ROLE_SESSION.query(RoleModel).\
            filter_by(world_id=world_id).\
            filter_by(account_id=account_id).\
            all()

        roles = []
        for role_model in roles_models:
            role = Role()
            role.id = role_model.id
            role.name = role_model.name
            roles.append(role)

        return roles

    async def handle_GetRolesInWorld(self, get_roles_in_world):
        roles = await run_in_threads(self.__get_roles, get_roles_in_world)

        get_roles_in_world_res = GetRolesInWorldRes()
        get_roles_in_world_res.roles.extend(roles)
        self.session.send(get_roles_in_world_res)

    def __create_new_role(self, new_role):
        role_model = ROLE_SESSION.query(RoleModel).\
            filter_by(name=new_role.name, world_id=new_role.world_id).\
            first()

        if role_model:
            return NewRoleRes.NewRoleResType.NAME_EXISTS
        else:
            id_of_new_role = self.__create_role(new_role)
            new_mate_id = self.__create_mate(new_role, id_of_new_role)
            # self.__create_ship(new_role, id_of_new_role, new_mate_id)

            return NewRoleRes.NewRoleResType.OK

    def __create_ship(self, new_role, id_of_new_role, new_mate_id):
        ship_template_id = 1
        ship_template = sObjectMgr.get_ship_template(ship_template_id)

        ship_model = ShipModel(
            id=sIdMgr.gen_new_ship_id(),
            role_id=id_of_new_role,
            name='0',
            ship_template_id=ship_template_id,
            material_type=1,
            captain=new_mate_id,

            now_durability=ship_template.durability,
            max_durability=ship_template.durability,

            tacking=ship_template.tacking,
            power=ship_template.power,

            capacity=ship_template.capacity,

            now_crew=ship_template.min_crew,
            min_crew=ship_template.min_crew,
            max_crew=ship_template.max_crew,

            now_guns=0,
            type_of_guns=1,
            max_guns=ship_template.max_guns,

            water=0,
            food=0,
            material=0,
            cannon=0,

            cargo_cnt=0,
            cargo_id=0,

        )
        ROLE_SESSION.add(ship_model)
        ROLE_SESSION.commit()

    def __create_mate(self, new_role, id_of_new_role):

        new_mate_id = sIdMgr.gen_new_mate_id()
        mate_model = MateModel(
            id=new_mate_id,
            role_id=id_of_new_role,
            name=new_role.name,
            img_id=new_role.img_id,
            nation=new_role.nation,
            navigation=1,
            accounting=1,
            battle=1,
            talent_in_navigation=new_role.talent_in_nav,
            talent_in_accounting=new_role.talent_in_acc,
            talent_in_battle=new_role.talent_in_bat,
            lv_in_nav=1,
            lv_in_acc=1,
            lv_in_bat=1,
            xp_in_nav=0,
            xp_in_acc=0,
            xp_in_bat=0,
        )
        ROLE_SESSION.add(mate_model)
        ROLE_SESSION.commit()

        return new_mate_id

    def __create_role(self, new_role):
        new_obj = RoleModel(
            name=new_role.name,
            world_id=new_role.world_id,
            account_id=self.account_id,
            map_id=30,
            x=56,
            y=71,
            dir=0,
            money=0,
            bank_money=2000,
            discovery_ids_json_str=json.dumps([]),
            seen_grids=json.dumps(c.INITIAL_SEEN_GRIDS),
            pay_days=0,
            days_at_sea=0,
            items=json.dumps([]),
            notorities=json.dumps([0] * 6),
            has_treated_crew=False,
            recruited_crew_cnt=0,
            treasure_map_id=0,
            event_id=1,
            nation=new_role.nation,
            ration=100,
        )
        ROLE_SESSION.add(new_obj)

        # get id of new_obj
        ROLE_SESSION.flush()
        id_of_new_role = new_obj.id

        ROLE_SESSION.commit()

        return id_of_new_role

    async def handle_NewRole(self, new_role):
        res_type = await run_in_threads(self.__create_new_role, new_role)

        new_role_res = NewRoleRes()
        new_role_res.new_role_res_type = res_type
        self.session.send(new_role_res)

        if res_type == NewRoleRes.NewRoleResType.OK:
            pack = pb.GetRolesInWorld(world_id=1)
            await self.handle_GetRolesInWorld(pack)

    def __fill_ships_in_ram(self, role, ships):

        for ship in ships:
            ship_obj = model.Ship()
            ship_obj.load_from_db(ship)
            role.ship_mgr.add_ship(ship_obj)

    def __query_ships_in_db(self, role_id):
        ships = ROLE_SESSION.query(ShipModel).\
            filter_by(role_id=role_id).\
            all()
        return ships

    def __gen_proto_ships(self, ships):
        proto_ships = []
        for ship in ships:
            proto_ship = ship.gen_ship_proto()
            proto_ships.append(proto_ship)

        return proto_ships

    def __query_mates_in_db(self, role_id):
        mates = ROLE_SESSION.query(MateModel).\
            filter_by(role_id=role_id).\
            all()
        return mates

    def __fill_mates_in_ram(self, role, mates):
        for mate in mates:
            mate_obj = model.Mate()
            mate_obj.load_from_db(mate)

            role.mate_mgr.add_mate(mate_obj)


    def __gen_proto_mates(self, mates):
        proto_mates = []
        for mate in mates:
            proto_mate = mate.gen_mate_pb()
            proto_mates.append(proto_mate)

        return proto_mates

    def __get_matrix_from_seen_grids(self, role):
        two_d_list = json.loads(role.seen_grids)
        matrix = np.array(two_d_list)
        return matrix

    def __get_64_int32s_from_seen_grids(self, matrix):

        ints = [0] * c.SEEN_GRIDS_COLS
        for i in range(c.SEEN_GRIDS_COLS):

            col_vals = matrix[:, i]

            bit_str = ''.join(str(x) for x in col_vals)

            # turn bit_str with 32 bits into a int32 number
            int_num = int(bit_str, 2)

            ints[i] = int_num

        return ints

    def __enter_world(self, enter_world):
        role = ROLE_SESSION.query(RoleModel).\
            filter_by(id=enter_world.role_id, account_id=self.account_id).\
            first()

        if role:
            # fill self.role
            self.role = model.Role(
                session=self.session,
                id=role.id,
                name=role.name,
                x=role.x,
                y=role.y,
                dir=role.dir,
                map_id=role.map_id,
                money=role.money,
                pay_days=role.pay_days,
                bank_money=role.bank_money,
                items=json.loads(role.items),
                notorities=json.loads(role.notorities),

                has_treated_crew=role.has_treated_crew,
                recruited_crew_cnt=role.recruited_crew_cnt,
                treasure_map_id=role.treasure_map_id,
                wanted_mate_template_id=role.wanted_mate_template_id,
                event_id=role.event_id,
                nation=role.nation,

                weapon=role.weapon,
                armor=role.armor,
                ration=role.ration,
            )

            # init seen grids
            self.role.seen_grids = self.__get_matrix_from_seen_grids(role)

            # init auras
            self.role.auras = set()

            # add self.role to server
            self.session.server.add_role(role.id, self.role)

            # init discovery_mgr
            self.role.discovery_mgr = model.DiscoveryMgr()
            if role.discovery_ids_json_str:
                discovery_ids = json.loads(role.discovery_ids_json_str)
            else:
                discovery_ids = []
            for discovery_id in discovery_ids:
                self.role.discovery_mgr.add(discovery_id)

            # init ship_mgr
            self.role.ship_mgr = model.ShipMgr(self.role)

            # fill ships
            ships = self.__query_ships_in_db(enter_world.role_id)
            self.__fill_ships_in_ram(self.role, ships)
            proto_ships = self.__gen_proto_ships(self.role.ship_mgr.get_ships())

            # init mate_mgr
            self.role.mate_mgr = model.MateMgr(self.role)

            # fill mates
            mates = self.__query_mates_in_db(enter_world.role_id)
            self.__fill_mates_in_ram(self.role, mates)
            proto_mates = self.__gen_proto_mates(self.role.mate_mgr.get_mates())

            # init friend_mgr
            self.role.friend_mgr = model.FriendMgr(self.role, self.role.id)
            self.role.friend_mgr.load_from_db(self.session.server)
            proto_friends = self.role.friend_mgr.gen_proto_friends()

            # prepare packet to send to client
            role_entered = RoleEntered()
            role_entered.id = role.id
            role_entered.name = role.name
            role_entered.map_id = role.map_id
            role_entered.x = role.x
            role_entered.y = role.y
            role_entered.dir = role.dir
            role_entered.money = role.money
            role_entered.items = role.items
            role_entered.notorities = role.notorities
            role_entered.treasure_map_id = role.treasure_map_id
            role_entered.wanted_mate_template_id = role.wanted_mate_template_id if role.wanted_mate_template_id else 0
            role_entered.event_id = role.event_id
            role_entered.nation = role.nation
            role_entered.weapon = role.weapon if role.weapon else 0
            role_entered.armor = role.armor if role.armor else 0
            role_entered.ration = role.ration if role.ration else 100

            if role.discovery_ids_json_str:
                role_entered.discovery_ids_json_str = role.discovery_ids_json_str
            ints = self.__get_64_int32s_from_seen_grids(self.role.seen_grids)
            role_entered.seen_grids_64_int32s.extend(ints)

            # fill ships and mates in protocol
            role_entered.ships.extend(proto_ships)
            role_entered.mates.extend(proto_mates)
            role_entered.friends.extend(proto_friends)

            enter_world_res = EnterWorldRes()
            enter_world_res.is_ok = True
            enter_world_res.role_entered.CopyFrom(role_entered)

            return enter_world_res


        else:
            enter_world_res = EnterWorldRes()
            enter_world_res.is_ok = False

            return enter_world_res

    async def handle_EnterWorld(self, enter_world):
        enter_world_res = await run_in_threads(self.__enter_world, enter_world)
        self.session.send(enter_world_res)
        self.session.send(sSeasonMgr.gen_season_changed_pb())

        # # enter port for tesing!!!!!!
        self.role.enter_port(self.role.map_id, self.role.x, self.role.y)

        # add role to map_mgr
        sMapMgr.add_object(self.role)

        # notify presence of nearby_roles
        self.send_role_appeared_to_nearby_roles()

        # sail
        # await self.handle_Sail('')

    async def handle_GetAvailableCargos(self, get_available_cargos):
        self.role.get_available_cargos()

    async def handle_Move(self, move):
        self.role.move(move.dir_type)

    async def handle_StartMoving(self, start_moving):
        x = start_moving.src_x
        y = start_moving.src_y
        dir = start_moving.dir_type
        self.role.start_moving(x, y, dir)

    async def handle_StopMoving(self, stop_moving):
        x = stop_moving.x
        y = stop_moving.y
        dir = stop_moving.dir
        self.role.stopped_moving(x, y, dir)

    async def handle_Disconnect(self, disconnect):
        print('got disconn packet from client')

        if not self.role:
            self.session.writer.close()
            await self.session.writer.wait_closed()
        else:
            if self.role.is_in_port():
                self.session.writer.close()
                await self.session.writer.wait_closed()
                # self.session.on_disconnect()
            else:
                # send chat
                pack = pb.GotChat(
                    chat_type=pb.ChatType.SYSTEM,
                    text=f'Please exit when in a port.',
                )
                self.session.send(pack)

    async def handle_BuyCargo(self, buy_cargo):
        cargo_id = buy_cargo.cargo_id
        cnt = buy_cargo.cnt
        ship_id = buy_cargo.ship_id

        self.role.buy_cargo(cargo_id, cnt, ship_id)

    async def handle_GetCargoCntAndSellPrice(self, get_cargo_cnt_and_sell_price):
        ship_id = get_cargo_cnt_and_sell_price.ship_id
        self.role.get_cargo_cnt_and_sell_price(ship_id)

    async def handle_SellCargoInShip(self, sell_cargo_in_ship):
        ship_id = sell_cargo_in_ship.ship_id
        cargo_id = sell_cargo_in_ship.cargo_id
        cnt = sell_cargo_in_ship.cnt

        self.role.sell_cargo(ship_id, cargo_id, cnt)

    def send_to_nearby_roles(self, packet, include_self=False):
        # notify presence of nearby_roles
        nearby_objects = sMapMgr.get_nearby_objects(self.role, include_self)
        for object in nearby_objects:
            if object.is_role():
                object.session.send(packet)

    def _handle_gm_cmd_map(self, params):
        port_id = int(params[0])

        self.send_role_disappeared_to_nearby_roles()

        old_x = self.role.x
        old_y = self.role.y
        old_map_id = self.role.map_id

        self.role.enter_port(port_id)

        sMapMgr.change_object_map(self.role,
                                  old_map_id, old_x, old_y,
                                  port_id, self.role.x, self.role.y)

        self.send_role_appeared_to_nearby_roles()


        pack = GotChat(
            origin_name=self.role.name,
            chat_type=ChatType.SYSTEM,
            text=f'map_id changed to {port_id}',
        )
        self.session.send(pack)

    def _handle_gm_cmd_vil(self, params):
        village_id = int(params[0])
        village = sObjectMgr.get_village(village_id)
        x = village.x
        y = village.y
        self.role.change_xy(x, y)

    def _handle_gm_cmd_xy(self, params):
        x = int(params[0])
        y = int(params[1])

        self.role.change_xy(x, y)

        pack = pb.GotChat(
            origin_name=self.role.name,
            chat_type=pb.ChatType.SYSTEM,
            text=f'xy changed to {x} {y}',
        )
        self.session.send(pack)

    def _handle_gm_cmd_win_npc(self, params):
        self.role.win_npc()

    def _handle_gm_cmd_die(self, params):
        self.role.die()

    def _handle_gm_cmd_lose_to_npc(self, params):
        # lose all except flag ship
        self.role.lose_to_npc()

    def __get_target_role(self):
        if self.role.battle_role_id:
            target_role = self.session.server.get_role(self.role.battle_role_id)
            return target_role
        else:
            return None

    def _handle_gm_cmd_win_role(self, params):

        # get target role
        target_role = self.__get_target_role()
        if not target_role:
            return

        self.role.win(target_role)

    def _handle_gm_cmd_lose_to_role(self, params):
        # get target role
        target_role = self.__get_target_role()
        if not target_role:
            return

        target_role.win(self.role)

    def _handle_gm_cmd_if(self, params):
        nation_id = int(params[0])
        fleet_id = int(params[1])
        self.role.investigate_fleet(nation_id, fleet_id)

    def __handle_gm_cmd(self, text):
        split_items = text[1:].split()
        cmd = split_items[0]
        params = split_items[1:]

        try:
            getattr(self, f'_handle_gm_cmd_{cmd}')(params)
        except Exception as e:
            print(f'handle gm cmd error: {e}')
            traceback.print_exc()
        else:
            print()

    async def handle_Chat(self, chat):
        # say
        if chat.chat_type == ChatType.SAY:

            # handle gm cmds
            if chat.text.startswith('.'):
                if self.account.gm_lv:
                   if self.account.gm_lv >= 9:
                        self.__handle_gm_cmd(chat.text.lower())
                        return

            # normal say chat
            pack = GotChat(
                origin_name=self.role.name,
                chat_type=ChatType.SAY,
                text=chat.text,
                role_id=self.role.id,
            )
            self.send_to_nearby_roles(pack, include_self=True)

        # whisper
        elif chat.chat_type == ChatType.WHISPER:

            target_role = self.session.server.get_role_by_name(chat.whisper_target_name)
            if target_role:
                pack = GotChat(
                    origin_name=self.role.name,
                    chat_type=ChatType.WHISPER,
                    text=chat.text,
                )
                target_role.session.send(pack)

                pack = GotChat(
                    origin_name=self.role.name,
                    chat_type=ChatType.WHISPER,
                    text=chat.text,
                    whisper_target_name=chat.whisper_target_name,
                )
                self.session.send(pack)

            else:
                # send chat msg
                pack = GotChat(
                    chat_type=ChatType.SYSTEM,
                    text=f'{chat.whisper_target_name} not found',
                )
                self.session.send(pack)

        # nation
        elif chat.chat_type == ChatType.NATION:
            nation = self.role.nation
            roles = self.session.server.get_roles_by_nation(nation)

            for role in roles:
                pack = GotChat(
                    origin_name=self.role.name,
                    chat_type=ChatType.NATION,
                    text=chat.text,
                )
                role.session.send(pack)

        # world
        elif chat.chat_type == ChatType.GLOBAL:
            roles = self.session.server.get_roles()

            for role in roles:
                pack = GotChat(
                    origin_name=self.role.name,
                    chat_type=ChatType.GLOBAL,
                    text=chat.text,
                )
                role.session.send(pack)

    async def handle_Discover(self, discover):
        village_id = discover.village_id
        self.role.make_discovery(village_id)

    def send_role_disappeared_to_nearby_roles(self):
        nearby_objects = sMapMgr.get_nearby_objects(self.role)

        for object in nearby_objects:
            if object.is_role():
                object.session.send(RoleDisappeared(id=self.role.id))

            self.session.send(RoleDisappeared(id=object.id))

    def send_role_appeared_to_nearby_roles(self):
        nearby_objects = sMapMgr.get_nearby_objects(self.role)


        for object in nearby_objects:
            if object.is_role():
                object.session.send(
                    RoleAppeared(
                        id=self.role.id,
                        name=self.role.name,
                        x=self.role.x,
                        y=self.role.y,
                    )
                )

            self.session.send(
                RoleAppeared(
                    id=object.id,
                    name=object.name,
                    x=object.x,
                    y=object.y,
                )
            )

    async def handle_Sail(self, sail):
        self.role.sail()

    async def handle_EnterPort(self, enter_port):
        port_id = enter_port.id

        distance = 3

        port = sObjectMgr.get_port(port_id)
        if abs(port.x - self.role.x) <= distance and abs(port.y - self.role.y) <= distance:

            # notority check
            if not self.role.can_enter_port(port_id):
                return

            self.send_role_disappeared_to_nearby_roles()

            old_x = self.role.x
            old_y = self.role.y

            self.role.enter_port(port_id)

            sMapMgr.change_object_map(self.role,
                                      0, old_x, old_y,
                                      port_id, self.role.x, self.role.y)

            self.send_role_appeared_to_nearby_roles()
        else:
            pass

    async def handle_EscapeNpcBattle(self, escape_npc_battle):
        npc_id = escape_npc_battle.npc_id
        self.role.escape_npc_battle()

    async def handle_SellShip(self, sell_ship):
        id = sell_ship.id
        self.role.sell_ship(id)

    async def handle_GetShipsToBuy(self, get_ships_to_buy):
        self.role.get_ships_to_buy()

    async def handle_BuyShip(self, buy_ship):
        ship_template_id = buy_ship.template_id
        self.role.buy_ship(ship_template_id)

    async def handle_FightRole(self, fight_role):
        role_id = fight_role.role_id
        self.role.fight_role(role_id)

    async def handle_FightNpc(self, fight_npc):
        npc_id = fight_npc.npc_id
        self.role.fight_npc(npc_id)

    async def handle_EscapeRoleBattle(self, escape_role_battle):
        self.role.escape_role_battle()

    def send_to_self_and_enemy(self, pack):
        enemy_role = self.get_enemy_role()

        self.session.send(pack)
        enemy_role.session.send(pack)

    def get_enemy_role(self):
        return self.session.server.get_role(self.role.battle_role_id)


    async def handle_AllShipsAttack(self, all_ships_attack):
        # if not self.role.battle_timer:
        #     return
        #
        # self.role.battle_timer = None

        await self.role.all_ships_attack_role()


    async def handle_SetAllShipsTarget(self, set_all_ships_target):
        ship_id = set_all_ships_target.ship_id
        self.role.set_all_ships_target(ship_id)

    async def handle_SetAllShipsStrategy(self, set_all_ships_strategy):
        strategy = set_all_ships_strategy.attack_method_type
        self.role.set_all_ships_strategy(strategy)

    async def handle_SetShipTarget(self, set_ship_target):
        ship_id = set_ship_target.ship_id
        target_ship_id = set_ship_target.target_ship_id
        self.role.set_ship_target(ship_id, target_ship_id)

    async def handle_SetShipStrategy(self, set_ship_strategy):
        ship_id = set_ship_strategy.ship_id
        strategy = set_ship_strategy.attack_method_type
        self.role.set_ship_strategy(ship_id, strategy)

    async def handle_FlagShipMove(self, flag_ship_move):
        battle_dir_type = flag_ship_move.battle_dir_type
        await self.role.flagship_move(battle_dir_type)

    async def handle_FlagShipAttack(self, pack):
        attack_method_type = pack.attack_method_type
        target_ship_id = pack.target_ship_id
        await self.role.flagship_attack(attack_method_type, target_ship_id)

    async def handle_ViewFleet(self, view_fleet):
        role_id = view_fleet.role_id
        role = self.session.server.get_role(role_id)
        if not role:
            role = sNpcMgr.get_npc(role_id)

        ships = role.ship_mgr.get_ships()
        ships_template_ids = [ship.ship_template_id for ship in ships]

        pack = pb.FleetInfo()
        pack.ships_template_ids.extend(ships_template_ids)
        self.session.send(pack)

    async def handle_GetMateInPort(self, get_mate_in_port):
        port_map = sMapMgr.get_map(self.role.map_id)
        mate_template = port_map.mate_template
        mate_template_id = mate_template.id if mate_template else 0

        pack = pb.MateInPort(
            mate_template_id=mate_template_id,
        )
        self.session.send(pack)

    async def handle_HireMate(self, hire_mate):
        mate_template_id = hire_mate.mate_template_id
        self.role.hire_mate(mate_template_id)

    async def handle_FireMate(self, fire_mate):
        mate_id = fire_mate.mate_id

        self.role.mate_mgr.rm_mate(mate_id)

        pack = pb.MateFired(mate_id=mate_id)
        self.session.send(pack)

    async def handle_AssignDuty(self, assign_duty):
        mate_id = assign_duty.mate_id
        ship_id = assign_duty.ship_id
        duty_type = assign_duty.duty_type

        # lv required
        if duty_type == pb.DutyType.CAPTAIN:
            ship = self.role.ship_mgr.get_ship(ship_id)
            ship_template = sObjectMgr.get_ship_template(ship.ship_template_id)
            if self.role.get_lv() < ship_template.lv:
                # send chat msg
                pack = pb.GotChat(
                    chat_type=pb.ChatType.SYSTEM,
                    text=f'lv required: {ship_template.lv}',
                )
                self.session.send(pack)
                return

        # can't replace captain of flagship
        flag_ship = self.role.get_flag_ship()
        if flag_ship:
            if ship_id == flag_ship.id and duty_type == pb.DutyType.CAPTAIN:
                # send chat msg
                pack = pb.GotChat(
                    chat_type=pb.ChatType.SYSTEM,
                    text='can\'t replace captain of flagship',
                )
                self.session.send(pack)
                return

        self.role.mate_mgr.assign_duty(mate_id, ship_id, duty_type)

        pack = pb.DutyAssigned(mate_id=mate_id, ship_id=ship_id, duty_type=duty_type)
        self.session.send(pack)

    async def handle_RepairShip(self, repair_ship):
        ship_id = repair_ship.id
        self.role.repair_ship(ship_id)

    async def handle_RenameShip(self, rename_ship):
        id = rename_ship.id
        name = rename_ship.name

        self.role.rename_ship(id, name)

    async def handle_ChangeShipCapacity(self, change_ship_capacity):
        id = change_ship_capacity.id
        max_crew = change_ship_capacity.max_crew
        max_guns = change_ship_capacity.max_guns

        self.role.change_ship_capacity(id, max_crew, max_guns)

    async def handle_ChangeShipWeapon(self, change_ship_weapon):
        ship_id = change_ship_weapon.ship_id
        cannon_id = change_ship_weapon.cannon_id

        self.role.change_ship_weapon(ship_id, cannon_id)

    async def handle_RecruitCrew(self, recruit_crew):
        ship_id = recruit_crew.ship_id
        cnt = recruit_crew.cnt

        self.role.recruit_crew(ship_id, cnt)

    async def handle_DismissCrew(self, dismiss_crew):
        ship_id = dismiss_crew.ship_id
        cnt = dismiss_crew.cnt

        self.role.dismiss_crew(ship_id, cnt)

    async def handle_LoadSupply(self, load_supply):
        ship_id = load_supply.ship_id
        supply_name = load_supply.supply_name
        cnt = load_supply.cnt

        self.role.load_supply(ship_id, supply_name, cnt)

    async def handle_UnloadSupply(self, unload_supply):
        ship_id = unload_supply.ship_id
        supply_name = unload_supply.supply_name
        cnt = unload_supply.cnt

        self.role.unload_supply(ship_id, supply_name, cnt)

    async def handle_SetRoleField(self, set_role_field):
        key = set_role_field.key
        int_value = set_role_field.int_value
        str_value = set_role_field.str_value

        self.role.set_field(key, int_value, str_value)

    async def handle_GetPortInfo(self, get_port_info):
        port_id = self.role.map_id

        port_map = sMapMgr.get_map(port_id)
        pack = pb.PortInfo(
            price_index=port_map.price_index,
            economy_index=port_map.economy_index,
            industry_index=port_map.industry_index,
            allied_nation=port_map.allied_nation,
            governor=port_map.governor_name if port_map.governor_name else 'NA',
            same_nation_tax=port_map.same_nation_tax,
            other_nation_tax=port_map.other_nation_tax,
        )
        self.session.send(pack)

    async def handle_GetNationInfo(self, get_nation_info):
        nation_id = get_nation_info.nation_id


        if self.role.money <= 1000:
            return

        self.role.mod_money(-1000)

        allied_ports_ids = []
        price_indexes = []
        same_nation_rates = []
        other_nation_rates = []
        governors = []

        port_maps = sMapMgr.get_port_maps()
        for port in port_maps:
            if port.allied_nation == nation_id:
                allied_ports_ids.append(port.id)
                price_indexes.append(port.price_index)
                same_nation_rates.append(port.same_nation_tax)
                other_nation_rates.append(port.other_nation_tax)
                governor_name = port.governor_name if port.governor_name else 'NA'
                governors.append(governor_name)

        pack = pb.NationAlliedPorts()
        pack.port_ids.extend(allied_ports_ids)
        pack.price_indexes.extend(price_indexes)
        pack.same_nation_rates.extend(same_nation_rates)
        pack.other_nation_rates.extend(other_nation_rates)
        pack.governors.extend(governors)
        pack.nation_id = nation_id
        self.session.send(pack)

    async def handle_GetNationsInvestments(self, get_nations_investments):

        port_map = sMapMgr.get_map(self.role.map_id)

        investments = list(port_map.nation_2_investment.values())

        pack = pb.NationsInvestments()
        pack.investments.extend(investments)
        self.session.send(pack)

    async def handle_Invest(self, invest):
        ingots_cnt = invest.ingots_cnt

        self.role.invest(ingots_cnt)

    def get_role_by_id(self, role_id):
        return self.session.server.get_role(role_id)

    async def handle_GetPersonsInvestments(self, get_persons_investments):

        port_map = self.role.get_map()
        my_dict = port_map.role_name_2_investment

        best_3_roles_names = list(my_dict.keys())[:3]

        persons_investments = []
        for role_name in best_3_roles_names:
            investment = my_dict[role_name]
            pack = pb.PersonInvestment(
                name=role_name,
                investment=investment,
            )
            persons_investments.append(pack)

        pack = pb.PersonsInvestments()
        pack.persons_investments.extend(persons_investments)
        self.session.send(pack)

    async def handle_GetAvailableItems(self, get_available_items):
        ids = self.role.get_availalbe_items_ids_in_port()
        prices = [sObjectMgr.get_item(id).buy_price for id in ids]


        pack = pb.AvailableItems()
        pack.items_ids.extend(ids)
        pack.prices.extend(prices)
        self.session.send(pack)

    async def handle_BuyItem(self, buy_item):
        item_id = buy_item.item_id

        self.role.buy_item(item_id)

    async def handle_GetItemSellPrice(self, get_item_sell_price):
        item_id = get_item_sell_price.item_id

        if item_id == self.role.weapon or item_id == self.role.armor:
            # send chat
            pack = pb.GotChat(
                chat_type=pb.ChatType.SYSTEM,
                text='can\'t sell equipped items',
            )
            self.session.send(pack)
            return

        price = sObjectMgr.get_item_sell_price(item_id)

        pack = pb.ItemSellPrice(item_id=item_id, price=price)
        self.session.send(pack)

    async def handle_SellItem(self, sell_item):
        item_id = sell_item.item_id

        self.role.sell_item(item_id)

    async def handle_BuyTaxFreePermit(self, buy_tax_free_permit):
        self.role.buy_tax_free_permit()

    async def handle_BuyLetterOfMarque(self, buy_letter_of_marque):
        self.role.buy_letter_of_marque()

    async def handle_InvestigateFleet(self, investigate_fleet):
        nation_id = investigate_fleet.nation_id
        fleet_id = investigate_fleet.fleet_id
        self.role.investigate_fleet(nation_id, fleet_id)

    async def handle_EquipItem(self, equip_item):
        item_id = equip_item.item_id
        self.role.equip_item(item_id)

    async def handle_UnequipItem(self, unequip_item):
        item_id = unequip_item.item_id
        self.role.unequip_item(item_id)

    async def handle_UseItem(self, use_item):
        item_id = use_item.item_id
        self.role.use_item(item_id)

    async def handle_Land(self, land):
        self.role.land()

    async def handle_Pray(self, pray):
        self.role.pray()

    async def handle_Donate(self, donate):
        ingots_cnt = donate.ingots_cnt
        self.role.donate(ingots_cnt)

    async def handle_CheckBalance(self, check_balance):
        self.role.check_balance()

    async def handle_Deposit(self, deposit):
        amount = deposit.amount
        self.role.deposit(amount)

    async def handle_Withdraw(self, withdraw):
        amount = withdraw.amount
        self.role.withdraw(amount)

    async def handle_TreatCrew(self, treat_crew):
        self.role.treat_crew()

    async def handle_Sleep(self, sleep):
        self.role.sleep()

    async def handle_Treat(self, treat):
        self.role.treat()

    async def handle_SeeWaitress(self, see_waitress):
        self.role.see_waitress()

    async def handle_Gossip(self, gossip):
        npc_id = gossip.npc_id
        self.role.gossip(npc_id)

    async def handle_ViewCaptain(self, view_captain):
        role_id = view_captain.role_id
        self.role.view_captain(role_id)

    async def handle_BuyTreasureMap(self, buy_treasure_map):
        self.role.buy_treasure_map()

    async def handle_TriggerEvent(self, trigger_event):
        self.role.trigger_event()

    async def handle_RequestTrade(self, request_trade):
        role_id = request_trade.role_id
        self.role.request_trade(role_id)

    async def handle_AcceptTradeRequest(self, accept_trade_request):
        role_id = accept_trade_request.role_id
        self.role.accept_trade_request(role_id)

    async def handle_SetTradeMoney(self, set_trade_money):
        amount = set_trade_money.amount
        self.role.set_trade_money(amount)

    async def handle_ConfirmTrade(self, confirm_trade):
        self.role.confirm_trade()

    async def handle_SetTradeItem(self, set_trade_item):
        item_id = set_trade_item.item_id
        self.role.set_trade_item(item_id)

    async def handle_AddFriend(self, pack):
        await run_in_threads(self.role.friend_mgr.add_friend, pack)

    async def handle_RemoveFriend(self, pack):
        await run_in_threads(self.role.friend_mgr.remove_friend, pack)

    async def handle_BuyWanted(self, pack):
        fleet_type = pack.fleet_type
        self.role.buy_wanted(fleet_type)

    async def handle_ManagePort(self, pack):
        self.role.manage_port()

    async def handle_SetPortStates(self, pack):
        self.role.set_port_states(pack)