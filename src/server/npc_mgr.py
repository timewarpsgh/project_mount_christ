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
from season_mgr import sSeasonMgr
from hash_paths import HASH_PATHS
import login_pb2 as pb
import constants as c


class Path:
    """read only. holds path from one port to another"""
    def __init__(self, start_port_id, end_port_id):
        self.list_of_points = HASH_PATHS[start_port_id][end_port_id]

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

    start_port_id: int = 30
    end_port_id: int = None
    is_outward: bool = True
    now_wp_id: int = 0

    # def get_flag_ship(self):
    #     flag_ship = list(self.ship_mgr.id_2_ship.values())[0]
    #     return flag_ship

    def move_along_path(self):
        """choose a random end port, reach it, and move back, and loop"""
        # get path and direction
        next_point = self.__get_next_point()
        self.__start_moving_to_next_point(next_point)


    def __get_next_point(self):
        # get path
        path = None

        if self.now_wp_id == 0:
            # init start and end
            self.is_outward = True
            self.end_port_id = random.choice(list(HASH_PATHS[self.start_port_id].keys()))

            # self.end_port_id = 33 # antwerp

            path = Path(self.start_port_id, self.end_port_id)
        else:
            # get path from start and end ids
            path = Path(self.start_port_id, self.end_port_id)
            if (self.now_wp_id + 1) == path.get_length():
                self.is_outward = False

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
        self.start_moving(self.x, self.y, dir)

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


    async def run_loop_to_update(self, server):
        while True:
            prev_time = asyncio.get_event_loop().time()

            sleep_time = c.PIXELS_COVERED_EACH_MOVE / c.NPC_SPEED

            await asyncio.sleep(sleep_time)
            next_time = asyncio.get_event_loop().time()
            time_diff = next_time - prev_time

            await self.update(time_diff)

            sSeasonMgr.update(time_diff, server)

    async def update(self, time_diff):
        # return
        print('npc_mgr updating')
        for npc in self.id_2_npc.values():
            # if npc.id == 2000000001:
            npc.move_along_path()
            print(f'NPC {npc.id} trying to move')
            await npc.update(time_diff)


    def __get_mate(self, npc_id):
        mate_model = ROLE_SESSION.query(MateModel).filter_by(npc_id=npc_id).first()

        mate = Mate(
            id=mate_model.id,
            accounting=mate_model.accounting,
            duty_type=mate_model.duty_type,
            battle=mate_model.battle,
            img_id=mate_model.img_id,
            leadership=mate_model.leadership,
            lv=mate_model.lv,
            name=mate_model.name,
            nation=mate_model.nation,
            navigation=mate_model.navigation,
            points=mate_model.points,
            role_id=mate_model.role_id,
            ship_id=mate_model.ship_id,
            talent_in_accounting=mate_model.talent_in_accounting,
            talent_in_battle=mate_model.talent_in_battle,
            talent_in_navigation=mate_model.talent_in_navigation,
        )

        return mate

    def __get_ship_mgr(self, npc_id):
        ship_mgr = ShipMgr(None)

        ship_models = ROLE_SESSION.query(ShipModel).filter_by(npc_id=npc_id).all()

        for ship_model in ship_models:
            ship = Ship(
                id=ship_model.id,
                accountant=ship_model.accountant,
                cannon=ship_model.cannon,
                capacity=ship_model.capacity,
                captain=ship_model.captain,
                cargo_cnt=ship_model.cargo_cnt,
                cargo_id=ship_model.cargo_id,
                chief_navigator=ship_model.chief_navigator,
                first_mate=ship_model.first_mate,
                food=ship_model.food,
                material=ship_model.material,
                material_type=ship_model.material_type,
                max_crew=ship_model.max_crew,
                max_durability=ship_model.max_durability,
                max_guns=ship_model.max_guns,
                min_crew=ship_model.min_crew,
                name=ship_model.name,
                now_crew=ship_model.now_crew,
                now_durability=ship_model.now_durability,
                now_guns=ship_model.now_guns,
                power=ship_model.power,
                role_id=ship_model.role_id,
                ship_template_id=ship_model.ship_template_id,
                tacking=ship_model.tacking,
                type_of_guns=ship_model.type_of_guns,
                water=ship_model.water,
            )

            ship_mgr.add_ship(ship)

        return ship_mgr


    def __get_mate_mgr(self, npc_id):
        mate = self.__get_mate(npc_id)
        mate_mgr = MateMgr(None)
        mate_mgr.add_mate(mate)
        return mate_mgr

    def __init_id_2_npc(self):
        for npc_model in WORLD_SESSION.query(NpcModel).all():
            npc = Npc(
                id=npc_model.id,
                mate=self.__get_mate(npc_model.id),
                x=npc_model.x,
                y=npc_model.y,
                dir=npc_model.dir,
                map_id=npc_model.map_id,
                ship_mgr=self.__get_ship_mgr(npc_model.id),
                mate_mgr=self.__get_mate_mgr(npc_model.id),

            )
            npc.name = npc.mate.name

            npc.ship_mgr.role = npc
            npc.mate_mgr.role = npc

            self.id_2_npc[npc_model.id] = npc

            sMapMgr.add_object(npc)


sNpcMgr = NpcMgr()