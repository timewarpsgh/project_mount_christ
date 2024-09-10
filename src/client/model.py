import sys
import math
from dataclasses import dataclass
import login_pb2 as pb
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared')

import constants as c
from map_maker import sMapMaker

@dataclass
class Ship:
    id: int = None
    role_id: int = None
    role: any = None

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

    x: int = None
    y: int = None
    dir: int = pb.DirType.N
    target_ship: any = None
    strategy: pb.AttackMethodType = None
    steps_left: int = None
    num: int = None

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

        self.x = prot_ship.x
        self.y = prot_ship.y

    def add_cargo(self, cargo_id, cargo_cnt):
        self.cargo_id = cargo_id
        self.cargo_cnt = cargo_cnt

    def remove_cargo(self, cargo_id, cargo_cnt):
        if self.cargo_id == cargo_id:
            self.cargo_cnt -= cargo_cnt
            if self.cargo_cnt <= 0:
                self.cargo_cnt = 0
                self.cargo_id = 0

    def set_target_ship(self, ship):
        self.target_ship = ship

    def set_strategy(self, strategy):
        self.strategy = strategy

    def is_alive(self):
        if self.now_crew > 0:
            return True
        else:
            return False

    def is_flag_ship(self):
        if not self.captain:
            return False
        mate = self.role.mate_mgr.get_mate(self.captain)
        if mate.name == self.role.name:
            return True
        else:
            return False

    def get_screen_xy(self, my_flag_ship):
        pixels = c.BATTLE_TILE_SIZE

        x = (self.x - my_flag_ship.x) * pixels + c.WINDOW_WIDTH // 2
        y = (self.y - my_flag_ship.y) * pixels + c.WINDOW_HEIGHT // 2

        return x, y

    def is_target_in_range(self, ship, is_for_engage=False):
        # get distance between self and ship
        distance_squared = (self.x - ship.x) ** 2 + (self.y - ship.y) ** 2

        if is_for_engage:
            max_in_range_distance = c.MAX_ENGAGE_DISTANCE#1.5 # a little more than 1.4
        else:
            max_in_range_distance = c.MAX_SHOOT_DISTANCE  # 3

        if distance_squared <= max_in_range_distance ** 2:
            return True
        else:
            return False

    def __is_angel_in_range(self, angle, angel_range):
        if angle >= angel_range[0] and angle <= angel_range[1]:
            return True
        else:
            return False

    def is_target_in_angle(self, ship):
        # get angle between the ships
        angle = math.atan2(-(ship.y - self.y), ship.x - self.x)
        angle = math.degrees(angle)
        angle_0 = angle
        angle_1 = angle - 360
        angle_2 = angle + 360

        # get angel range based on self.dir

        hex_dir = c.DIR_2_HEX_DIR[self.dir]
        degrees = 60
        dir_angel = 90 - hex_dir * degrees
        angle_range_low = [dir_angel - degrees - degrees, dir_angel - degrees] # 90 degrees
        angle_range_high = [dir_angel + degrees, dir_angel + degrees + degrees] # 90 degrees


        if self.__is_angel_in_range(angle_0, angle_range_low) or \
                self.__is_angel_in_range(angle_0, angle_range_high):
            return True

        if self.__is_angel_in_range(angle_1, angle_range_low) or \
                self.__is_angel_in_range(angle_1, angle_range_high):
            return True

        if self.__is_angel_in_range(angle_2, angle_range_low) or \
                self.__is_angel_in_range(angle_2, angle_range_high):
            return True

        return False

    def can_shoot(self, ship):
        if self.is_target_in_range(ship) and self.is_target_in_angle(ship):
            return True
        else:
            return False

    def can_engage(self, ship):
        if self.is_target_in_range(ship, is_for_engage=True):
            return True
        else:
            return False

@dataclass
class Mate:
    id: int = None
    role_id: int = None

    name: str = None
    img_id: int = None
    nation: str = None

    lv: int = None
    points: int = None
    duty_type: int = None
    ship_id: int = None

    leadership: int = None

    navigation: int = None
    accounting: int = None
    battle: int = None

    talent_in_navigation: int = None
    talent_in_accounting: int = None
    talent_in_battle: int = None

    lv_in_nav: int = None
    lv_in_acc: int = None
    lv_in_bat: int = None

    xp_in_nav: int = None
    xp_in_acc: int = None
    xp_in_bat: int = None

    def __init__(self, prot_mate):
        self.id = prot_mate.id
        self.role_id = prot_mate.role_id

        self.name = prot_mate.name
        self.img_id = prot_mate.img_id
        self.nation = prot_mate.nation

        self.lv = prot_mate.lv
        self.points = prot_mate.points
        self.duty_type = prot_mate.duty_type
        self.ship_id = prot_mate.ship_id

        self.leadership = prot_mate.leadership

        self.navigation = prot_mate.navigation
        self.accounting = prot_mate.accounting
        self.battle = prot_mate.battle

        self.talent_in_navigation = prot_mate.talent_in_navigation
        self.talent_in_accounting = prot_mate.talent_in_accounting
        self.talent_in_battle = prot_mate.talent_in_battle

        self.lv_in_nav = prot_mate.lv_in_nav
        self.lv_in_acc = prot_mate.lv_in_acc
        self.lv_in_bat = prot_mate.lv_in_bat

        self.xp_in_nav = prot_mate.xp_in_nav
        self.xp_in_acc = prot_mate.xp_in_acc
        self.xp_in_bat = prot_mate.xp_in_bat


