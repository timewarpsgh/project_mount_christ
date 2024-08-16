from dataclasses import dataclass
import login_pb2 as pb


@dataclass
class Ship:

    id: int=None
    role_id: int=None

    name: str=None
    ship_template_id: int=None


    material_type: int=None

    now_durability: int=None
    max_durability: int=None

    tacking: int=None
    power: int=None

    capacity: int=None

    now_crew: int=None
    min_crew: int=None
    max_crew: int=None

    now_guns: int=None
    type_of_guns: int=None
    max_guns: int=None

    water: int=None
    food: int=None
    material: int=None
    cannon: int=None

    cargo_cnt: int=None
    cargo_id: int=None

    captain: int=None
    accountant: int=None
    first_mate: int=None
    chief_navigator: int=None

    def add_cargo(self, cargo_id, cargo_cnt):
        self.cargo_id = cargo_id
        self.cargo_cnt = cargo_cnt

    def remove_cargo(self, cargo_id, cargo_cnt):
        if self.cargo_id == cargo_id:
            self.cargo_cnt -= cargo_cnt
            if self.cargo_cnt <= 0:
                self.cargo_cnt = 0
                self.cargo_id = 0

@dataclass
class Mate:

    id: int=None
    role_id: int=None

    name: str=None
    img_id: int=None
    nation: str=None

    lv: int=None
    points: int=None
    assigned_duty: str=None
    ship_id: int=None

    leadership: int=None

    navigation: int=None
    accounting: int=None
    battle: int=None

    talent_in_navigation: int=None
    talent_in_accounting: int=None
    talent_in_battle: int=None


class ShipMgr:

    def __init__(self, role):
        self.role = role
        self.id_2_ship = {}

    def get_role(self):
        return self.role

    def add_ship(self, ship):
        self.id_2_ship[ship.id] = ship

    def rm_ship(self, ship_id):
        del self.id_2_ship[ship_id]

    def get_ship(self, ship_id):
        return self.id_2_ship[ship_id]

    def get_new_ship_name(self):
        new_ship_name = str(len(self.id_2_ship) + 1)
        return new_ship_name


class MateMgr:

    def __init__(self, role):
        self.role = role
        self.id_2_mate = {}

    def get_role(self):
        return self.role

    def add_mate(self, mate):
        self.id_2_mate[mate.id] = mate

    def rm_mate(self, mate_id):
        del self.id_2_mate[mate_id]

    def get_mate(self, mate_id):
        return self.id_2_mate.get(mate_id)


class DiscoveryMgr:

    def __init__(self):
        self.ids_set = set()

    def add(self, discovery_id):
        self.ids_set.add(discovery_id)

    def get_ids_set(self):
        return self.ids_set


@dataclass
class Role:
    session: any=None

    id: int=None
    name: str=None
    x: int=None
    y: int=None
    map_id: int=None
    money: int=None
    seen_grids: any=None  # numpy matrix

    ship_mgr: ShipMgr=None
    mate_mgr: MateMgr=None
    discovery_mgr: DiscoveryMgr=None

    battle_npc_id: int=None
    battle_role_id: int=None

    def get_flag_ship(self):
        for id, ship in self.ship_mgr.id_2_ship.items():
            mate_id = ship.captain
            if not mate_id:
                continue

            mate = self.mate_mgr.get_mate(mate_id)
            if mate.name == self.name:
                return ship

    def get_non_flag_ships_ids(self):
        flag_ship = self.get_flag_ship()
        return [id for id, ship in self.ship_mgr.id_2_ship.items() if id != flag_ship.id]


    def is_close_to_role(self, target_role):
        return abs(self.x - target_role.x) <= 1 and abs(self.y - target_role.y) <= 1
    def win(self, target_role):

        for id in target_role.get_non_flag_ships_ids():
            # add to my role
            ship = target_role.ship_mgr.get_ship(id)
            prev_ship_name = ship.name
            ship.name = self.ship_mgr.get_new_ship_name()
            ship.role_id = self.id
            self.ship_mgr.add_ship(ship)

            ship_proto = self.session.packet_handler._gen_new_ship_proto(ship)
            self.session.send(pb.GotNewShip(ship=ship_proto))
            self.session.send(pb.GotChat(
                chat_type=pb.ChatType.SYSTEM,
                text=f'acquired ship {prev_ship_name} as {ship.name}',
            ))

            # remove from target role
            target_role.ship_mgr.rm_ship(id)
            target_role.session.send(pb.ShipRemoved(id=id))
            target_role.session.send(pb.GotChat(
                chat_type=pb.ChatType.SYSTEM,
                text=f'lost ship {prev_ship_name}',
            ))

        # tell client
        self.session.send(pb.EscapedRoleBattle())
        target_role.session.send(pb.EscapedRoleBattle())

        target_role.battle_role_id = None
        self.battle_role_id = None

class Model:

    def __init__(self):
        self.role = None
        self.id_2_role = {}
