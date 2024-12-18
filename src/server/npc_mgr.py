import asyncio

from dataclasses import dataclass
from model import Role, Mate, ShipMgr, Ship, MateMgr
import random
import json

# import from dir
import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\server\models')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\server')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared')
from world_models import Npc as NpcModel, \
    SESSION as WORLD_SESSION

from role_models import SESSION as ROLE_SESSION, \
    Mate as MateModel, \
    Ship as ShipModel

from map_mgr import sMapMgr
from object_mgr import sObjectMgr
from season_mgr import sSeasonMgr
from hash_paths import HASH_PATHS
import login_pb2 as pb
import constants as c


class Path:
    """read only. holds path from one port to another"""
    def __init__(self, start_port_id, end_port_id):
        self.list_of_points = HASH_PATHS[start_port_id][end_port_id][2:-2]

    def get_length(self):
        return len(self.list_of_points)

    def get_wp(self, id):
        return self.list_of_points[id]


@dataclass
class Npc(Role):
    id: str = None

    x: int = None
    y: int = None
    dir: int = None
    map_id: int = None

    mate: Mate = None
    ship_mgr: ShipMgr = None
    battle_timer: int = None

    start_port_id: int = None
    end_port_id: int = 33
    is_outward: bool = True
    now_wp_id: int = 0

    # def get_flag_ship(self):
    #     flag_ship = list(self.ship_mgr.id_2_ship.values())[0]
    #     return flag_ship

    def get_target_port_name(self):
        start_port_name = sObjectMgr.get_port(self.start_port_id).name
        end_port_name = sObjectMgr.get_port(self.end_port_id).name

        if self.is_outward:
            return end_port_name
        else:
            return start_port_name

    def get_nation(self):
        return self.mate.nation

    def move_along_path(self):
        """choose a random end port, reach it, and move back, and loop"""
        # get path and direction
        next_point = self.__get_next_point()
        self.__start_moving_to_next_point(next_point)

    def get_rand_cargo_id(self):
        max_cargo_id = 46
        return random.randint(1, max_cargo_id)

    def __randomize_ships_cargo(self):
        rand_cargo_id = self.get_rand_cargo_id()
        for ship in self.ship_mgr.get_ships():
            ship.cargo_id = rand_cargo_id

    def __get_next_point(self):
        # get path
        path = None

        if self.now_wp_id == 0:
            # init start and end
            self.is_outward = True
            self.end_port_id = random.choice(list(HASH_PATHS[self.start_port_id].keys()))

            # self.end_port_id = 33 # antwerp

            path = Path(self.start_port_id, self.end_port_id)

            self.__randomize_ships_cargo()
        else:
            # get path from start and end ids
            path = Path(self.start_port_id, self.end_port_id)
            if (self.now_wp_id + 1) == path.get_length():
                self.is_outward = False

                self.__randomize_ships_cargo()

        # change index
        if self.is_outward:
            self.now_wp_id += 1
        else:
            self.now_wp_id -= 1

        # get next point and move to it
        next_point = path.get_wp(self.now_wp_id)

        return next_point

    def __start_moving_to_next_point(self, next_point):
        dir = self.__get_dir_to_next_point(next_point)
        self.stopped_moving(next_point[0], next_point[1], dir)

        # self.start_moving(self.x, self.y, dir)

    def __get_dir_to_next_point(self, next_point):
        next_x = next_point[0]
        next_y = next_point[1]

        # get now position
        now_x = self.x
        now_y = self.y

        # get direction
        dir = None

        if next_y < now_y and next_x == now_x:
            dir = pb.DirType.N
        elif next_y > now_y and next_x == now_x:
            dir = pb.DirType.S
        elif next_y == now_y and next_x < now_x:
            dir = pb.DirType.W
        elif next_y == now_y and next_x > now_x:
            dir = pb.DirType.E

        elif next_y < now_y and next_x > now_x:
            dir = pb.DirType.NE
        elif next_y < now_y and next_x < now_x:
            dir = pb.DirType.NW
        elif next_y > now_y and next_x > now_x:
            dir = pb.DirType.SE
        elif next_y > now_y and next_x < now_x:
            dir = pb.DirType.SW

        if next_y == now_y and next_x == now_x:
            dir = pb.DirType.N

        return dir


