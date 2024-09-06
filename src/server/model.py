from dataclasses import dataclass
import asyncio
import random
import login_pb2 as pb
import math
import numpy
from enum import Enum, auto

# import from dir
import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared')

import constants as c
from object_mgr import sObjectMgr
from map_maker import sMapMaker
from map_mgr import sMapMgr
from helpers import Point, are_vectors_in_same_direction


@dataclass
class Ship:

    id: int=None
    role_id: int=None
    role: any=None

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

    x: int=None
    y: int=None
    dir: int=pb.DirType.N
    target_ship: any=None
    strategy: pb.AttackMethodType=pb.AttackMethodType.SHOOT
    steps_left: int=c.STEPS_LEFT


    def reset_steps_left(self):
        self.steps_left = c.STEPS_LEFT

    def add_cargo(self, cargo_id, cargo_cnt):
        self.cargo_id = cargo_id
        self.cargo_cnt = cargo_cnt

    def remove_cargo(self, cargo_id, cargo_cnt):
        if self.cargo_id == cargo_id:
            self.cargo_cnt -= cargo_cnt
            if self.cargo_cnt <= 0:
                self.cargo_cnt = 0
                self.cargo_id = 0

    def shoot(self, ship):
        self.cannon -= 1

        damage = c.SHOOT_DAMAGE
        ship.now_durability -= damage

        is_sunk = False
        if ship.now_durability <= 0:
            is_sunk = True

        # send packs
        pack = pb.ShipAttacked(
            src_id=self.id,
            dst_id=ship.id,
            attack_method_type=pb.AttackMethodType.SHOOT,
            dst_damage=damage,
        )
        self.role.send_to_self_and_enemy(pack)

        pack = pb.GotChat(
            text=f"{self.name} at {self.x} {self.y} shot {ship.name} at {ship.x} {ship.y} and dealt {damage} damage",
            chat_type=pb.ChatType.SYSTEM
        )
        self.role.send_to_self_and_enemy(pack)

        return damage, is_sunk

    def engage(self, ship):
        self_dmg = c.ENGAGE_SELF_DAMAGE
        target_dmg = c.ENGAGE_TARGET_DAMAGE
        self.now_crew -= self_dmg
        ship.now_crew -= target_dmg


        is_target_dead = False
        if ship.now_crew <= 0:
            is_target_dead = True

        is_self_dead = False
        if self.now_crew <= 0:
            is_self_dead = True

        # send packs
        pack = pb.ShipAttacked(
            src_id=self.id,
            dst_id=ship.id,
            attack_method_type=pb.AttackMethodType.ENGAGE,
            dst_damage=target_dmg,
            src_damage=self_dmg,
        )
        self.role.send_to_self_and_enemy(pack)

        pack = pb.GotChat(
            text=f"{self.name} at {self.x} {self.y} engaged {ship.name} at {ship.x} {ship.y} "
                 f"and dealt {self_dmg} to self and {target_dmg} to enemy ",
            chat_type=pb.ChatType.SYSTEM
        )
        self.role.send_to_self_and_enemy(pack)

        return is_self_dead, is_target_dead

    def is_alive(self):
        if self.now_crew > 0:
            return True
        else:
            return False

    def move(self, dir):
        if self.steps_left <= 0:
            return

        self.steps_left -= 1


        self.dir = dir

        if dir == pb.DirType.N:
            self.y -= 1
        elif dir == pb.DirType.S:
            self.y += 1

        elif dir == pb.DirType.NE:
            self.x += 1
            self.y -= 0.5
        elif dir == pb.DirType.SE:
            self.x += 1
            self.y += 0.5
        elif dir == pb.DirType.SW:
            self.x -= 1
            self.y += 0.5
        elif dir == pb.DirType.NW:
            self.x -= 1
            self.y -= 0.5

        pack = pb.ShipMoved(
            id=self.id,
            x=self.x,
            y=self.y,
            dir=self.dir,
            steps_left=self.steps_left,
        )
        self.role.send_to_self_and_enemy(pack)


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

    def move_in_cur_dir(self):
        self.move(self.dir)

    def move_to_left(self):
        new_dir = self.dir - 1
        if new_dir < 0:
            new_dir = 7
        if new_dir in [2, 6]:
            new_dir -= 1

        self.move(new_dir)

    def move_to_right(self):
        new_dir = self.dir + 1
        if new_dir > 7:
            new_dir = 0
        if new_dir in [2, 6]:
            new_dir += 1
        self.move(new_dir)

    def __is_target_point_left_of_vector(self, vector, target_point):
        """ A,B: points of the vector
            M: point to check
        """
        A = vector[0]
        B = vector[1]

        res = (B.x - A.x) * (target_point.y - A.y) - \
              (B.y - A.y) * (target_point.x - A.x)
        if res > 0:
            return True
        else:
            return False

    def __is_target_point_on_vector(self, vector, target_point):
        """ A,B: points of the vector
            M: point to check
        """
        A = vector[0]
        B = vector[1]

        res = (B.x - A.x) * (target_point.y - A.y) - \
              (B.y - A.y) * (target_point.x - A.x)
        if res == 0:
            return True
        else:
            return False

    def __try_to_move_to_left(self):
        if self.__can_move_to_left():
            self.move_to_left()
        elif self.__can_move_in_cur_dir():
            self.move_in_cur_dir()
        elif self.__can_move_to_right():
            self.move_to_right()

    def __try_to_move_in_cur_dir(self):
        if self.__can_move_in_cur_dir():
            self.move_in_cur_dir()
        elif self.__can_move_to_left():
            self.move_to_left()
        elif self.__can_move_to_right():
            self.move_to_right()

    def __try_to_move_to_right(self):
        if self.__can_move_to_right():
            self.move_to_right()
        elif self.__can_move_in_cur_dir():
            self.move_in_cur_dir()
        elif self.__can_move_to_left():
            self.move_to_left()

    def __can_move_to_right(self):
        next_dir = self.dir + 1
        if next_dir > 7:
            next_dir = 0
        if next_dir in [2, 6]:
            next_dir += 1

        return self.__can_move(next_dir)

    def __can_move_to_left(self):
        next_dir = self.dir - 1
        if next_dir < 0:
            next_dir = 7
        if next_dir in [2, 6]:
            next_dir -= 1

        return self.__can_move(next_dir)

    def __can_move_in_cur_dir(self):
        return self.__can_move(self.dir)

    def __can_move(self, dir):
        if self.steps_left <= 0:
            return False

        # get future x,y
        future_x = self.x
        future_y = self.y

        if dir == pb.DirType.N:
            future_y -= 1
        elif dir == pb.DirType.S:
            future_y += 1

        elif dir == pb.DirType.NE:
            future_x += 1
            future_y -= 0.5
        elif dir == pb.DirType.SE:
            future_x += 1
            future_y += 0.5
        elif dir == pb.DirType.SW:
            future_x -= 1
            future_y += 0.5
        elif dir == pb.DirType.NW:
            future_x -= 1
            future_y -= 0.5

        # collide with any of my ships?
        for ship in self.role.ship_mgr.get_ships():
            if ship.x == future_x and ship.y == future_y:
                print(f' collide with my ship at {future_x, future_y}')
                return False

        # collide with any of enemy ships?
        enemy = self.role.get_enemy()
        for ship in enemy.ship_mgr.get_ships():
            if ship.x == future_x and ship.y == future_y:
                return False

        # return ture
        return True

    def move_closer(self, ship):
        # target point when self is origin
        target_point = Point(ship.x - self.x, self.y - ship.y)

        vector = c.DIR_2_VECTOR[self.dir]

        is_target_left = self.__is_target_point_left_of_vector(vector, target_point)
        if is_target_left:
            self.__try_to_move_to_left()
        else:
            are_same_dir = are_vectors_in_same_direction(vector[1], target_point)
            if are_same_dir:
                self.__try_to_move_in_cur_dir()
            else:
                # right or 180 degrees
                self.__try_to_move_to_right()

    def move_further(self, ship):
        # target point when self is origin
        target_point = Point(ship.x - self.x, self.y - ship.y)

        vector = c.DIR_2_VECTOR[self.dir]

        is_target_left = self.__is_target_point_left_of_vector(vector, target_point)
        if is_target_left:
            self.__try_to_move_to_right()
        else:
            is_target_point_on_vector = self.__is_target_point_on_vector(vector, target_point)
            if is_target_point_on_vector:
                are_same_dir = are_vectors_in_same_direction(vector[1], target_point)
                if not are_same_dir:
                    self.__try_to_move_in_cur_dir()
                else:
                    self.__try_to_move_to_left()
            else:
                # right or 180 degrees
                self.__try_to_move_to_left()

    async def try_to_shoot(self, enemy_role, flag_ship)->bool:
        """returns has_won"""
        has_won = False

        target_ship = self.target_ship

        # move and check is_in_range
        has_attacked = False
        left_steps = 3
        for i in range(left_steps):
            await asyncio.sleep(0.3)

            if self.is_target_in_range(target_ship):
                if self.is_target_in_angle(target_ship):
                    damage, is_target_sunk = self.shoot(target_ship)
                    has_attacked = True
                    break
                else:
                    self.move_further(target_ship)
            else:
                self.move_closer(target_ship)


        # if has_attacked and target is_sunk
        if has_attacked and is_target_sunk:

            if target_ship.id == flag_ship.id:
                self.role.win(enemy_role)
                has_won = True
                return has_won

            if target_ship.id not in enemy_role.ship_mgr.id_2_ship:
                return has_won

            enemy_role.ship_mgr.rm_ship(target_ship.id)

        return has_won

    async def try_to_engage(self, enemy_role, flag_ship):
        """returns has_won"""
        has_won = False

        target_ship = self.target_ship

        # move and check is_in_range
        has_attacked = False
        left_steps = 3
        for i in range(left_steps):
            await asyncio.sleep(0.3)

            if self.is_target_in_range(target_ship, is_for_engage=True):
                is_self_dead, is_target_dead = self.engage(target_ship)
                has_attacked = True
                break
            else:
                self.move_closer(target_ship)


        # if has_attacked and target is_sunk
        if has_attacked:
            if is_target_dead:
                if target_ship.id == flag_ship.id:
                    self.role.win(enemy_role)
                    has_won = True
                    return has_won
            elif is_self_dead:
                pass

        return has_won

    async def __try_to_flee(self):
        left_steps = 3
        for i in range(left_steps):
            self.move_further(self.target_ship)
            await asyncio.sleep(0.3)

    async def __try_to_hold(self):
        left_steps = 3
        for i in range(left_steps):
            pass
            await asyncio.sleep(0.3)

    async def move_based_on_strategy(self, enemy, enemy_flag_ship):
        # shoot or engage based on strategy
        has_won = False

        if self.strategy == pb.AttackMethodType.SHOOT:
            has_won = await self.try_to_shoot(enemy, enemy_flag_ship)
        elif self.strategy == pb.AttackMethodType.ENGAGE:
            has_won = await self.try_to_engage(enemy, enemy_flag_ship)
        elif self.strategy == pb.AttackMethodType.FLEE:
            await self.__try_to_flee()
        elif self.strategy == pb.AttackMethodType.HOLD:
            await self.__try_to_hold()

        return has_won

    def gen_ship_proto(self):
        ship_proto = pb.Ship(
            id=self.id,
            role_id=self.role_id,
            name=self.name,
            ship_template_id=self.ship_template_id,
            material_type=self.material_type,
            now_durability=self.now_durability,
            max_durability=self.max_durability,
            tacking=self.tacking,
            power=self.power,
            capacity=self.capacity,
            now_crew=self.now_crew,
            min_crew=self.min_crew,
            max_crew=self.max_crew,
            now_guns=self.now_guns,
            type_of_guns=self.type_of_guns,
            max_guns=self.max_guns,
            water=self.water,
            food=self.food,
            material=self.material,
            cannon=self.cannon,
            cargo_cnt=self.cargo_cnt,
            cargo_id=self.cargo_id,
            captain=self.captain,
            accountant=self.accountant,
            first_mate=self.first_mate,
            chief_navigator=self.chief_navigator,
            x=self.x,
            y=self.y,
        )

        return ship_proto

    def set_random_target_ship(self, enemy):
        if not self.target_ship:
            self.target_ship = enemy.get_random_ship()
        else:
            if self.target_ship.id not in enemy.ship_mgr.id_2_ship:
                self.target_ship = enemy.get_random_ship()
            elif not self.target_ship.is_alive():
                self.target_ship = enemy.get_random_ship()

    def set_random_strategy(self):
        if self.strategy is None:
            strategy = random.choice([pb.AttackMethodType.SHOOT, pb.AttackMethodType.ENGAGE])
            self.strategy = strategy

    def set_target_ship(self, ship):
        self.target_ship = ship

    def set_strategy(self, strategy):
        self.strategy = strategy

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

        pack = pb.ShipRemoved(
            id=ship_id
        )
        self.role.send_to_self_and_enemy(pack)


    def get_ship(self, ship_id):
        return self.id_2_ship[ship_id]

    def get_ships(self):
        return self.id_2_ship.values()

    def get_new_ship_name(self):
        new_ship_name = str(len(self.id_2_ship) + 1)
        return new_ship_name

    def init_ships_positions_in_battle(self, is_attacker=True):
        # initial x need to satisfy hex movement
        for id, ship in enumerate(self.id_2_ship.values()):

            ship.role = self.role

            if is_attacker:
                ship.x = 5
                ship.y = 3 + id * 2
            else:
                ship.x = 11
                ship.y = 3 + id * 2

    def gen_ships_prots(self):
        ships_prots = []
        for ship in self.id_2_ship.values():
             ship_proto = ship.gen_ship_proto()
             ships_prots.append(ship_proto)

        return ships_prots

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
    dir: int=None
    is_moving: bool=False
    speed: float=None
    move_timer: int=None
    map_id: int=None
    money: int=None
    seen_grids: any=None  # numpy matrix

    ship_mgr: ShipMgr=None
    mate_mgr: MateMgr=None
    discovery_mgr: DiscoveryMgr=None

    battle_npc_id: int=None
    battle_role_id: int=None
    battle_timer: int=None
    npc_instance: any=None
    battle_role: any=None

    def __get_grid_xy(self, x, y):
        grid_x = int(y / c.SIZE_OF_ONE_GRID)
        grid_y = int(x / c.SIZE_OF_ONE_GRID)
        return grid_x, grid_y

    def is_npc(self):
        if self.session:
            return False
        else:
            return True

    def is_in_battle_with_role(self):
        if self.battle_role_id:
            return True
        else:
            return False

    def is_in_battle_with_npc(self):
        if self.battle_npc_id:
            return True
        else:
            return False

    def is_role(self):
        if self.session:
            return True
        else:
            return False

    def stop_moving(self):
        self.is_moving = False

        print(f'{self.id} stopped moving at {self.x} {self.y}')

        # send stopped moving to nearby clients

        # pack = pb.StopMoving(
        #     x=self.x,
        #     y=self.y,
        #     dir=self.dir,
        # )
        # self.graphics.client.send(pack)

    def move(self, dir):
        # can move?
        if self.is_in_port():
            return

            if not sMapMaker.can_move_in_port(self.map_id, self.x, self.y, dir):
                return
        elif self.is_at_sea():
            if not sMapMaker.can_move_at_sea(self.x, self.y, dir):
                alt_dir = sMapMaker.get_alt_dir_at_sea(self.x, self.y, dir)
                if not alt_dir:
                    self.stop_moving()
                    return
                self.move(alt_dir)
                return

        old_x = self.x
        old_y = self.y

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

        # print(f'{self.id} moved to {self.x} {self.y}')

        # change cell maybe
        sMapMgr.move_object(self, old_x, old_y, self.x, self.y)

        # check opened grid?
        if self.is_npc():
            return

        grid_x, grid_y = self.__get_grid_xy(self.x, self.y)
        if self.seen_grids[grid_x][grid_y] == 0:
            self.seen_grids[grid_x][grid_y] = 1
            self.session.send(pb.OpenedGrid(grid_x=grid_x, grid_y=grid_y))

    def enter_port(self, port_id):


        # change map_id
        self.map_id = port_id
        harbor_x, harbor_y = sObjectMgr.get_building_xy_in_port(building_id=4, port_id=port_id)

        self.x = harbor_x
        self.y = harbor_y

        # send map changed packet
        packet = pb.MapChanged(
            role_id=self.id,
            map_id=port_id,
            x=harbor_x,
            y=harbor_y,
        )
        self.session.send(packet)

    def get_enemy_role(self):
        """sometimes not working??"""
        return self.session.packet_handler.get_enemy_role()

    def get_enemy(self):
        if self.is_role():
            if self.is_in_battle_with_role():
                return self.session.packet_handler.get_enemy_role()
            elif self.is_in_battle_with_npc():
                return self.npc_instance
        elif self.is_npc():
            if self.is_in_battle_with_role():
                return self.battle_role

    def get_flag_ship(self):
        for ship in self.ship_mgr.get_ships():
            mate_id = ship.captain
            if not mate_id:
                continue

            mate = self.mate_mgr.get_mate(mate_id)
            if mate.name == self.name:
                return ship


    def get_random_ship(self):
        alive_ships = [ship for ship in self.ship_mgr.get_ships() if ship.is_alive()]
        return random.choice(alive_ships)

    def get_non_flag_ships_ids(self):
        flag_ship = self.get_flag_ship()
        return [id for id, ship in self.ship_mgr.id_2_ship.items() if id != flag_ship.id]


    def is_close_to_role(self, target_role):
        distance = 3
        return abs(self.x - target_role.x) <= distance and abs(self.y - target_role.y) <= distance

    def win(self, target_role):

        for id in target_role.get_non_flag_ships_ids():
            print(f'## non flagship id {id}')

            # add to my role
            ship = target_role.ship_mgr.get_ship(id)
            prev_ship_name = ship.name
            ship.name = self.ship_mgr.get_new_ship_name()
            ship.role_id = self.id
            self.ship_mgr.add_ship(ship)

            ship_proto = ship.gen_ship_proto()
            self.session.send(pb.GotNewShip(ship=ship_proto))
            self.session.send(pb.GotChat(
                chat_type=pb.ChatType.SYSTEM,
                text=f'acquired ship {prev_ship_name} as {ship.name}',
            ))

            # remove from target role
            del target_role.ship_mgr.id_2_ship[id]
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

        # notify nearby roles
        sMapMgr.add_object(self)
        sMapMgr.add_object(target_role)
        self.session.packet_handler.send_role_appeared_to_nearby_roles()
        target_role.session.packet_handler.send_role_appeared_to_nearby_roles()

    async def switch_turn_with_enemy(self):
        if self.is_role():

            # set mine to none
            self.battle_timer = None

            # enemy is role
            if self.is_in_battle_with_role():
                enemy_role = self.session.packet_handler.get_enemy_role()
                enemy_role.battle_timer = c.BATTLE_TIMER_IN_SECONDS

                pack = pb.BattleTimerStarted(
                    battle_timer=enemy_role.battle_timer,
                    role_id=enemy_role.id,
                )
                self.session.send(pack)
                enemy_role.session.send(pack)

            # if enemy is npc
            elif self.is_in_battle_with_npc():
                enemy_npc = self.get_enemy()
                enemy_npc.battle_timer = c.BATTLE_TIMER_IN_SECONDS

                pack = pb.BattleTimerStarted(
                    battle_timer=enemy_npc.battle_timer,
                    role_id=0,
                )
                self.session.send(pack)

                # enemy npc attack
                await enemy_npc.all_ships_attack_role()

        elif self.is_npc():
            if self.is_in_battle_with_role():
                role = self.battle_role
                role.battle_timer = c.BATTLE_TIMER_IN_SECONDS
                pack = pb.BattleTimerStarted(
                    battle_timer=role.battle_timer,
                    role_id=role.id,
                )
                role.session.send(pack)

    async def update(self, time_diff):
        # movment
        if self.is_moving:
            self.move_timer -= time_diff
            if self.move_timer <= 0:
                self.move(self.dir)
                self.move_timer = self.calc_move_timer()

        # battle timer
        if self.battle_timer:
            self.battle_timer -= time_diff

            if self.battle_timer <= 0:
                await self.switch_turn_with_enemy()

    def win_npc(self):
        for id, ship in self.npc_instance.ship_mgr.id_2_ship.items():
            new_ship_id = self.session.server.id_mgr.gen_new_ship_id()
            ship.id = new_ship_id
            ship.name = self.ship_mgr.get_new_ship_name()
            ship.role_id = self.id
            self.ship_mgr.add_ship(ship)

        pack = pb.YouWonNpcBattle()
        ships_prots = self.npc_instance.ship_mgr.gen_ships_prots()
        pack.ships.extend(ships_prots)
        self.session.send(pack)
        self.session.send(pb.EscapedNpcBattle())

        self.npc_instance = None
        self.battle_npc_id = None

        # notify nearby roles
        sMapMgr.add_object(self)
        self.session.packet_handler.send_role_appeared_to_nearby_roles()

    def lose_to_npc(self):
        for id in self.get_non_flag_ships_ids():
            self.ship_mgr.rm_ship(id)
            self.session.send(pb.ShipRemoved(id=id))

        self.session.send(pb.EscapedNpcBattle())

        self.npc_instance = None
        self.battle_npc_id = None

        # notify nearby roles
        sMapMgr.add_object(self)
        self.send_role_appeared_to_nearby_roles()


    def send_to_self_and_enemy(self, pack):
        if self.is_role():
            if self.is_in_battle_with_role():
                self.session.packet_handler.send_to_self_and_enemy(pack)
            elif self.is_in_battle_with_npc():
                self.session.send(pack)

        elif self.is_npc():
            if self.is_in_battle_with_role():
                self.battle_role.session.send(pack)

    async def all_ships_attack_role(self, include_flagship=True):
        # get enemy role and flag_ship
        enemy = self.get_enemy()
        enemy_flag_ship = enemy.get_flag_ship()
        my_flag_ship = self.get_flag_ship()

        # for each ship
        for ship in self.ship_mgr.get_ships():
            if not ship.is_alive():
                continue

            # wait some time
            await asyncio.sleep(0.6)

            # include flagship?
            if not include_flagship:
                if ship.id == my_flag_ship.id:
                    continue

            ship.set_random_target_ship(enemy)
            ship.set_random_strategy()
            ship.reset_steps_left()

            # move_based_on_strategy
            has_won = await ship.move_based_on_strategy(enemy, enemy_flag_ship)

            if has_won:
                return

        # switch battle timer
        await self.switch_turn_with_enemy()


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

    def start_moving(self, x, y, dir):
        old_x = self.x
        old_y = self.y

        self.is_moving = True
        self.dir = dir
        self.x = x
        self.y = y
        self.move_timer = 0

        sMapMgr.move_object(self, old_x, old_y, x, y)


        if self.is_in_port():
            self.speed = c.PORT_SPEED
        elif self.is_at_sea():
            if self.is_role():
                self.speed = c.PORT_SPEED
            elif self.is_npc():
                self.speed = c.NPC_SPEED

        pack = pb.StartedMoving(
            id=self.id,
            src_x=self.x,
            src_y=self.y,
            dir=self.dir,
            speed=self.speed,
        )
        if self.is_role():
            self.session.packet_handler.send_to_nearby_roles(pack, include_self=True)
        else:
            nearby_objects = sMapMgr.get_nearby_objects(self)
            for object in nearby_objects:
                if object.is_role():
                    object.session.send(pack)
    def is_dir_diagnal(self):
        if self.dir in [pb.DirType.NW, pb.DirType.NE, pb.DirType.SW, pb.DirType.SE]:
            return True
        else:
            return False

    def calc_move_timer(self):
        if self.is_dir_diagnal():
            move_timer = 1.41 * c.PIXELS_COVERED_EACH_MOVE / self.speed
        else:
            move_timer = c.PIXELS_COVERED_EACH_MOVE / self.speed
        return move_timer

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


class Model:

    def __init__(self):
        self.role = None
        self.id_2_role = {}
