from dataclasses import dataclass


@dataclass
class Ship:
    id: int = None
    role_id: int = None

    name: str = None
    ship_template_id: int = None

    material_type: int = None

    now_durability: int = None
    max_durability: int = None

    tacking: int = None
    power: int = None

    capacity: int = None

    now_crew: int = None
    min_crew: int = None
    max_crew: int = None

    now_guns: int = None
    type_of_guns: int = None
    max_guns: int = None

    water: int = None
    food: int = None
    material: int = None
    cannon: int = None

    cargo_cnt: int = None
    cargo_id: int = None

    captain: int = None
    accountant: int = None
    first_mate: int = None
    chief_navigator: int = None

    def __init__(self, prot_ship):
        self.id = prot_ship.id
        self.role_id = prot_ship.role_id

        self.name = prot_ship.name
        self.ship_template_id = prot_ship.ship_template_id

        self.material_type = prot_ship.material_type

        self.now_durability = prot_ship.now_durability
        self.max_durability = prot_ship.max_durability

        self.tacking = prot_ship.tacking
        self.power = prot_ship.power

        self.capacity = prot_ship.capacity

        self.now_crew = prot_ship.now_crew
        self.min_crew = prot_ship.min_crew
        self.max_crew = prot_ship.max_crew

        self.now_guns = prot_ship.now_guns
        self.type_of_guns = prot_ship.type_of_guns
        self.max_guns = prot_ship.max_guns

        self.water = prot_ship.water
        self.food = prot_ship.food
        self.material = prot_ship.material
        self.cannon = prot_ship.cannon

        self.cargo_cnt = prot_ship.cargo_cnt
        self.cargo_id = prot_ship.cargo_id

        self.captain = prot_ship.captain
        self.accountant = prot_ship.accountant
        self.first_mate = prot_ship.first_mate
        self.chief_navigator = prot_ship.chief_navigator

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
    id: int = None
    role_id: int = None

    name: str = None
    img_id: int = None
    nation: str = None

    lv: int = None
    points: int = None
    assigned_duty: str = None
    ship_id: int = None

    leadership: int = None

    navigation: int = None
    accounting: int = None
    battle: int = None

    talent_in_navigation: int = None
    talent_in_accounting: int = None
    talent_in_battle: int = None


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
    session: any = None

    id: int = None
    name: str = None
    x: int = None
    y: int = None
    map_id: int = None
    money: int = None
    seen_grids: any = None  # numpy matrix

    ship_mgr: ShipMgr = None
    mate_mgr: MateMgr = None
    discovery_mgr: DiscoveryMgr = None

    battle_npc_id: int = None
    battle_role_id: int = None
    battle_timer: int = None
    is_battle_timer_mine: bool = None

class Model:

    def __init__(self):
        self.role = None
        self.id_2_role = {}

    def get_role(self, id):
        return self.id_2_role.get(id)