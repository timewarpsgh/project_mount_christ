import random
import sys
import math
from dataclasses import dataclass
import login_pb2 as pb
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared')

import constants as c
from map_maker import sMapMaker
from object_mgr import sObjectMgr


@dataclass
class Friend:

    role_id: int=None
    name: str=None
    is_enemy: bool=False
    is_online: bool=False


class FriendMgr:

    def __init__(self, role_id):
        self.role_id = role_id
        self.id_2_friend = {}

    def load_from_packet(self, proto_friends):
        for proto_friend in proto_friends:
            friend = Friend(
                role_id=proto_friend.role_id,
                name=proto_friend.name,
                is_enemy=proto_friend.is_enemy,
                is_online=proto_friend.is_online
            )
            self.id_2_friend[friend.role_id] = friend


    def add_friend(self, role_id, name, is_enemy, is_online):
        friend = Friend(
            role_id=role_id,
            name=name,
            is_enemy=is_enemy,
            is_online=is_online
        )
        self.id_2_friend[role_id] = friend

    def remove_friend(self, role_id):
        if role_id in self.id_2_friend:
            del self.id_2_friend[role_id]

    def get_friends(self, is_enemy):
        friends = []
        for friend in self.id_2_friend.values():
            if friend.is_enemy == is_enemy:
                friends.append(friend)
        return friends

    def get_friend(self, role_id):
        return self.id_2_friend.get(role_id)


@dataclass
class Ship:
    id: int = None
    role_id: int = None
    role: any = None
    ship_mgr: any = None

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
        self.dir = prot_ship.dir

    def has_cargo(self):
        if self.cargo_id:
            return True
        else:
            return False

    def get_mate(self, mate_id):
        mate = self.ship_mgr.role.mate_mgr.get_mate(mate_id)
        return mate

    def get_captain(self):
        if not self.captain:
            return None
        mate = self.get_mate(self.captain)
        return mate

    def get_chief_navigator(self):
        if not self.chief_navigator:
            return None
        mate = self.get_mate(self.chief_navigator)
        return mate

    def get_base_speed_in_knots(self):
        """
        depends on ship and mate
        """

        # ship conditions
        tacking = self.tacking
        power = self.power

        # navigation skill
        navigation = 0
        captain = self.get_captain()
        if captain:
            navigation = captain.navigation
        chief_navigator = self.get_chief_navigator()
        if captain and chief_navigator:
            navigation = max(captain.navigation, chief_navigator.navigation)

        # calc base_speed(about 100 max)
        base_speed = (tacking + power + navigation) * 0.25

        base_speed_in_knots = base_speed / c.SPEED_2_KNOTS_FACTOR

        if self.now_crew >= self.min_crew:
            pass
        else:
            base_speed_in_knots = base_speed_in_knots * self.now_crew / self.min_crew

        base_speed_in_knots = round(base_speed_in_knots, 2)
        return base_speed_in_knots

    def get_accountant(self):
        if not self.accountant:
            return None
        mate = self.get_mate(self.accountant)
        return mate

    def get_first_mate(self):
        if not self.first_mate:
            return None
        mate = self.get_mate(self.first_mate)
        return mate

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

    def get_max_cargo(self):
        max_cargo = self.capacity - self.max_crew - self.max_guns
        return max_cargo


@dataclass
class Mate:
    id: int = None
    role_id: int = None
    mate_mgr: any = None

    name: str = None
    img_id: int = None
    nation: int = None

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

    def clear_duty(self):
        self.duty_type = None
        self.ship_id = None

    def xp_earned(self, duty_type, amount):
        if duty_type == pb.DutyType.CHIEF_NAVIGATOR:
            self.xp_in_nav += amount

        elif duty_type == pb.DutyType.ACCOUNTANT:
            self.xp_in_acc += amount

        elif duty_type == pb.DutyType.FIRST_MATE:
            self.xp_in_bat += amount

    def lv_uped(self, duty_type, lv, xp, value):
        if duty_type == pb.DutyType.CHIEF_NAVIGATOR:
            self.lv_in_nav = lv
            self.xp_in_nav = xp
            prev_value = self.navigation
            self.navigation = value

        elif duty_type == pb.DutyType.ACCOUNTANT:
            self.lv_in_acc = lv
            self.xp_in_acc = xp
            prev_value = self.accounting
            self.accounting = value

        elif duty_type == pb.DutyType.FIRST_MATE:
            self.lv_in_bat = lv
            self.xp_in_bat = xp
            prev_value = self.battle
            self.battle = value

        return prev_value


