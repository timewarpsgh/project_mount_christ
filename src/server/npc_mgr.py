from dataclasses import dataclass
from model import Role, Mate, ShipMgr, Ship

import json

# import from dir
import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\server\models')

from world_models import Npc as NpcModel, \
    SESSION as WORLD_SESSION

from role_models import SESSION as ROLE_SESSION, \
    Mate as MateModel, \
    Ship as ShipModel



@dataclass
class Npc(Role):
    id: int = None

    x: int = None
    y: int = None
    map_id: int = None

    mate: Mate = None
    ship_mgr: ShipMgr = None
    battle_timer: int = None

    def get_flag_ship(self):
        flag_ship = list(self.ship_mgr.id_2_ship.values())[0]
        return flag_ship

class NpcMgr:

    def __init__(self):
        self.id_2_npc = {}
        self.__init_id_2_npc()

    def get_npc(self, id):
        return self.id_2_npc.get(id)

    def __get_mate(self, npc_id):
        mate_model = ROLE_SESSION.query(MateModel).filter_by(npc_id=npc_id).first()

        mate = Mate(
            id=mate_model.id,
            accounting=mate_model.accounting,
            assigned_duty=mate_model.assigned_duty,
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


    def __init_id_2_npc(self):
        for npc_model in WORLD_SESSION.query(NpcModel).all():
            npc = Npc(
                id=npc_model.id,
                mate=self.__get_mate(npc_model.id),
                x=npc_model.x,
                y=npc_model.y,
                map_id=npc_model.map_id,
                ship_mgr=self.__get_ship_mgr(npc_model.id)

            )

            self.id_2_npc[npc_model.id] = npc

            for id, ship in npc.ship_mgr.id_2_ship.items():
                print(ship.name)


sNpcMgr = NpcMgr()