class ShipMgr:

    def __init__(self, role):
        self.role = role
        self.id_2_ship = {}

    def get_role(self):
        return self.role

    def add_ship(self, ship):
        self.id_2_ship[ship.id] = ship

    def rm_ship(self, ship_id):
        if ship_id not in self.id_2_ship:
            return
        del self.id_2_ship[ship_id]

    def get_ship(self, ship_id):
        return self.id_2_ship[ship_id]

    def get_ships(self):
        return self.id_2_ship.values()

    def has_ship(self, id):
        return id in self.id_2_ship


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

    def get_mates(self):
        return self.id_2_mate.values()

    def is_mate_in_fleet(self, mate_template):
        mates = self.get_mates()
        for mate in mates:
            if mate.name == mate_template.name:
                return True
        return False


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
    graphics: any = None

    id: int = None
    name: str = None
    x: int = None
    y: int = None
    last_x: int = None
    last_y: int = None
    dir: int = None
    is_moving: bool = None
    speed: float = c.PORT_SPEED
    move_timer: float = None
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
    has_attacked: bool = False

    def is_npc(self):
        if self.id > c.NPC_ROLE_START_ID:
            return True
        else:
            return False

    def is_role(self):
        return not self.is_npc()

    def is_mine(self):
        if self.seen_grids is None:
            return False
        else:
            return True

    def is_in_port(self):
        if self.map_id != 0 and self.map_id is not None:
            return True
        else:
            return False

    def is_at_sea(self):
        if self.map_id == 0 and not self.is_in_battle():
            return True
        else:
            return False

    def is_in_battle(self):
        if self.battle_npc_id or self.battle_role_id:
            return True
        else:
            return False

    def is_dir_diagnal(self):
        if self.dir in [pb.DirType.NW, pb.DirType.NE, pb.DirType.SW, pb.DirType.SE]:
            return True
        else:
            return False

    def start_moving(self, dir):
        self.is_moving = True
        self.dir = dir
        self.move_timer = 0

        if self.is_in_port():
            self.speed = c.PORT_SPEED
        elif self.is_at_sea():
            self.speed = c.PORT_SPEED


        self.graphics.client.send(
            pb.StartMoving(
                dir_type=dir,
                src_x=self.x,
                src_y=self.y,
            )
        )

    def stop_moving(self):
        self.is_moving = False
        print(f'stopped moving at {self.x} {self.y}')

        if self.is_mine():
            pack = pb.StopMoving(
                x=self.x,
                y=self.y,
                dir=self.dir,
            )
            self.graphics.client.send(pack)

    def stopped_moving(self, src_x, src_y, dir):

        self.is_moving = False
        self.x = src_x
        self.y = src_y
        self.dir = dir

        if self.is_in_port():
            self.graphics.move_port_bg(self.x, self.y)
        elif self.is_at_sea():
            self.graphics.move_sea_bg(self.x, self.y)

    def move(self, dir):
        # can move?
        if self.is_in_port():
            if not sMapMaker.can_move_in_port(self.map_id, self.x, self.y, dir):
                return
        elif self.is_at_sea():
            if not sMapMaker.can_move_at_sea(self.x, self.y, dir):
                alt_dir = sMapMaker.get_alt_dir_at_sea(self.x, self.y, dir)
                if not alt_dir:

                    # don't send stop pack is not my role
                    if self.is_mine():
                        self.stop_moving()
                    return
                self.move(alt_dir)
                return

        self.last_x = self.x
        self.last_y = self.y

        distance = 1

        if dir == pb.DirType.E:
            self.x += distance
        elif dir == pb.DirType.W:
            self.x -= distance
        elif dir == pb.DirType.N:
            self.y -= distance
        elif dir == pb.DirType.S:
            self.y += distance

        elif dir == pb.DirType.NE:
            self.x += distance
            self.y -= distance
        elif dir == pb.DirType.NW:
            self.x -= distance
            self.y -= distance
        elif dir == pb.DirType.SE:
            self.x += distance
            self.y += distance
        elif dir == pb.DirType.SW:
            self.x -= distance
            self.y += distance

        # in port
        if self.is_in_port():

            # other role
            if not self.is_mine():
                # update pos
                x, y = self.get_x_y_between_roles(self, self.graphics.model.role)
                self.graphics.move_sp_role(self.id, x, y, self.calc_move_timer())
                self.graphics.get_sp_role(self.id).change_to_next_frame()
                return

            # my role
            else:
                self.graphics.sp_role.change_to_next_frame()
                self.graphics.move_port_bg(self.x, self.y)

                # move other roles
                for id, role in self.graphics.model.id_2_role.items():
                    x, y = self.get_x_y_between_roles(role, self)
                    self.graphics.move_sp_role(id, x, y, self.calc_move_timer())


        # at sea
        elif self.is_at_sea():
            # other role
            if not self.is_mine():
                x, y = self.get_x_y_between_roles(self, self.graphics.model.role)
                self.graphics.move_sp_role(self.id, x, y, self.calc_move_timer())
                self.graphics.get_sp_role(self.id).change_to_next_frame()
                return

            # my role
            else:
                self.graphics.sp_role.change_to_next_frame()
                self.graphics.move_sea_bg(self.x, self.y)

                # move other roles
                for id, role in self.graphics.model.id_2_role.items():
                    x, y = self.get_x_y_between_roles(role, self)
                    self.graphics.move_sp_role(id, x, y, self.calc_move_timer())

    def get_x_y_between_roles(self, role1, role2):
        x = (role1.x - role2.x) * c.PIXELS_COVERED_EACH_MOVE \
            + c.WINDOW_WIDTH // 2
        y = (role1.y - role2.y) * c.PIXELS_COVERED_EACH_MOVE \
            + c.WINDOW_HEIGHT // 2
        return x, y

    def calc_move_timer(self):
        if self.is_dir_diagnal():
            move_timer = 1.41 * c.PIXELS_COVERED_EACH_MOVE / self.speed
        else:
            move_timer = c.PIXELS_COVERED_EACH_MOVE / self.speed
        return move_timer

    def update(self, time_diff):
        # movment
        if self.is_moving:
            self.move_timer -= time_diff
            if self.move_timer <= 0:
                self.move(self.dir)
                self.move_timer = self.calc_move_timer()

    def get_enemy(self):
        return self.graphics.model.get_enemy()

    def set_all_ships_target(self, ship_id):
        enemy = self.get_enemy()

        target_ship = enemy.ship_mgr.get_ship(ship_id)

        for ship in self.ship_mgr.get_ships():
            ship.set_target_ship(target_ship)

    def set_all_ships_strategy(self, strategy):
        for ship in self.ship_mgr.get_ships():
            ship.set_strategy(strategy)

    def set_ship_target(self, ship_id, target_ship_id):
        ship = self.ship_mgr.get_ship(ship_id)
        target_ship = self.get_enemy().ship_mgr.get_ship(target_ship_id)
        ship.set_target_ship(target_ship)

    def set_ship_strategy(self, ship_id, strategy):
        ship = self.ship_mgr.get_ship(ship_id)
        ship.set_strategy(strategy)

    def get_flag_ship(self):
        for id, ship in self.ship_mgr.id_2_ship.items():
            mate_id = ship.captain
            if not mate_id:
                continue

            mate = self.mate_mgr.get_mate(mate_id)
            if mate.name == self.name:
                return ship