class ShipMgr:

    def __init__(self, role):
        self.role = role
        self.id_2_ship = {}

    def get_role(self):
        return self.role

    def add_ship(self, ship):
        self.id_2_ship[ship.id] = ship
        ship.ship_mgr = self

    def rm_ship(self, ship_id):
        if ship_id not in self.id_2_ship:
            return

        if self.role.is_mine():
            ship = self.get_ship(ship_id)
            captain = ship.get_captain()
            if captain:
                captain.clear_duty()

        del self.id_2_ship[ship_id]

    def get_ship(self, ship_id):
        return self.id_2_ship.get(ship_id)

    def get_ships(self):
        return self.id_2_ship.values()

    def has_ship(self, id):
        return id in self.id_2_ship

    def get_total_supply(self, supply_type):
        total_supply = 0
        supply_name = c.INT_2_SUPPLY_NAME[supply_type]
        for ship in self.get_ships():
            total_supply += getattr(ship, supply_name)
        return total_supply

    def get_total_crew(self):
        total_crew = 0
        for ship in self.get_ships():
            total_crew += ship.now_crew
        return total_crew

    def calc_days_at_sea(self):
        total_water = self.get_total_supply(pb.SupplyType.WATER)
        total_food = self.get_total_supply(pb.SupplyType.FOOD)

        total_crew = self.get_total_crew()

        if total_crew <= 0:
            total_crew = 1

        days_based_on_water = total_water // (total_crew * c.SUPPLY_CONSUMPTION_PER_PERSON)
        days_based_on_food = total_food // (total_crew * c.SUPPLY_CONSUMPTION_PER_PERSON)

        days = min(days_based_on_water, days_based_on_food)
        days = int(days)
        return days


