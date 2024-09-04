import time
import asyncio
import json
import traceback
import numpy as np
import random
from concurrent.futures import ThreadPoolExecutor

# import from dir
import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\server\models')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared')

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
            new_obj = RoleModel(
                name=new_role.name,
                world_id=new_role.world_id,
                account_id=self.account_id,
                map_id=2,
                x=4,
                y=2,
            )

            ROLE_SESSION.add(new_obj)
            ROLE_SESSION.commit()

            return NewRoleRes.NewRoleResType.OK

    async def handle_NewRole(self, new_role):
        res_type = await run_in_threads(self.__create_new_role, new_role)

        new_role_res = NewRoleRes()
        new_role_res.new_role_res_type = res_type
        self.session.send(new_role_res)


    def __fill_ships_in_ram(self, role, ships):

        for ship in ships:
            ship_obj = model.Ship(
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
                chief_navigator=ship.chief_navigator,
            )

            role.ship_mgr.add_ship(ship_obj)

    def __query_ships_in_db(self, role_id):
        ships = ROLE_SESSION.query(ShipModel).\
            filter_by(role_id=role_id).\
            all()
        return ships

    def __gen_proto_ships(self, ships):
        proto_ships = []
        for ship in ships:
            proto_ship = Ship(
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
                chief_navigator=ship.chief_navigator,

            )

            proto_ships.append(proto_ship)

        return proto_ships

    def __query_mates_in_db(self, role_id):
        mates = ROLE_SESSION.query(MateModel).\
            filter_by(role_id=role_id).\
            all()
        return mates

    def __fill_mates_in_ram(self, role, mates):
        for mate in mates:
            mate_obj = model.Mate(
                id=mate.id,
                role_id=mate.role_id,

                name=mate.name,
                img_id=mate.img_id,
                nation=mate.nation,

                lv=mate.lv,
                points=mate.points,
                assigned_duty=mate.assigned_duty,
                ship_id=mate.ship_id,

                leadership=mate.leadership,
                navigation=mate.navigation,
                accounting=mate.accounting,
                battle=mate.battle,

                talent_in_navigation=mate.talent_in_navigation,
                talent_in_accounting=mate.talent_in_accounting,
                talent_in_battle=mate.talent_in_battle,
            )

            role.mate_mgr.add_mate(mate_obj)


    def __gen_proto_mates(self, mates):
        proto_mates = []
        for mate in mates:
            proto_mate = Mate(
                id=mate.id,
                role_id=mate.role_id,

                name=mate.name,
                img_id=mate.img_id,
                nation=mate.nation,

                lv=mate.lv,
                points=mate.points,
                assigned_duty=mate.assigned_duty,
                ship_id=mate.ship_id,

                leadership=mate.leadership,
                navigation=mate.navigation,
                accounting=mate.accounting,
                battle=mate.battle,

                talent_in_navigation=mate.talent_in_navigation,
                talent_in_accounting=mate.talent_in_accounting,
                talent_in_battle=mate.talent_in_battle,
            )
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
            )

            # init seen grids
            self.role.seen_grids = self.__get_matrix_from_seen_grids(role)

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
            proto_ships = self.__gen_proto_ships(ships)

            # init mate_mgr
            self.role.mate_mgr = model.MateMgr(self.role)

            # fill mates
            mates = self.__query_mates_in_db(enter_world.role_id)
            self.__fill_mates_in_ram(self.role, mates)
            proto_mates = self.__gen_proto_mates(mates)

            # prepare packet to send to client
            role_entered = RoleEntered()
            role_entered.id = role.id
            role_entered.name = role.name
            role_entered.map_id = role.map_id
            role_entered.x = role.x
            role_entered.y = role.y
            role_entered.dir = role.dir
            role_entered.money = role.money
            if role.discovery_ids_json_str:
                role_entered.discovery_ids_json_str = role.discovery_ids_json_str
            ints = self.__get_64_int32s_from_seen_grids(self.role.seen_grids)
            role_entered.seen_grids_64_int32s.extend(ints)

            # fill ships and mates in protocol
            role_entered.ships.extend(proto_ships)
            role_entered.mates.extend(proto_mates)

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

        # enter port for tesing!!!!!!
        self.role.enter_port(self.role.map_id)

        # add role to map_mgr
        sMapMgr.add_object(self.role)

        # notify presence of nearby_roles
        self.send_role_appeared_to_nearby_roles()

        # sail
        await self.handle_Sail('')


    def __get_available_cargos(self):
        port = sObjectMgr.get_port(self.role.map_id)
        cargo_ids = sObjectMgr.get_cargo_ids(port.economy_id)
        available_cargos = []

        for cargo_id in cargo_ids:
            cargo_template = sObjectMgr.get_cargo_template(cargo_id)
            available_cargo = AvailableCargo()
            available_cargo.id = cargo_template.id
            available_cargo.name = cargo_template.name

            available_cargo.price = json.loads(cargo_template.buy_price)[str(port.economy_id)]

            available_cargos.append(available_cargo)

        return available_cargos

    async def handle_GetAvailableCargos(self, get_available_cargos):

        available_cargos = self.__get_available_cargos()

        get_available_cargos_res = GetAvailableCargosRes()
        get_available_cargos_res.available_cargos.extend(available_cargos)
        self.session.send(get_available_cargos_res)

    async def handle_Move(self, move):
        self.role.move(move.dir_type)

    async def handle_StartMoving(self, start_moving):
        x = start_moving.src_x
        y = start_moving.src_y
        dir = start_moving.dir_type
        self.role.start_moving(x, y, dir)

    async def handle_StopMoving(self, stop_moving):
        self.role.is_moving = False

        tolerant_diff = 4

        # if abs(self.role.x - stop_moving.x) <= tolerant_diff and \
        #         abs(self.role.y - stop_moving.y) <= tolerant_diff:
        old_x = self.role.x
        old_y = self.role.y

        self.role.x = stop_moving.x
        self.role.y = stop_moving.y
        self.role.dir = stop_moving.dir

        sMapMgr.move_object(self.role, old_x, old_y, self.role.x, self.role.y)


        pack = pb.StoppedMoving(
            id=self.role.id,
            src_x=self.role.x,
            src_y=self.role.y,
            dir=self.role.dir,
        )
        self.send_to_nearby_roles(pack, include_self=True)
        print(f'server: {self.role.id} stopped moving at ({self.role.x}, {self.role.y})')


    async def handle_Disconnect(self, disconnect):
        print('got disconn packet from client')
        self.session.writer.close()
        await self.session.writer.wait_closed()

        # self.session.on_disconnect()

    async def handle_BuyCargo(self, buy_cargo):
        cargo_id = buy_cargo.cargo_id
        cnt = buy_cargo.cnt
        ship_id = buy_cargo.ship_id

        print(f'cnt: {cnt}')

        # get cost
        cost = 0
        cargo_template = sObjectMgr.get_cargo_template(cargo_id)
        economy_id_str_2_buy_price = json.loads(cargo_template.buy_price)

        port = sObjectMgr.get_port(self.role.map_id)

        # port dosen't have this cargo
        if str(port.economy_id) not in economy_id_str_2_buy_price:
            print("port dosen't have this cargo")
            return

        buy_price = economy_id_str_2_buy_price[str(port.economy_id)]
        cost = cnt * buy_price

        # not enough money
        if not self.role.money  >= cost:
            print("not enough money")
            return

        # update ram
        self.role.money -= cost
        self.role.ship_mgr.get_ship(ship_id).add_cargo(cargo_id, cnt)

        # tell client
        money_changed = MoneyChanged()
        money_changed.money = self.role.money
        self.session.send(money_changed)

        ship_cargo_changed = ShipCargoChanged()
        ship_cargo_changed.ship_id = ship_id
        ship_cargo_changed.cargo_id = cargo_id
        ship_cargo_changed.cnt = cnt
        self.session.send(ship_cargo_changed)

    async def handle_GetCargoCntAndSellPrice(self, get_cargo_cnt_and_sell_price):
        ship_id = get_cargo_cnt_and_sell_price.ship_id
        ship = self.role.ship_mgr.get_ship(ship_id)

        if not ship.cargo_id:
            return

        # get sell price
        cargo_template = sObjectMgr.get_cargo_template(ship.cargo_id)
        port = sObjectMgr.get_port(self.role.map_id)
        sell_price = json.loads(cargo_template.sell_price)[str(port.economy_id)]

        packet = CargoToSellInShip()
        packet.cargo_id = ship.cargo_id
        packet.cargo_name = cargo_template.name
        packet.cnt = ship.cargo_cnt
        packet.sell_price = sell_price
        packet.ship_id = ship_id
        self.session.send(packet)


    async def handle_SellCargoInShip(self, sell_cargo_in_ship):
        ship_id = sell_cargo_in_ship.ship_id
        cargo_id = sell_cargo_in_ship.cargo_id
        cnt = sell_cargo_in_ship.cnt

        ship = self.role.ship_mgr.get_ship(ship_id)

        if not ship.cargo_id:
            return
        if not ship.cargo_cnt >= cnt:
            return

        # get sell price
        cargo_template = sObjectMgr.get_cargo_template(cargo_id)
        port = sObjectMgr.get_port(self.role.map_id)
        sell_price = json.loads(cargo_template.sell_price)[str(port.economy_id)]

        # change ram
        self.role.money += cnt * sell_price
        ship.remove_cargo(cargo_id, cnt)

        # tell client
        self.session.send(MoneyChanged(money=self.role.money))
        self.session.send(ShipCargoChanged(ship_id=ship_id, cargo_id=ship.cargo_id, cnt=ship.cargo_cnt))
        self.session.send(PopSomeMenus(cnt=2))

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

    def _handle_gm_cmd_xy(self, params):
        x = int(params[0])
        y = int(params[1])

        pack = GotChat(
            origin_name=self.role.name,
            chat_type=ChatType.SYSTEM,
            text=f'xy changed to {x} {y}',
        )
        self.session.send(pack)

        self.send_role_disappeared_to_nearby_roles()

        old_x = self.role.x
        old_y = self.role.y
        old_map_id = self.role.map_id

        self.role.x = x
        self.role.y = y

        sMapMgr.change_object_map(self.role,
                                  old_map_id, old_x, old_y,
                                  self.role.map_id, self.role.x, self.role.y)

        self.send_role_appeared_to_nearby_roles()

        pack = RoleMoved(
            id=self.role.id,
            x=self.role.x,
            y=self.role.y,
            dir_type=DirType.E,
        )
        self.session.send(pack)

    def _handle_gm_cmd_win_npc(self, params):
        self.role.win_npc()

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
            )
            self.send_to_nearby_roles(pack, include_self=True)

    async def handle_Discover(self, discover):
        village_id = discover.village_id

        village = sObjectMgr.get_village(village_id)
        distance = 3

        if abs(village.x - self.role.x) <= distance and abs(village.y - self.role.y) <= distance:
            if village_id not in self.role.discovery_mgr.get_ids_set():
                self.role.discovery_mgr.add(village_id)

                pack = GotChat(
                    origin_name=self.role.name,
                    chat_type=ChatType.SYSTEM,
                    text=f'discovered {village.name}',
                )
                self.session.send(pack)

                self.session.send(Discovered(village_id=village_id))


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

    def __get_sailable_x_y_around_port(self, port_tile_x, port_tile_y):
        matrix = sMapMaker.world_map_piddle
        deltas = c.TILES_AROUND_PORTS
        for delta in deltas:
            test_tile_x = port_tile_x + delta[1]
            test_tile_y = port_tile_y + delta[0]
            if int(matrix[test_tile_y, test_tile_x]) in c.SAILABLE_TILES:
                sailable = True
                three_nearby_tiles = c.THREE_NEARBY_TILES_OF_UP_LEFT_TILE
                for tile in three_nearby_tiles:
                    if not int(matrix[test_tile_y + tile[1], test_tile_x + tile[0]]) in c.SAILABLE_TILES:
                        sailable = False
                        break

                if sailable:
                    return test_tile_x, test_tile_y

        return None, None

    async def handle_Sail(self, sail):
        # tell port nearby roles
        self.send_role_disappeared_to_nearby_roles()

        # update map_mgr
        port = sObjectMgr.get_port(self.role.map_id)

        sailable_x, sailable_y = self.__get_sailable_x_y_around_port(port.x, port.y)

        if not sailable_x:
            return

        sMapMgr.change_object_map(self.role,
                                  self.role.map_id, self.role.x, self.role.y,
                                  0, sailable_x, sailable_y)

        # update model
        self.role.map_id = 0
        self.role.x = sailable_x
        self.role.y = sailable_y

        # tell client
        self.session.send(
            MapChanged(
                role_id=self.role.id,
                map_id=0,
                x=sailable_x,
                y=sailable_y,
            )
        )

        # tell nearby_roles_at_sea
        self.send_role_appeared_to_nearby_roles()


    async def handle_EnterPort(self, enter_port):
        port_id = enter_port.id

        distance = 3

        port = sObjectMgr.get_port(port_id)
        if abs(port.x - self.role.x) <= distance and abs(port.y - self.role.y) <= distance:
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


    async def handle_FightNpc(self, fight_npc):
        npc_id = fight_npc.npc_id

        npc = sNpcMgr.get_npc(npc_id)

        if not self.role.is_close_to_role(npc):
            return

        self.role.is_moving = False

        # notify nearby roles
        sMapMgr.rm_object(self.role)
        self.send_role_disappeared_to_nearby_roles()

        self.role.battle_npc_id = npc_id

        # gen npc_instance (each role has its own instance)
        npc_instance = copy.deepcopy(npc)
        self.role.npc_instance = npc_instance

        self.role.ship_mgr.init_ships_positions_in_battle(is_attacker=True)
        npc_instance.ship_mgr.init_ships_positions_in_battle(is_attacker=False)

        pack = EnteredBattleWithNpc(
            npc_id=npc_id,
            ships=npc_instance.ship_mgr.gen_ships_prots(),
        )

        self.session.send(pack)

        #### copied
        # init battle_role_id and enemy ships
        # init my ships pos
        for id, ship in self.role.ship_mgr.id_2_ship.items():
            self.session.send(pb.ShipMoved(
                id=id,
                x=ship.x,
                y=ship.y,
            ))

        # init battle_timer (updated each session update)
        self.role.battle_timer = c.BATTLE_TIMER_IN_SECONDS

        pack = BattleTimerStarted(
            battle_timer=self.role.battle_timer,
            role_id=self.role.id,
        )
        self.session.send(pack)



    async def handle_EscapeNpcBattle(self, escape_npc_battle):
        npc_id = escape_npc_battle.npc_id

        self.role.battle_npc_id = None

        self.session.send(EscapedNpcBattle())

        # notify nearby roles
        sMapMgr.add_object(self.role)
        self.send_role_appeared_to_nearby_roles()

    async def handle_SellShip(self, sell_ship):
        id = sell_ship.id

        ship = self.role.ship_mgr.get_ship(id)
        ship_template = sObjectMgr.get_ship_template(ship.ship_template_id)
        sell_price = int(ship_template.buy_price / 2)

        self.role.money += sell_price
        self.role.ship_mgr.rm_ship(id)

        self.session.send(MoneyChanged(money=self.role.money))
        self.session.send(ShipRemoved(id=id))
        self.session.send(PopSomeMenus(cnt=1))

    def __get_ships_to_buy(self, ship_ids):
        ships_to_buy = []

        for id in ship_ids:
            ship_template = sObjectMgr.get_ship_template(id)
            ship_to_buy = ShipToBuy(template_id=id, price=ship_template.buy_price)
            ships_to_buy.append(ship_to_buy)

        return ships_to_buy

    async def handle_GetShipsToBuy(self, get_ships_to_buy):
        port = sObjectMgr.get_port(self.role.map_id)

        ship_ids = sObjectMgr.get_ship_ids(port.economy_id)

        pack = ShipsToBuy()
        ships_to_buy = self.__get_ships_to_buy(ship_ids)
        pack.ships_to_buy.extend(ships_to_buy)
        self.session.send(pack)

    def _gen_ship_proto(self, new_model_ship):
        new_ship_proto = Ship(
            id=new_model_ship.id,
            role_id=new_model_ship.role_id,
            name=new_model_ship.name,
            ship_template_id=new_model_ship.ship_template_id,
            material_type=new_model_ship.material_type,
            now_durability=new_model_ship.now_durability,
            max_durability=new_model_ship.max_durability,
            tacking=new_model_ship.tacking,
            power=new_model_ship.power,
            capacity=new_model_ship.capacity,
            now_crew=new_model_ship.now_crew,
            min_crew=new_model_ship.min_crew,
            max_crew=new_model_ship.max_crew,
            now_guns=new_model_ship.now_guns,
            type_of_guns=new_model_ship.type_of_guns,
            max_guns=new_model_ship.max_guns,
            water=new_model_ship.water,
            food=new_model_ship.food,
            material=new_model_ship.material,
            cannon=new_model_ship.cannon,
            cargo_cnt=new_model_ship.cargo_cnt,
            cargo_id=new_model_ship.cargo_id,
            captain=new_model_ship.captain,
            accountant=new_model_ship.accountant,
            first_mate=new_model_ship.first_mate,
            chief_navigator=new_model_ship.chief_navigator
        )

        return new_ship_proto

    async def handle_BuyShip(self, buy_ship):
        ship_template_id = buy_ship.template_id
        ship_template = sObjectMgr.get_ship_template(ship_template_id)
        price = ship_template.buy_price

        if not self.role.money >= price:
            return

        new_ship_name = self.role.ship_mgr.get_new_ship_name()

        new_model_ship = model.Ship(
            id=sIdMgr.gen_new_ship_id(),
            role_id=self.role.id,

            name=new_ship_name,
            ship_template_id=ship_template_id,

            material_type=0,

            now_durability=ship_template.durability,
            max_durability=ship_template.durability,

            tacking=ship_template.tacking,
            power=ship_template.power,

            capacity=ship_template.capacity,

            now_crew=0,
            min_crew=ship_template.min_crew,
            max_crew=ship_template.max_crew,

            now_guns=0,
            type_of_guns=0,
            max_guns=ship_template.max_guns,

            water=0,
            food=0,
            material=0,
            cannon=0,

            cargo_cnt=0,
            cargo_id=0,
        )

        self.role.money -= price
        self.role.ship_mgr.add_ship(new_model_ship)

        # tell client
        self.session.send(MoneyChanged(money=self.role.money))

        self.session.send(GotNewShip(ship=new_model_ship.gen_ship_proto()))

    async def handle_FightRole(self, fight_role):
        role_id = fight_role.role_id

        target_role = self.session.server.get_role(role_id)

        if not self.role.is_close_to_role(target_role):
            return

        # stop moving
        self.role.is_moving = False
        target_role.is_moving = False

        self.send_role_disappeared_to_nearby_roles()
        target_role.session.packet_handler.send_role_disappeared_to_nearby_roles()

        sMapMgr.rm_object(self.role)
        sMapMgr.rm_object(target_role)

        # init battle_role_id and enemy ships
        self.role.battle_role_id = target_role.id
        target_role.battle_role_id = self.role.id

        self.role.ship_mgr.init_ships_positions_in_battle(is_attacker=True)

        target_role.ship_mgr.init_ships_positions_in_battle(is_attacker=False)

        pack = EnteredBattleWithRole(
            role_id=target_role.id,
            ships=target_role.ship_mgr.gen_ships_prots(),
        )
        self.session.send(pack)

        # init my ships pos
        for id, ship in self.role.ship_mgr.id_2_ship.items():
            self.session.send(pb.ShipMoved(
                id=id,
                x=ship.x,
                y=ship.y,
                dir=ship.dir,
            ))

        pack = EnteredBattleWithRole(
            role_id=self.role.id,
            ships=self.role.ship_mgr.gen_ships_prots(),
        )
        target_role.session.send(pack)

        # init enemy ships pos
        for id, ship in target_role.ship_mgr.id_2_ship.items():
            target_role.session.send(pb.ShipMoved(
                id=id,
                x=ship.x,
                y=ship.y,
                dir=ship.dir,
            ))

        # init battle_timer (updated each session update)
        self.role.battle_timer = c.BATTLE_TIMER_IN_SECONDS

        pack = BattleTimerStarted(
            battle_timer=self.role.battle_timer,
            role_id=self.role.id,
        )
        self.session.send(pack)
        target_role.session.send(pack)


    async def handle_EscapeRoleBattle(self, escape_role_battle):

        # if not self.role.battle_timer:
        #     return

        target_role = self.session.server.get_role(self.role.battle_role_id)

        target_role.session.send(EscapedRoleBattle())
        self.session.send(EscapedRoleBattle())

        target_role.battle_role_id = None
        self.role.battle_role_id = None

        # notify nearby roles
        sMapMgr.add_object(self.role)
        sMapMgr.add_object(target_role)
        self.send_role_appeared_to_nearby_roles()
        target_role.session.packet_handler.send_role_appeared_to_nearby_roles()


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

        if self.role.battle_role_id:
            await self.role.all_ships_attack_role()
        elif self.role.battle_npc_id:
            await self.role.all_ships_attack_npc()

    async def handle_SetAllShipsTarget(self, set_all_ships_target):
        ship_id = set_all_ships_target.ship_id

        self.role.set_all_ships_target(ship_id)

    async def handle_SetAllShipsStrategy(self, set_all_ships_strategy):
        strategy = set_all_ships_strategy.attack_method_type

        self.role.set_all_ships_strategy(strategy)