@dataclass
class Npc(Role):
    id: int = None

    x: int = None
    y: int = None
    map_id: int = None

    mate: Mate = None
    ship_mgr: ShipMgr = None


class Model:

    def __init__(self):
        self.role = None
        self.id_2_role = {} # other roles
        self.id_2_npc = {}

    def add_role(self, role):
        self.id_2_role[role.id] = role

    def add_npc(self, npc):
        self.id_2_npc[npc.id] = npc

    def get_npc_by_id(self, id):
        return self.id_2_npc.get(id)

    def get_role_by_id(self, id):
        return self.id_2_role.get(id)

    def get_enemy_npc(self):
        if not self.role.battle_npc_id:
            return None
        return self.get_npc_by_id(self.role.battle_npc_id)

    def get_enemy_role(self):
        if not self.role.battle_role_id:
            return None

        return self.get_role_by_id(self.role.battle_role_id)

    def get_enemy(self):
        enemy_role = self.get_enemy_role()
        if enemy_role:
            return enemy_role
        else:
            return self.get_enemy_npc()

    def get_ship_in_battle_by_id(self, id):

        if id in self.role.ship_mgr.id_2_ship:
            return self.role.ship_mgr.get_ship(id)

        elif self.role.battle_npc_id:
            return self.get_enemy_npc().ship_mgr.get_ship(id)

        else:
            return self.get_enemy_role().ship_mgr.get_ship(id)

    def update(self, time_delta):
        if not self.role:
            return

        self.role.update(time_delta)

        for id, role in self.id_2_role.items():
            role.update(time_delta)