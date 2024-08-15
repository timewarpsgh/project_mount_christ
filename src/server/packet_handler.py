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

        # notify presence of nearby_roles
        nearby_roles = self.session.server.get_nearby_roles(self.role.id)

        # init packet my_role_appeared
        my_role_appeared = RoleAppeared()
        my_role_appeared.id = self.role.id
        my_role_appeared.name = self.role.name
        my_role_appeared.x = self.role.x
        my_role_appeared.y = self.role.y

        for nearby_role in nearby_roles:
            # init packet role_appeared for one nearby_role
            role_appeared = RoleAppeared()
            role_appeared.id = nearby_role.id
            role_appeared.name = nearby_role.name
            role_appeared.x = nearby_role.x
            role_appeared.y = nearby_role.y

            nearby_role.session.send(my_role_appeared)
            self.session.send(role_appeared)

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

    def __get_grid_xy(self, x, y):
        grid_x = int(y/c.SIZE_OF_ONE_GRID)
        grid_y = int(x/c.SIZE_OF_ONE_GRID)
        return grid_x, grid_y

    async def handle_Move(self, move):
        if move.dir_type == DirType.E:
            self.role.x += 5
        elif move.dir_type == DirType.W:
            self.role.x -= 5
        elif move.dir_type == DirType.N:
            self.role.y -= 5
        elif move.dir_type == DirType.S:
            self.role.y += 5

        # check opened grid?
        grid_x, grid_y = self.__get_grid_xy(self.role.x, self.role.y)
        print(f'{grid_x=}')
        print(f'{grid_y=}')
        if self.role.seen_grids[grid_x][grid_y] == 0:
            self.role.seen_grids[grid_x][grid_y] = 1
            self.session.send(OpenedGrid(grid_x=grid_x, grid_y=grid_y))



        # make packet
        role_moved = RoleMoved()
        role_moved.id = self.role.id
        role_moved.x = self.role.x
        role_moved.y = self.role.y
        role_moved.dir_type = move.dir_type
        self.send_to_nearby_roles(role_moved, include_self=True)

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
        nearby_roles = self.session.server.get_nearby_roles(self.role.id)
        for nearby_role in nearby_roles:
            nearby_role.session.send(packet)

        if include_self:
            self.session.send(packet)

    def __handle_gm_cmd(self, text):
        split_items = text[1:].split()
        cmd = split_items[0]
        params = split_items[1:]

        if cmd == 'map':
            map_id = int(params[0])

            self.role.map_id = map_id

            pack = GotChat(
                origin_name=self.role.name,
                chat_type=ChatType.SYSTEM,
                text=f'map changed to {map_id}',
            )
            self.session.send(pack)

        elif cmd == 'xy':
            x = int(params[0])
            y = int(params[1])

            self.role.x = x
            self.role.y = y

            pack = GotChat(
                origin_name=self.role.name,
                chat_type=ChatType.SYSTEM,
                text=f'xy changed to {x} {y}',
            )
            self.session.send(pack)

            pack = RoleMoved(
                id=self.role.id,
                x=self.role.x,
                y=self.role.y,
                dir_type=DirType.E,
            )
            self.session.send(pack)

        elif cmd == 'win_npc':
            for id, ship in self.role.npc_instance.ship_mgr.id_2_ship.items():
                new_ship_id = sIdMgr.gen_new_ship_id()
                ship.id = new_ship_id
                ship.name = self.role.ship_mgr.get_new_ship_name()
                ship.role_id = self.role.id
                self.role.ship_mgr.add_ship(ship)

            pack = YouWonNpcBattle()
            ships = self.__gen_won_ships(self.role.npc_instance.ship_mgr.id_2_ship)
            pack.ships.extend(ships)
            self.session.send(pack)
            self.session.send(EscapedNpcBattle())

            self.role.npc_instance = None
            self.role.battle_npc_id = None

    def __gen_won_ships(self, id_2_ship):
        ships_prots = []
        for id, ship in id_2_ship.items():
             ship_prot = Ship(
                id=ship.id,
                role_id=self.role.id,
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
             ships_prots.append(ship_prot)

        return ships_prots

    async def handle_Chat(self, chat):
        if chat.chat_type == ChatType.SAY:

            # handle gm cmds
            if chat.text.startswith('.'):
                if self.account.gm_lv:
                   if self.account.gm_lv >= 9:
                        self.__handle_gm_cmd(chat.text)
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
        if abs(village.x - self.role.x) <= 1 and abs(village.y - self.role.y) <= 1:
            if village_id not in self.role.discovery_mgr.get_ids_set():
                self.role.discovery_mgr.add(village_id)

                pack = GotChat(
                    origin_name=self.role.name,
                    chat_type=ChatType.SYSTEM,
                    text=f'discovered {village.name}',
                )
                self.session.send(pack)

                self.session.send(Discovered(village_id=village_id))

    async def handle_Sail(self, sail):
        port = sObjectMgr.get_port(self.role.map_id)

        self.role.map_id = 0
        self.role.x = port.x
        self.role.y = port.y

        packet = MapChanged(
            role_id = self.role.id,
            map_id=0,
            x=port.x,
            y=port.y
        )
        self.send_to_nearby_roles(packet, include_self=True)

    async def handle_EnterPort(self, enter_port):
        port_id = enter_port.id

        port = sObjectMgr.get_port(port_id)
        if abs(port.x - self.role.x) <= 1 and abs(port.y - self.role.y) <= 1:
            # change map_id
            self.role.map_id = port_id

            # change x y to harbor x y
            # should be inited beforehand (later)
            dict = json.loads(port.building_locations)

            harbor_x = dict['4']['x']
            harbor_y = dict['4']['y']

            self.role.x = harbor_x
            self.role.y = harbor_y

            # send map changed packet
            packet = MapChanged(
                role_id=self.role.id,
                map_id=port_id,
                x=harbor_x,
                y=harbor_y,
            )
            self.send_to_nearby_roles(packet, include_self=True)

        else:
            pass


    async def handle_FightNpc(self, fight_npc):
        npc_id = fight_npc.npc_id

        npc = sNpcMgr.get_npc(npc_id)

        if abs(npc.x - self.role.x) <= 1 and abs(npc.y - self.role.y) <= 1:

            self.role.battle_npc_id = npc_id

            # gen npc_instance (each role has its own instance)
            npc_instance = copy.deepcopy(npc)
            self.role.npc_instance = npc_instance

            self.session.send(EnteredBattleWithNpc(npc_id=npc_id))

    async def handle_EscapeNpcBattle(self, escape_npc_battle):
        npc_id = escape_npc_battle.npc_id
        self.session.send(EscapedNpcBattle())


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

    def __gen_new_ship_proto(self, new_model_ship):
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

        self.session.send(GotNewShip(ship=self.__gen_new_ship_proto(new_model_ship)))