class NpcMgr:

    def __init__(self):
        self.id_2_npc = {}
        self.__init_id_2_npc()

    def get_npc(self, id):
        return self.id_2_npc.get(id)

    def get_npc_by_nation_and_fleet(self, nation_id, fleet_id):
        npcs = []
        for npc in self.id_2_npc.values():
            if npc.mate.nation == nation_id and npc.mate.fleet == fleet_id:
                npcs.append(npc)

        return npcs

    async def run_loop_to_update(self, server):
        while True:
            prev_time = asyncio.get_event_loop().time()

            sleep_time = c.PIXELS_COVERED_EACH_MOVE / c.NPC_SPEED

            await asyncio.sleep(sleep_time)
            next_time = asyncio.get_event_loop().time()
            time_diff = next_time - prev_time

            await self.update(time_diff)

            # update others
            sSeasonMgr.update(time_diff, server)
            sMapMgr.update(time_diff)

    async def update(self, time_diff):
        # return
        for npc in self.id_2_npc.values():
            # if npc.id == 2000000001:
            npc.move_along_path()
            # await npc.update(time_diff)

    def __get_mate(self, npc_id):
        mate_model = ROLE_SESSION.query(MateModel).filter_by(npc_id=npc_id).first()

        mate = Mate(
            id=mate_model.id,
            duty_type=mate_model.duty_type,
            img_id=mate_model.img_id,
            mate_template_id=mate_model.mate_template_id,
            leadership=mate_model.leadership,
            lv=mate_model.lv,
            name=mate_model.name,
            nation=mate_model.nation,
            fleet=mate_model.fleet,

            points=mate_model.points,
            role_id=mate_model.role_id,
            ship_id=mate_model.ship_id,

            navigation=mate_model.navigation,
            accounting=mate_model.accounting,
            battle=mate_model.battle,

            lv_in_acc=mate_model.lv_in_acc,
            lv_in_bat=mate_model.lv_in_bat,
            lv_in_nav=mate_model.lv_in_nav,

            talent_in_accounting=mate_model.talent_in_accounting,
            talent_in_battle=mate_model.talent_in_battle,
            talent_in_navigation=mate_model.talent_in_navigation,
        )

        return mate

    def __get_ship_mgr(self, npc_id, fleet_type):
        ship_mgr = ShipMgr(None)

        ship_model = ROLE_SESSION.query(ShipModel).filter_by(npc_id=npc_id).first()

        # get ships_cnt and ship_template_id
        if fleet_type == c.Fleet.MERCHANT.value:
            ships_cnt = random.randint(4, 6)
            ship_template_id = random.choice([9, 20])
            type_of_guns = 2
        elif fleet_type == c.Fleet.CONVOY.value:
            ships_cnt = random.randint(6, 8)
            ship_template_id = random.choice([10, 12])
            type_of_guns = 4
        elif fleet_type == c.Fleet.BATTLE.value:
            ships_cnt = random.randint(8, 10)
            ship_template_id = random.choice([11, 21])
            type_of_guns = 6

        ship_template = sObjectMgr.get_ship_template(ship_template_id)

        # for testing
        # ships_cnt = 2
        for i in range(ships_cnt):

            max_cargo = ship_template.capacity - ship_template.max_crew - ship_template.max_guns
            supply_cnt = 20
            cargo_cnt = max_cargo - supply_cnt * 4

            ship = Ship(
                id=ship_model.id + c.NPC_ROLE_START_ID + i,
                role_id=ship_model.role_id,
                ship_template_id=ship_template_id,
                captain=ship_model.captain,
                name=str(i),

                tacking=ship_template.tacking,
                power=ship_template.power,
                material_type=ship_model.material_type,

                now_durability=ship_template.durability,
                max_durability=ship_template.durability,

                capacity=ship_template.capacity,

                min_crew=ship_template.min_crew,
                now_crew=ship_template.max_crew,
                max_crew=ship_template.max_crew,

                max_guns=ship_template.max_guns,
                now_guns=ship_template.max_guns,
                type_of_guns=type_of_guns,

                water=supply_cnt,
                food=supply_cnt,
                material=supply_cnt,
                cannon=supply_cnt,

                cargo_cnt=cargo_cnt,
                cargo_id=None,
            )

            ship_mgr.add_ship(ship)

        return ship_mgr


    def __get_mate_mgr(self, npc_id):
        mate = self.__get_mate(npc_id)
        mate_mgr = MateMgr(None)
        mate_mgr.add_mate(mate)
        return mate_mgr

    def __get_start_port_id(self, nation_id):
        start_port_id = c.NATION_ID_2_PORT_ID[nation_id]
        return start_port_id

    def __init_weapon_and_armor(self, npc):
        fleet = npc.mate.fleet

        if fleet == c.Fleet.MERCHANT.value:
            npc.weapon = 44
            npc.armor = 33
        elif fleet == c.Fleet.CONVOY.value:
            npc.weapon = 52
            npc.armor = 35
        elif fleet == c.Fleet.BATTLE.value:
            npc.weapon = 48
            npc.armor = 37

    def __init_id_2_npc(self):
        for npc_model in WORLD_SESSION.query(NpcModel).all():
            npc = Npc(
                id=npc_model.id,
                mate=self.__get_mate(npc_model.id),
                x=npc_model.x,
                y=npc_model.y,
                dir=npc_model.dir,
                map_id=npc_model.map_id,
                mate_mgr=self.__get_mate_mgr(npc_model.id),

            )
            npc.name = npc.mate.name


            npc.mate_mgr.role = npc

            npc.start_port_id = self.__get_start_port_id(npc.mate.nation)
            npc.ship_mgr = self.__get_ship_mgr(npc_model.id, npc.mate.fleet)
            npc.ship_mgr.role = npc

            # init weapon and armor based on fleet type
            self.__init_weapon_and_armor(npc)

            self.id_2_npc[npc_model.id] = npc

            sMapMgr.add_object(npc)


sNpcMgr = NpcMgr()