class MateMgr:

    def __init__(self, role):
        self.role = role
        self.id_2_mate = {}

    def get_role(self):
        return self.role

    def add_mate(self, mate):
        self.id_2_mate[mate.id] = mate
        mate.mate_mgr = self

    def rm_mate(self, mate_id):
        del self.id_2_mate[mate_id]

    def get_mate(self, mate_id):
        return self.id_2_mate.get(mate_id)

    def get_mates(self):
        return list(self.id_2_mate.values())

    def get_random_mate(self):
        mates = self.get_mates()
        return random.choice(mates)

    def is_mate_in_fleet(self, mate_template):
        mates = self.get_mates()
        for mate in mates:
            if mate.name == mate_template.name:
                return True
        return False

    def assign_duty(self, mate_id, ship_id, duty_type):
        # get mate and ship
        mate = self.get_mate(mate_id)
        ship = self.role.ship_mgr.get_ship(ship_id)

        # clear prev ship
        if mate.ship_id and mate.duty_type:
            prev_ship = self.role.ship_mgr.get_ship(mate.ship_id)
            if prev_ship:
                prev_duty = mate.duty_type
                if prev_duty == pb.DutyType.CAPTAIN:
                    prev_ship.captain = None
                elif prev_duty == pb.DutyType.CHIEF_NAVIGATOR:
                    prev_ship.chief_navigator = None
                elif prev_duty == pb.DutyType.ACCOUNTANT:
                    prev_ship.accountant = None
                elif prev_duty == pb.DutyType.FIRST_MATE:
                    prev_ship.first_mate = None

        # clear prev mate's duty
        if duty_type == pb.DutyType.CAPTAIN:
            if ship.captain:
                prev_mate = self.get_mate(ship.captain)
                prev_mate.duty_type = None
                prev_mate.ship_id = None
        elif duty_type == pb.DutyType.CHIEF_NAVIGATOR:
            if ship.chief_navigator:
                prev_mate = self.get_mate(ship.chief_navigator)
                prev_mate.duty_type = None
                prev_mate.ship_id = None
        elif duty_type == pb.DutyType.ACCOUNTANT:
            if ship.accountant:
                prev_mate = self.get_mate(ship.accountant)
                prev_mate.duty_type = None
                prev_mate.ship_id = None
        elif duty_type == pb.DutyType.FIRST_MATE:
            if ship.first_mate:
                prev_mate = self.get_mate(ship.first_mate)
                prev_mate.duty_type = None
                prev_mate.ship_id = None

        # set mate
        mate.duty_type = duty_type
        mate.ship_id = ship_id

        # set ship
        if duty_type == pb.DutyType.CAPTAIN:
            ship.captain = mate_id
        elif duty_type == pb.DutyType.CHIEF_NAVIGATOR:
            ship.chief_navigator = mate_id
        elif duty_type == pb.DutyType.ACCOUNTANT:
            ship.accountant = mate_id
        elif duty_type == pb.DutyType.FIRST_MATE:
            ship.first_mate = mate_id


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
    move_timer: float = 0
    map_id: int = None
    money: int = None
    items: list[int] = None
    auras: set[int] = None
    seen_grids: any = None  # numpy matrix
    days_at_sea: int = 0

    ship_mgr: ShipMgr = None
    mate_mgr: MateMgr = None
    discovery_mgr: DiscoveryMgr = None
    friend_mgr: FriendMgr = None

    battle_npc_id: int = None
    battle_role_id: int = None
    battle_timer: int = None
    is_battle_timer_mine: bool = None
    has_attacked: bool = False

    ration: int=100
    morale: int=100
    health: int=100

    is_in_building: bool = False

    weapon: int = None
    armor: int = None
    notorities: list[int] = None
    has_treated: bool = False
    has_told_story: bool = False
    treasure_map_id: int = None
    event_id: int = None
    nation: int = None

    trade_role_id: int = None
    trade_money: int = 0
    trade_item_id: int = None
    is_trade_confirmed: bool = False

    is_dynamic_port_npc: bool = False

    def get_port(self):
        return sObjectMgr.get_port(self.map_id)

    def has_tax_free_permit(self):
        if c.Item.TAX_FREE_PERMIT.value in self.items:
            return True
        else:
            return False

    def get_lv(self):
        mate = self.mate_mgr.get_mates()[0]
        lv = max(mate.lv_in_nav, mate.lv_in_acc, mate.lv_in_bat)
        return lv

    def unequip_item(self, item_id):
        if item_id == self.weapon:
            self.weapon = None
        elif item_id == self.armor:
            self.armor = None

    def equip_item(self, item_id):
        if not self.has_item(item_id):
            return

        item = sObjectMgr.get_item(item_id)
        if item.item_type == c.ItemType.WEAPON.value:
            self.weapon = item_id
        elif item.item_type == c.ItemType.ARMOR.value:
            self.armor = item_id

    def has_item(self, item_id):
        return item_id in self.items

    def can_inspect(self, role):
        if self.has_item(c.Item.TELESCOPE.value):
            distance = 10
        else:
            distance = 5

        if abs(self.x - role.x) <= distance and abs(self.y - role.y) <= distance:
            return True
        else:
            return False

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

    def is_man_in_port(self):
        if self.id in c.PORT_MEN_IDS:
            return True
        else:
            return False

    def is_woman_in_port(self):
        if self.id in c.PORT_WOMEN_IDS:
            return True
        else:
            return False

    def is_in_port(self):
        if self.map_id != 0 and self.map_id is not None:
            return True
        else:
            return False

    def is_in_supply_port(self):
        if self.is_in_port():
            if self.map_id > 100:
                return True
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
        if self.is_in_port():
            if self.is_moving and self.dir == dir:
                return

            self.is_moving = True
            self.dir = dir
            self.move_timer = 0
            self.speed = c.PORT_SPEED
        elif self.is_at_sea():
            self.dir = dir
            if not self.move_timer:
                self.move_timer = self.calc_move_timer()
            self.is_moving = True


        self.graphics.client.send(
            pb.StartMoving(
                dir_type=dir,
                src_x=self.x,
                src_y=self.y,
            )
        )

    def stop_moving(self):
        self.is_moving = False

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
            # move bg
            self.graphics.move_port_bg(self.x, self.y)

            # move other roles
            for role in self.graphics.model.get_other_roles():
                x, y = self.get_x_y_between_roles(role, self)
                self.graphics.move_sp_role(role.id, x, y, role.calc_move_timer())

            # move port npcs
            for port_npc in self.graphics.get_port_npcs():
                x, y = port_npc.get_xy_relative_to_role(self)
                port_npc.animation.move_to_smoothly(x, y, self.calc_move_timer())

        elif self.is_at_sea():
            self.graphics.move_sea_bg(self.x, self.y)

            # move other roles
            for role in self.graphics.model.get_other_roles():
                x, y = self.get_x_y_between_roles(role, self)
                self.graphics.move_sp_role(role.id, x, y, role.calc_move_timer())

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
                # change my frame
                self.graphics.sp_role.change_to_next_frame()

                # move bg
                self.graphics.move_port_bg(self.x, self.y)

                # move other roles
                for role in self.graphics.model.get_other_roles():
                    x, y = self.get_x_y_between_roles(role, self)
                    self.graphics.move_sp_role(role.id, x, y, self.calc_move_timer())

                for port_npc in self.graphics.get_port_npcs():
                    x, y = port_npc.get_xy_relative_to_role(self)
                    port_npc.animation.move_to_smoothly(x, y, self.calc_move_timer())

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

        return None

@dataclass
class Npc(Role):
    id: int = None

    x: int = None
    y: int = None
    map_id: int = None

    mate: Mate = None
    ship_mgr: ShipMgr = None


class SeasonMgr:
    season: pb.SeasonType = pb.SeasonType.SPRING
    wind_dir: int = None
    wind_speed: int = None
    current_dir: int = None
    current_speed: int = None

    def change_season(self, season, wind_dir, wind_speed, current_dir, current_speed):
        print(self.season)
        self.season = season
        self.wind_dir = wind_dir
        self.wind_speed = wind_speed
        self.current_dir = current_dir
        self.current_speed = current_speed

class Model:

    def __init__(self):
        self.role = None
        self.id_2_role = {} # other roles
        self.id_2_npc = {}
        self.season_mgr = SeasonMgr()

    def get_other_roles(self):
        return self.id_2_role.values()

    def remove_role(self, role_id):
        if role_id in self.id_2_role:
            del self.id_2_role[role_id]

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

        for role in self.get_other_roles():
            role.update(time_delta)

        for port_npc in self.role.graphics.get_port_npcs():
            port_npc.animation.update(time_delta)

        if self.role.is_at_sea():
            sMapMaker.update(time_delta, self.role)