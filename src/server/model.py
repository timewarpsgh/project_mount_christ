from dataclasses import dataclass
import asyncio
import random
import login_pb2 as pb
import math
import numpy
from enum import Enum, auto
import json
import copy

# import from dir
import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\server\models')

import constants as c
from object_mgr import sObjectMgr
from map_maker import sMapMaker
from map_mgr import sMapMgr
from helpers import Point, are_vectors_in_same_direction
from id_mgr import sIdMgr
from season_mgr import sSeasonMgr

from role_models import \
    SESSION as ROLE_SESSION, \
    Role as RoleModel, \
    Ship as ShipModel, \
    Mate as MateModel, \
    Friend as FriendModel



@dataclass
class Friend:

    role_id: int=None
    name: str=None
    is_enemy: bool=False
    is_online: bool=False


class FriendMgr:

    def __init__(self, role, role_id):
        self.role = role
        self.role_id = role_id
        self.id_2_friend = {}

    def load_from_db(self, server):
        friends_models = ROLE_SESSION.query(FriendModel).\
            filter_by(role_id=self.role_id).\
            all()

        for friend_model in friends_models:
            friend = Friend(
                role_id=friend_model.friend,
                name=friend_model.friend_name,
                is_enemy=friend_model.is_enemy,
                is_online=server.is_role_online(friend_model.friend),
            )
            self.id_2_friend[friend.role_id] = friend

        self.tell_watchers_my_online_state(server, is_online=True)

    def tell_watchers_my_online_state(self, server, is_online):
        # tell watchers that I am online
        friends_models = ROLE_SESSION.query(FriendModel). \
            filter_by(friend=self.role_id). \
            all()
        for friend_model in friends_models:
            watcher_id = friend_model.role_id
            if server.is_role_online(watcher_id):
                watcher = server.get_role(watcher_id)
                pack = pb.FriendOnlineStateChanged(
                    role_id=self.role_id,
                    is_online=is_online,
                )
                watcher.session.send(pack)

    def gen_proto_friends(self):
        proto_friends = []

        for friend in self.id_2_friend.values():
            proto_friend = pb.Friend(
                role_id=friend.role_id,
                name=friend.name,
                is_enemy=friend.is_enemy,
                is_online=friend.is_online,
            )
            proto_friends.append(proto_friend)

        return proto_friends

    def add_friend(self, pack):
        role_id = pack.role_id
        name = pack.name
        is_enemy = pack.is_enemy

        if len(self.id_2_friend) >= c.MAX_FRIENDS:
            return

        if role_id in self.id_2_friend:
            return

        # add to db
        friend_model = FriendModel(
            role_id=self.role_id,
            friend=role_id,
            friend_name=name,
            is_enemy=is_enemy,
        )
        ROLE_SESSION.add(friend_model)
        ROLE_SESSION.commit()

        # modify ram
        friend = Friend(
            role_id=role_id,
            name=name,
            is_enemy=is_enemy,
            is_online=True,
        )
        self.id_2_friend[role_id] = friend

        # tell client
        pack = pb.FriendAdded(
            role_id=role_id,
            name=name,
            is_enemy=is_enemy,
            is_online=True,
        )
        self.role.session.send(pack)

    def remove_friend(self, pack):
        role_id = pack.role_id

        # remove from db
        friend_model = ROLE_SESSION.query(FriendModel).\
            filter_by(role_id=self.role_id, friend=role_id).\
            first()
        ROLE_SESSION.delete(friend_model)
        ROLE_SESSION.commit()

        # modify ram
        self.id_2_friend.pop(role_id)

        # tell client
        pack = pb.FriendRemoved(
            role_id=role_id,
        )
        self.role.session.send(pack)

    def get_friends(self, is_enemy):
        pass


@dataclass
class Ship:

    id: int=None
    role_id: int=None
    role: any=None
    ship_mgr: any=None

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
    strategy: pb.AttackMethodType=None
    steps_left: int=0


    def get_supply_cnt(self):
        supply_cnt = self.food + self.water + self.material + self.cannon
        return supply_cnt

    def can_load(self, cnt):
        if self.cargo_cnt + self.get_supply_cnt() + cnt <= self.get_max_cargo():
            return True
        else:
            return False

    def remove_supply(self, supply_name, cnt):
        if supply_name == 'food':
            self.food -= cnt
        elif supply_name == 'water':
            self.water -= cnt
        elif supply_name == 'material':
            self.material -= cnt
        elif supply_name == 'cannon':
            self.cannon -= cnt

    def add_supply(self, supply_name, cnt):
        if supply_name == 'food':
            self.food += cnt
        elif supply_name == 'water':
            self.water += cnt
        elif supply_name == 'material':
            self.material += cnt
        elif supply_name == 'cannon':
            self.cannon += cnt

    def reduce_crew(self, cnt):
        self.now_crew -= cnt
        if self.now_crew < 0:
            self.now_crew = 0

    def add_crew(self, cnt):
        self.now_crew += cnt
        if self.now_crew > self.max_crew:
            self.now_crew = self.max_crew

    def change_weapon(self, cannon_id):
        self.type_of_guns = cannon_id
        self.now_guns = self.max_guns

    def clear_mates_onboard(self):
        self.captain = None
        self.accountant = None
        self.chief_navigator = None
        self.first_mate = None

    def get_mate(self, mate_id):
        mate = self.ship_mgr.role.mate_mgr.get_mate(mate_id)
        return mate

    def get_captain(self):
        if not self.captain:
            if self.ship_mgr.role.is_role():
                return None
            elif self.ship_mgr.role.is_npc():
                return None
                # mates = self.ship_mgr.role.mate_mgr.get_mates()
                # for mate in mates:
                #     return mate
        mate = self.get_mate(self.captain)
        return mate

    def get_chief_navigator(self):
        if not self.chief_navigator:
            return None
        mate = self.get_mate(self.chief_navigator)
        return mate

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

    def __calc_steps(self):
        base_speed = self.__get_base_speed()
        steps = int(base_speed // 20) + 1

        min_steps = 1
        max_steps = 8

        if steps < min_steps:
            steps = min_steps
        if steps > max_steps:
            steps = max_steps

        print(f'steps: {steps}')
        return steps

    def reset_steps_left(self):
        self.steps_left = self.__calc_steps()  # c.STEPS_LEFT

    def add_cargo(self, cargo_id, cargo_cnt):
        self.cargo_id = cargo_id
        self.cargo_cnt = cargo_cnt

    def remove_cargo(self, cargo_id, cargo_cnt):
        if self.cargo_id == cargo_id:
            self.cargo_cnt -= cargo_cnt
            if self.cargo_cnt <= 0:
                self.cargo_cnt = 0
                self.cargo_id = 0

    def __get_battle_skill(self):
        captain = self.get_captain()
        if not captain:
            battle_skill = 0
            return battle_skill

        battle_skill = captain.battle

        first_mate = self.get_first_mate()
        if first_mate:
            battle_skill = max(battle_skill, first_mate.battle)

        return battle_skill

    def __calc_shoot_dmg(self, ship):
        # get battle_skill
        battle_skill = self.__get_battle_skill()

        # get gun_dmg from gun_type
        cannon = sObjectMgr.get_cannon(self.type_of_guns)
        gun_dmg = cannon.damage

        # gear ratio
        if self.ship_mgr.role.weapon:
            weapon_ratio = 1 + sObjectMgr.get_item(self.ship_mgr.role.weapon).effect / 100
        else:
            weapon_ratio = 1

        if ship.ship_mgr.role.armor:
            armor_ratio = 1 + sObjectMgr.get_item(ship.ship_mgr.role.armor).effect / 100
        else:
            armor_ratio = 1

        # calc dmg
        dmg = int(self.now_guns * gun_dmg * battle_skill * 0.01 * 0.1 * weapon_ratio / armor_ratio)

        # morale effect
        morale = self.ship_mgr.role.morale
        dmg = int(dmg * morale * 0.01)

        # now_crew effect
        if self.now_crew >= self.now_guns:
            pass
        else:
            dmg = int(dmg * self.now_crew / self.now_guns)

        # rand effect
        dmg = self.__rand_dmg(dmg)

        max_dmg = 20
        min_dmg = 1
        if dmg < min_dmg:
            dmg = min_dmg
        if dmg > max_dmg:
            dmg = max_dmg

        return dmg

    def shoot(self, ship):
        damage = 0
        is_sunk = False

        if self.cannon <= 0:
            return damage, is_sunk
        if not self.type_of_guns:
            return damage, is_sunk
        if not self.now_guns:
            return damage, is_sunk

        self.cannon -= 1

        damage = self.__calc_shoot_dmg(ship)#  c.SHOOT_DAMAGE
        # damage = c.SHOOT_DAMAGE
        ship.now_durability -= damage

        is_sunk = False
        if ship.now_durability <= 0:
            ship.now_durability = 0
            is_sunk = True

        # send packs
        pack = pb.ShipAttacked(
            src_id=self.id,
            dst_id=ship.id,
            attack_method_type=pb.AttackMethodType.SHOOT,
            dst_damage=damage,
        )
        self.role.send_to_self_and_enemy(pack)

        # pack = pb.GotChat(
        #     text=f"{self.name} at {self.x} {self.y} "
        #          f"shot {ship.name} at {ship.x} {ship.y} "
        #          f"and dealt {damage} damage",
        #     chat_type=pb.ChatType.SYSTEM
        # )
        # self.role.send_to_self_and_enemy(pack)

        return damage, is_sunk

    def __calc_engage_dmg(self, ship):
        # get battle_skill
        battle_skill = self.__get_battle_skill()

        # get crew_ratio
        if self.ship_mgr.role.weapon:
            weapon_ratio = 1 + sObjectMgr.get_item(self.ship_mgr.role.weapon).effect / 100
        else:
            weapon_ratio = 1

        if ship.ship_mgr.role.armor:
            armor_ratio = 1 + sObjectMgr.get_item(ship.ship_mgr.role.armor).effect / 100
        else:
            armor_ratio = 1

        crew_ratio = (self.now_crew * weapon_ratio) / (ship.now_crew * armor_ratio)

        # calc dmg
        dmg = int(self.now_crew * crew_ratio * battle_skill * 0.01 // 4)

        # morale effect
        morale = self.ship_mgr.role.morale
        dmg = int(dmg * morale * 0.01)

        # rand effect
        dmg = self.__rand_dmg(dmg)

        max_dmg = 50
        min_dmg = 0
        if dmg < min_dmg:
            dmg = min_dmg
        if dmg > max_dmg:
            dmg = max_dmg

        return dmg

    def __rand_dmg(self, dmg):
        dmg = int(dmg * (random.randint(80, 120) / 100))
        return dmg

    def engage(self, ship):
        self_dmg = ship.__calc_engage_dmg(self)#c.ENGAGE_SELF_DAMAGE
        # self_dmg = c.ENGAGE_SELF_DAMAGE
        target_dmg = self.__calc_engage_dmg(ship)#c.ENGAGE_TARGET_DAMAGE
        # target_dmg = c.ENGAGE_TARGET_DAMAGE
        self.now_crew -= self_dmg
        ship.now_crew -= target_dmg

        is_target_dead = False
        if ship.now_crew <= 0:
            ship.now_crew = 0
            is_target_dead = True

        is_self_dead = False
        if self.now_crew <= 0:
            self.now_crew = 0
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

        # pack = pb.GotChat(
        #     text=f"{self.name} at {self.x} {self.y} engaged {ship.name} at {ship.x} {ship.y} "
        #          f"and dealt {self_dmg} to self and {target_dmg} to enemy ",
        #     chat_type=pb.ChatType.SYSTEM
        # )
        # self.role.send_to_self_and_enemy(pack)

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

    async def try_to_shoot(self, enemy, flag_ship)->bool:
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

                if enemy.is_npc():
                    enemy.ship_mgr.rm_ship(target_ship.id)

                self.role.win(enemy)
                has_won = True
                return has_won

            if target_ship.id not in enemy.ship_mgr.id_2_ship:
                return has_won

            enemy.ship_mgr.rm_ship(target_ship.id)

        return has_won

    async def try_to_engage(self, enemy, flag_ship):
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
                    self.role.win(enemy)
                    has_won = True
                    return has_won
            elif is_self_dead:
                enemy.win(self.role)
                has_won = True
                return has_won

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
            dir=self.dir,
        )

        return ship_proto

    def load_from_db(self, ship):
        self.id = ship.id
        self.role_id = ship.role_id
        self.name = ship.name
        self.ship_template_id = ship.ship_template_id
        self.material_type = ship.material_type
        self.now_durability = ship.now_durability
        self.max_durability = ship.max_durability
        self.tacking = ship.tacking
        self.power = ship.power
        self.capacity = ship.capacity
        self.now_crew = ship.now_crew
        self.min_crew = ship.min_crew
        self.max_crew = ship.max_crew
        self.now_guns = ship.now_guns
        self.type_of_guns = ship.type_of_guns
        self.max_guns = ship.max_guns
        self.water = ship.water
        self.food = ship.food
        self.material = ship.material
        self.cannon = ship.cannon
        self.cargo_cnt = ship.cargo_cnt
        self.cargo_id = ship.cargo_id
        self.captain = ship.captain
        self.accountant = ship.accountant
        self.first_mate = ship.first_mate
        self.chief_navigator = ship.chief_navigator


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

        if self.cannon <= 0:
            self.strategy = pb.AttackMethodType.ENGAGE

        if self.now_crew <= self.min_crew:
            self.strategy = pb.AttackMethodType.FLEE

        if self.now_durability <= 10:
            self.strategy = pb.AttackMethodType.FLEE

    def set_target_ship(self, ship):
        self.target_ship = ship

    def set_strategy(self, strategy):
        self.strategy = strategy

    def __get_wind_effect(self, dir):
        ship_dir = dir
        wind_dir = sSeasonMgr.wind_dir
        wind_speed = sSeasonMgr.wind_speed


        # Convert directions to angles
        ship_angle = ship_dir * 45
        wind_angle = wind_dir * 45

        # Calculate the angle difference
        angle_diff = abs(ship_angle - wind_angle)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff

        # Determine wind effect based on angle difference
        if angle_diff == 0:
            # Tailwind
            wind_effect = wind_speed * 0.5
        elif angle_diff == 180:
            # Headwind
            wind_effect = wind_speed * -0.25
        elif angle_diff == 90:
            # Crosswind
            wind_effect = wind_speed * 1.0
        elif angle_diff == 45:
            # Crosswind closer to tailwind
            wind_effect = wind_speed * 0.75
        elif angle_diff == 135:
            # Crosswind closer to headwind
            wind_effect = wind_speed * 0.25

        wind_effect = wind_effect * 4
        return wind_effect

    def __get_current_effect(self, dir):
        ship_dir = dir
        current_dir = sSeasonMgr.current_dir
        current_speed = sSeasonMgr.current_speed

        # Convert directions to angles
        ship_angle = ship_dir * 45
        current_angle = current_dir * 45

        # Calculate the angle difference
        angle_diff = abs(ship_angle - current_angle)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff

        # Determine wind effect based on angle difference
        if angle_diff == 0:
            # Tail
            current_effect = current_speed * 1.0
        elif angle_diff == 180:
            # Head
            current_effect = current_speed * -1.0
        elif angle_diff == 90:
            # Cross
            current_effect = current_speed * 0
        elif angle_diff == 45:
            # Cross closer to tail
            current_effect = current_speed * 0.5
        elif angle_diff == 135:
            # Cross closer to head
            current_effect = current_speed * -0.5

        current_effect = current_effect * 4
        return current_effect

    def __get_base_speed(self):
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
        if chief_navigator:
            navigation = max(captain.navigation, chief_navigator.navigation)

        # calc base_speed(about 100 max)
        base_speed = (tacking + power + navigation) * 0.25

        return base_speed

    def get_speed(self, dir):

        base_speed = self.__get_base_speed()
        wind_effect = self.__get_wind_effect(dir)
        curren_effect = self.__get_current_effect(dir)

        speed = int(base_speed + wind_effect + curren_effect)

        if self.now_crew >= self.min_crew:
            speed = speed
        else:
            speed = int(speed * self.now_crew / self.min_crew)

        if self.now_durability <= 0:
            speed = 0

        if speed <= 0:
            speed = 1
        if speed > 80:
            speed = 80

        return speed

    def get_repair_cost(self):
        ship_template = sObjectMgr.get_ship_template(self.ship_template_id)
        cost = ship_template.buy_price * \
               (self.max_durability - self.now_durability) / \
               self.max_durability
        cost = int(cost)
        return cost

    def repair(self):
        """max dura reduces based on damage"""

        loss = (self.max_durability - self.now_durability) * 0.1
        loss = int(loss)
        self.max_durability -= loss
        self.now_durability = self.max_durability

    def get_max_cargo(self):
        max_cargo = self.capacity - self.max_crew - self.max_guns
        return max_cargo

    def change_capacity(self, max_crew, max_guns):
        template_id = self.ship_template_id
        ship_template = sObjectMgr.get_ship_template(template_id)

        if max_crew <= ship_template.max_crew and max_crew >= ship_template.min_crew:
            self.max_crew = max_crew
            if self.now_crew > self.max_crew:
                self.now_crew = self.max_crew

        if max_guns <= ship_template.max_guns and max_guns >= 0:
            self.max_guns = max_guns
            if self.now_guns > self.max_guns:
                self.now_guns = self.max_guns

        self.useful_capacity = self.capacity - self.max_guns - self.max_crew

        self.ship_mgr.role.session.send(
            pb.ShipCapacityChanged(
                id = self.id,
                max_crew = self.max_crew,
                max_guns = self.max_guns,
                useful_capacity = self.useful_capacity,
                now_crew = self.now_crew,
                now_guns = self.now_guns,
            )
        )

@dataclass
class Mate:

    id: int=None
    role_id: int=None
    mate_mgr: any=None

    name: str=None
    img_id: int=None
    mate_template_id: int=None
    nation: int=None
    fleet: int=None

    lv: int=None
    points: int=None
    duty_type: int=None
    ship_id: int=None

    leadership: int=None

    navigation: int=None
    accounting: int=None
    battle: int=None

    talent_in_navigation: int=None
    talent_in_accounting: int=None
    talent_in_battle: int=None

    lv_in_nav: int=None
    lv_in_acc: int=None
    lv_in_bat: int=None

    xp_in_nav: int=None
    xp_in_acc: int=None
    xp_in_bat: int=None

    def clear_duty(self):
        self.duty_type = None
        self.ship_id = None

    def earn_xp(self, amount, duty_type):
        pack = pb.XpEarned(
            mate_id=self.id,
            duty_type=duty_type,
            amount=amount
        )
        self.mate_mgr.role.session.send(pack)

        if duty_type == pb.DutyType.CHIEF_NAVIGATOR:
            self.xp_in_nav += amount

            if self.xp_in_nav >= c.LV_2_MAX_XP[self.lv_in_nav]:
                self.lv_up(duty_type)

        elif duty_type == pb.DutyType.ACCOUNTANT:
            self.xp_in_acc += amount
            if self.xp_in_acc >= c.LV_2_MAX_XP[self.lv_in_acc]:
                self.lv_up(duty_type)

        elif duty_type == pb.DutyType.FIRST_MATE:
            self.xp_in_bat += amount
            if self.xp_in_bat >= c.LV_2_MAX_XP[self.lv_in_bat]:
                self.lv_up(duty_type)

    def lv_up(self, duty_type):
        talent_chance = 0.5

        if duty_type == pb.DutyType.CHIEF_NAVIGATOR:
            self.lv_in_nav += 1
            self.xp_in_nav = 0

            # hard increase
            self.navigation += 1

            # increase navigation by change
            if random.random() < talent_chance:
                self.navigation += self.talent_in_navigation

            # send pack
            pack = pb.LvUped(
                mate_id=self.id,
                duty_type=duty_type,
                lv=self.lv_in_nav,
                xp=self.xp_in_nav,
                value=self.navigation,
            )
            self.mate_mgr.role.session.send(pack)

        elif duty_type == pb.DutyType.ACCOUNTANT:
            self.lv_in_acc += 1
            self.xp_in_acc = 0

            # hard increase
            self.accounting += 1

            # increase accounting by change
            if random.random() < talent_chance:
                self.accounting += self.talent_in_accounting

            # send pack
            pack = pb.LvUped(
                mate_id=self.id,
                duty_type=duty_type,
                lv=self.lv_in_acc,
                xp=self.xp_in_acc,
                value=self.accounting,
            )
            self.mate_mgr.role.session.send(pack)

        elif duty_type == pb.DutyType.FIRST_MATE:
            self.lv_in_bat += 1
            self.xp_in_bat = 0

            # hard increase
            self.battle += 1

            # increase battle by change
            if random.random() < talent_chance:
                self.battle += self.talent_in_battle

            # send pack
            pack = pb.LvUped(
                mate_id=self.id,
                duty_type=duty_type,
                lv=self.lv_in_bat,
                xp=self.xp_in_bat,
                value=self.battle,
            )
            self.mate_mgr.role.session.send(pack)

    def load_from_db(self, mate):
        self.id = mate.id
        self.role_id = mate.role_id
        self.name = mate.name
        self.img_id = mate.img_id
        self.nation = mate.nation
        self.lv = mate.lv
        self.points = mate.points
        self.duty_type = mate.duty_type
        self.ship_id = mate.ship_id

        self.leadership = mate.leadership

        self.navigation = mate.navigation
        self.accounting = mate.accounting
        self.battle = mate.battle

        self.talent_in_navigation = mate.talent_in_navigation
        self.talent_in_accounting = mate.talent_in_accounting
        self.talent_in_battle = mate.talent_in_battle

        self.lv_in_nav = mate.lv_in_nav
        self.lv_in_acc = mate.lv_in_acc
        self.lv_in_bat = mate.lv_in_bat

        self.xp_in_nav = mate.xp_in_nav
        self.xp_in_acc = mate.xp_in_acc
        self.xp_in_bat = mate.xp_in_bat

    def gen_mate_pb(self):

        mate_pb = pb.Mate(
            id=self.id,
            role_id=self.role_id,
            name=self.name,
            img_id=self.img_id,
            nation=self.nation,
            lv=self.lv,
            points=self.points,

            duty_type=self.duty_type,
            ship_id=self.ship_id,

            leadership=self.leadership,

            navigation=self.navigation,
            accounting=self.accounting,
            battle=self.battle,

            talent_in_navigation=self.talent_in_navigation,
            talent_in_accounting=self.talent_in_accounting,
            talent_in_battle=self.talent_in_battle,

            lv_in_nav=self.lv_in_nav,
            lv_in_acc=self.lv_in_acc,
            lv_in_bat=self.lv_in_bat,

            xp_in_nav=self.xp_in_nav,
            xp_in_acc=self.xp_in_acc,
            xp_in_bat=self.xp_in_bat,
        )

        return mate_pb

    def init_from_template(self, mate_template, role_id):
        self.id = sIdMgr.gen_new_mate_id()
        self.role_id = role_id

        self.name = mate_template.name
        self.img_id = mate_template.img_id
        self.nation = mate_template.nation

        self.navigation = mate_template.navigation
        self.accounting = mate_template.accounting
        self.battle = mate_template.battle

        self.talent_in_navigation = mate_template.talent_in_navigation
        self.talent_in_accounting = mate_template.talent_in_accounting
        self.talent_in_battle = mate_template.talent_in_battle

        self.lv_in_nav = mate_template.lv_in_nav
        self.lv_in_acc = mate_template.lv_in_acc
        self.lv_in_bat = mate_template.lv_in_bat

        self.xp_in_nav = 0
        self.xp_in_acc = 0
        self.xp_in_bat = 0


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
        del self.id_2_ship[ship_id]

        pack = pb.ShipRemoved(
            id=ship_id
        )
        self.role.send_to_self_and_enemy(pack)


    def get_ship(self, ship_id):
        return self.id_2_ship[ship_id]

    def get_ships(self):
        return list(self.id_2_ship.values())

    def get_total_crew(self):
        ships = self.get_ships()
        return sum([ship.now_crew for ship in ships])

    def get_new_ship_name(self):
        new_ship_name = str(len(self.id_2_ship))
        return new_ship_name

    def init_ships_positions_in_battle(self, is_attacker=True):
        # initial x need to satisfy hex movement
        x_positions = set(range(5, 15))
        y_positions = set(range(5, 15))

        if not is_attacker:
            attacker = self.role.get_enemy()
            x_diff = self.role.x - attacker.x
            y_diff = self.role.y - attacker.y

        for id, ship in enumerate(self.id_2_ship.values()):

            ship.role = self.role

            # attacker
            if is_attacker:
                x_pos = random.choice(list(x_positions))
                x_positions.remove(x_pos)
                ship.x = x_pos

                y_pos = random.choice(list(y_positions))
                ship.y = y_pos
                if x_pos % 2 == 0:
                    ship.y += 0.5

                self.__set_ship_dir_from_role_dir(ship)

            # defender
            else:
                x_pos = random.choice(list(x_positions))
                x_positions.remove(x_pos)
                ship.x = x_pos + 10 * x_diff

                y_pos = random.choice(list(y_positions))
                ship.y = y_pos + 10 * y_diff

                if x_pos % 2 == 0:
                    ship.y += 0.5

                self.__set_ship_dir_from_role_dir(ship)

            ship.reset_steps_left()

    def __set_ship_dir_from_role_dir(self, ship):
        if self.role.dir == pb.DirType.E:
            ship.dir = pb.DirType.NE
        elif self.role.dir == pb.DirType.W:
            ship.dir = pb.DirType.NW
        else:
            ship.dir = self.role.dir

    def gen_ships_prots(self):
        ships_prots = []
        for ship in self.id_2_ship.values():
             ship_proto = ship.gen_ship_proto()
             ships_prots.append(ship_proto)

        return ships_prots

    def has_ship(self, id):
        return id in self.id_2_ship

    def clear_crew(self):
        for ship in self.get_ships():
            ship.now_crew = 0

            self.role.session.send(
                pb.ShipFieldChanged(
                    ship_id=ship.id,
                    key='now_crew',
                    int_value=0,
                )
            )

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
    bank_money: int=None
    items: list[int]=None
    auras: set[int]=None
    seen_grids: any=None  # numpy matrix
    days_at_sea: int=0
    pay_days: int=0
    starved_days: int=0
    is_dead: bool=False
    at_sea_timer: int=c.SUPPLY_CONSUMPTION_INVERVAL

    ship_mgr: ShipMgr=None
    mate_mgr: MateMgr=None
    discovery_mgr: DiscoveryMgr=None
    friend_mgr: FriendMgr=None

    battle_npc_id: int=None
    battle_role_id: int=None
    battle_timer: int=None
    npc_instance: any=None
    battle_role: any=None

    ration: int=100
    morale: int=100
    health: int=100

    weapon: int=None
    armor: int=None
    notorities: list[int]=None

    has_treated_crew: bool=False
    recruited_crew_cnt: int=0
    has_treated: bool=False
    treasure_map_id: int=None
    event_id: int=None
    nation: int=None

    trade_role_id: int=None
    trade_money: int=0
    trade_item_id: int=None
    is_trade_confirmed: bool=False

    def save_to_db(self):
        self.__save_role()

        self.__save_ships()
        self.__save_mates()
        self.__save_friends()

    def __save_ships(self):
        # clear ships in db
        ROLE_SESSION.query(ShipModel).filter_by(role_id=self.id).delete()
        ROLE_SESSION.commit()

        # add ships in ram to db
        for ship in self.ship_mgr.get_ships():
            ship_model = ShipModel(
                id=ship.id,
                role_id=self.id,
                name=ship.name,
                ship_template_id=ship.ship_template_id,
                material_type=ship.material_type,

                captain=ship.captain,
                accountant=ship.accountant,
                first_mate=ship.first_mate,
                chief_navigator=ship.chief_navigator,

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
            )

            ROLE_SESSION.add(ship_model)

        ROLE_SESSION.commit()

    def __save_mates(self):
        # clear mates in db
        ROLE_SESSION.query(MateModel).filter_by(role_id=self.id).delete()
        ROLE_SESSION.commit()

        # add mates in ram to db
        for mate in self.mate_mgr.get_mates():
            mate_model = MateModel(
                id=mate.id,
                role_id=self.id,
                mate_template_id=mate.mate_template_id,
                name=mate.name,
                img_id=mate.img_id,

                nation=mate.nation,
                fleet=mate.fleet,
                lv=mate.lv,
                points=mate.points,
                duty_type=mate.duty_type,
                ship_id=mate.ship_id,
                leadership=mate.leadership,
                navigation=mate.navigation,
                accounting=mate.accounting,
                battle=mate.battle,
                talent_in_navigation=mate.talent_in_navigation,
                talent_in_accounting=mate.talent_in_accounting,
                talent_in_battle=mate.talent_in_battle,
                lv_in_nav=mate.lv_in_nav,
                lv_in_acc=mate.lv_in_acc,
                lv_in_bat=mate.lv_in_bat,
                xp_in_nav=mate.xp_in_nav,
                xp_in_acc=mate.xp_in_acc,
                xp_in_bat=mate.xp_in_bat,
            )

            ROLE_SESSION.add(mate_model)

        ROLE_SESSION.commit()

    def __save_friends(self):
        """
        no need, as friends in db are modified in real time
        """
        pass

    def __save_role(self):
        # save role
        role_model = ROLE_SESSION.query(RoleModel).filter_by(id=self.id).first()

        role_model.map_id = self.map_id
        role_model.x = self.x
        role_model.y = self.y
        role_model.dir = self.dir
        role_model.money = self.money
        role_model.bank_money = self.bank_money
        role_model.discovery_ids_json_str = json.dumps(list(self.discovery_mgr.get_ids_set()))
        role_model.seen_grids = json.dumps(self.seen_grids.tolist())
        role_model.pay_days = self.pay_days
        role_model.days_at_sea = self.days_at_sea
        role_model.items = json.dumps(self.items)
        role_model.notorities = json.dumps(self.notorities)
        role_model.has_treated_crew = self.has_treated_crew
        role_model.recruited_crew_cnt = self.recruited_crew_cnt
        role_model.treasue_map_id = self.treasure_map_id
        role_model.event_id = self.event_id
        role_model.nation = self.nation
        role_model.weapon = self.weapon
        role_model.armor = self.armor

        ROLE_SESSION.commit()

    def __unconfirm_trade(self):
        # unconfirm
        self.is_trade_confirmed = False
        self.__get_trade_role().is_trade_confirmed = False

        pack = pb.TradeUnconfirmed()
        self.session.send(pack)
        self.__get_trade_role().session.send(pack)

    def set_trade_money(self, amount):
        if not self.has_enough_money(amount):
            return

        self.trade_money = amount

        pack = pb.TradeMoneySet(
            amount=amount,
            role_id=self.id,
        )

        self.session.send(pack)
        self.__get_trade_role().session.send(pack)

        self.__unconfirm_trade()

    def set_trade_item(self, item_id):
        if not self.has_item(item_id):
            return

        self.trade_item_id = item_id

        pack = pb.TradeItemSet(
            item_id=item_id,
            role_id=self.id,
        )

        self.session.send(pack)
        self.__get_trade_role().session.send(pack)

        self.__unconfirm_trade()

    def confirm_trade(self):
        trade_role = self.session.server.get_role(self.trade_role_id)

        self.is_trade_confirmed = True

        pack = pb.TradeConfirmed(
            role_id=self.id,
        )
        self.session.send(pack)
        trade_role.session.send(pack)

        if trade_role.is_trade_confirmed:
            self.__complete_trade()

    def __get_trade_role(self):
        return self.session.server.get_role(self.trade_role_id)

    def __is_item_equiped(self, item_id):
        if self.weapon == item_id or self.armor == item_id:
            return True
        else:
            return False

    def __complete_trade(self):
        trade_role = self.__get_trade_role()

        # trade money
        if self.trade_money != 0:
            self.mod_money(-self.trade_money)
            trade_role.mod_money(self.trade_money)

        if trade_role.trade_money != 0:
            trade_role.mod_money(-trade_role.trade_money)
            self.mod_money(trade_role.trade_money)

        # trade item
        if self.trade_item_id:
            self.remove_item(self.trade_item_id)

            if self.__is_item_equiped(self.trade_item_id):
                if not self.has_item(self.trade_item_id):
                    self.unequip_item(self.trade_item_id)

            trade_role.add_item(self.trade_item_id)

        if trade_role.trade_item_id:
            trade_role.remove_item(trade_role.trade_item_id)

            if trade_role.__is_item_equiped(trade_role.trade_item_id):
                if not trade_role.has_item(trade_role.trade_item_id):
                    trade_role.unequip_item(trade_role.trade_item_id)

            self.add_item(trade_role.trade_item_id)

        pack = pb.TradeCompleted()
        self.session.send(pack)
        trade_role.session.send(pack)

    def accept_trade_request(self, role_id):
        role = self.session.server.get_role(role_id)

        pack = pb.TradeStart(
            role_id=role.id,
            role_name=role.name,
        )
        self.session.send(pack)
        self.trade_role_id = role_id
        self.trade_money = 0
        self.trade_item_id = None
        self.is_trade_confirmed = False

        pack = pb.TradeStart(
            role_id=self.id,
            role_name=self.name,
        )
        role.session.send(pack)
        role.trade_role_id = self.id
        role.trade_money = 0
        role.trade_item_id = None
        role.is_trade_confirmed = False

    def request_trade(self, role_id):
        role = self.session.server.get_role(role_id)
        pack = pb.TradeRequested(
            role_id=self.id,
            role_name=self.name,
        )
        role.session.send(pack)

    def trigger_event(self):
        event = sObjectMgr.get_event(self.event_id)

        if event.reward_type:
            if event.reward_type == 'Mate':
                mate_template_id = event.reward_id
                mate_template = sObjectMgr.get_mate_template(mate_template_id)

                mate = Mate()
                mate.init_from_template(mate_template, self.id)
                self.mate_mgr.add_mate(mate)
                pack = pb.MateAdded(
                    mate=mate.gen_mate_pb(),
                )
                self.session.send(pack)

        self.event_id += 1

    def buy_treasure_map(self):
        if self.has_enough_money(c.TREASURE_MAP_COST):
            self.mod_money(-c.TREASURE_MAP_COST)
            self.treasure_map_id = sObjectMgr.get_rand_village_id()
            pack = pb.TreasureMapBought(
                treasure_map_id=self.treasure_map_id
            )
            self.session.send(pack)

    def make_discovery(self, village_id):
        village = sObjectMgr.get_village(village_id)
        distance = 3

        if abs(village.x - self.x) <= distance and abs(village.y - self.y) <= distance:
            self.__make_discovery(village, village_id)
            self.__find_treasure(village_id)

    def __find_treasure(self, village_id):
        # find treasure
        if self.treasure_map_id:
            if self.treasure_map_id == village_id:
                item_name = self.__add_rand_item()

                # send chat
                pack = pb.RandMateSpeak(
                    text=f'Found {item_name}!',
                )
                self.session.send(pack)

                self.treasure_map_id = None
                # send treasure map cleared
                pack = pb.TreasureMapCleared()
                self.session.send(pack)

                self.__earn_xp_for_navigation()

    def __make_discovery(self, village, village_id):
        # make discovery
        if village_id not in self.discovery_mgr.get_ids_set():

            self.discovery_mgr.add(village_id)

            pack = pb.GotChat(
                origin_name=self.name,
                chat_type=pb.ChatType.SYSTEM,
                text=f'discovered {village.name}',
            )
            self.session.send(pack)

            self.session.send(pb.Discovered(village_id=village_id))

            self.__earn_xp_for_navigation()

    def __earn_xp_for_navigation(self):

        # cal xp_amount
        flag_ship = self.get_flag_ship()
        captain_of_flag_ship = flag_ship.get_captain()
        navigation_skill = captain_of_flag_ship.navigation
        chief_navigator = flag_ship.get_chief_navigator()

        if chief_navigator:
            navigation_skill = max(navigation_skill, chief_navigator.navigation)

        xp_amount = int(200 * navigation_skill * c.DISCOVER_XP_FACTOR)

        # chief_navigator earn xp
        if chief_navigator:
            chief_navigator.earn_xp(xp_amount, pb.DutyType.CHIEF_NAVIGATOR)

        # captains earn xp
        ships = self.ship_mgr.get_ships()
        for ship in ships:
            captain = ship.get_captain()
            if captain:
                captain.earn_xp(xp_amount, pb.DutyType.CHIEF_NAVIGATOR)

    def __reset_flagship(self, flag_ship):
        flag_ship.reset_steps_left()

        pack = pb.ShipMoved(
            id=flag_ship.id,
            x=flag_ship.x,
            y=flag_ship.y,
            dir=flag_ship.dir,
            steps_left=flag_ship.steps_left,
        )
        self.session.send(pack)

    async def flagship_attack(self, attack_method_type, target_ship_id):

        flag_ship = self.get_flag_ship()
        enemy = self.get_enemy()
        enemy_flag_ship = enemy.get_flag_ship()

        if target_ship_id:
            target_ship = enemy.ship_mgr.get_ship(target_ship_id)

        if attack_method_type == pb.AttackMethodType.SHOOT:
            if flag_ship.can_shoot(target_ship):
                flag_ship.target_ship = target_ship
                has_won = await flag_ship.try_to_shoot(enemy, enemy_flag_ship)
                if not has_won:
                    await self.all_ships_attack_role(include_flagship=False)

        elif attack_method_type == pb.AttackMethodType.ENGAGE:
            if flag_ship.can_engage(target_ship):
                flag_ship.target_ship = target_ship
                has_won = await flag_ship.try_to_engage(enemy, enemy_flag_ship)
                if not has_won:
                    await self.all_ships_attack_role(include_flagship=False)

        elif attack_method_type == pb.AttackMethodType.HOLD:
            await self.all_ships_attack_role(include_flagship=False)

        # reset flag_ship steps_left
        self.__reset_flagship(flag_ship)

    async def flagship_move(self, battle_dir_type):
        flag_ship = self.get_flag_ship()

        if battle_dir_type == pb.BattleDirType.LEFT:
            flag_ship.move_to_left()
        elif battle_dir_type == pb.BattleDirType.RIGHT:
            flag_ship.move_to_right()
        elif battle_dir_type == pb.BattleDirType.CUR:
            flag_ship.move_in_cur_dir()

        if flag_ship.steps_left <= 0:
            await self.all_ships_attack_role(include_flagship=False)
            self.__reset_flagship(flag_ship)

    def __can_escape_npc_battle(self):
        # distance check
        npc = self.npc_instance
        npc_flag_ship = npc.get_flag_ship()
        my_flag_ship = self.get_flag_ship()

        if abs(my_flag_ship.x - npc_flag_ship.x) >= c.ESCAPE_DISTANCE or \
                abs(my_flag_ship.y - npc_flag_ship.y) >= c.ESCAPE_DISTANCE:
            return True
        else:
            return False

    def __can_escape_role_battle(self):
        # distance check
        target_role = self.session.server.get_role(self.battle_role_id)
        target_flag_ship = target_role.get_flag_ship()
        my_flag_ship = self.get_flag_ship()

        if abs(my_flag_ship.x - target_flag_ship.x) >= c.ESCAPE_DISTANCE or \
                abs(my_flag_ship.y - target_flag_ship.y) >= c.ESCAPE_DISTANCE:
            return True
        else:
            return False

    def escape_role_battle(self):
        if not self.battle_timer:
            return

        if not self.__can_escape_role_battle():
            # send chat
            pack = pb.GotChat(
                chat_type=pb.ChatType.SYSTEM,
                text="Need to be far enough from enemy flagship to escape.",
            )
            self.session.send(pack)
            return

        target_role = self.session.server.get_role(self.battle_role_id)

        target_role.session.send(pb.EscapedRoleBattle())
        self.session.send(pb.EscapedRoleBattle())

        target_role.battle_role_id = None
        self.battle_role_id = None

        # notify nearby roles
        sMapMgr.add_object(self)
        sMapMgr.add_object(target_role)
        self.session.packet_handler.send_role_appeared_to_nearby_roles()
        target_role.session.packet_handler.send_role_appeared_to_nearby_roles()

    def escape_npc_battle(self):
        if not self.battle_timer:
            return

        if not self.__can_escape_npc_battle():
            # send chat
            pack = pb.GotChat(
                chat_type=pb.ChatType.SYSTEM,
                text="Need to be far enough from enemy flagship to escape.",
            )
            self.session.send(pack)
            return


        self.battle_npc_id = None

        self.session.send(pb.EscapedNpcBattle())

        # notify nearby roles
        sMapMgr.add_object(self)
        self.session.packet_handler.send_role_appeared_to_nearby_roles()

    def investigate_fleet(self, nation_id, fleet_id):
        npcs = self.__get_npc_mgr().get_npc_by_nation_and_fleet(nation_id, fleet_id)
        fleets_investigated = []
        for npc in npcs:
            fleet_investigated = pb.FleetInvestigated()
            fleet_investigated.captain_name = npc.mate.name
            fleet_investigated.now_x = npc.x
            fleet_investigated.now_y = npc.y
            fleet_investigated.dest_port_id = npc.end_port_id if npc.is_outward else npc.start_port_id
            fleet_investigated.cargo_id = npc.ship_mgr.get_ships()[0].cargo_id
            fleets_investigated.append(fleet_investigated)

        pack = pb.FleetsInvestigated()
        pack.fleets_investigated.extend(fleets_investigated)
        self.session.send(pack)

    def __can_hire_mate(self, mate_template):
        captain = self.get_flag_ship().get_captain()
        my_max_stat = max(captain.lv_in_nav, captain.lv_in_acc, captain.lv_in_bat)

        mate_template_max_stat = max(mate_template.lv_in_nav,
                                     mate_template.lv_in_acc,
                                     mate_template.lv_in_bat)

        if my_max_stat + 10 >= mate_template_max_stat:
            return True
        else:
            return False

    def hire_mate(self, mate_template_id):
        port_map = self.get_map()
        mate_template = port_map.mate_template

        if not mate_template:
            return

        if len(self.mate_mgr.get_mates()) >= c.MAX_MATES_CNT:
            return

        if not self.has_treated:
            pack = pb.MateSpeak(
                mate_template_id=mate_template.id,
                text=f"Sorry, I'm not interested in working with you.",
            )
            self.session.send(pack)
            return

        if mate_template.id != mate_template_id:
            return

        if self.mate_mgr.is_mate_in_fleet(mate_template):
            print('mate already in fleet')
            return

        if self.__can_hire_mate(mate_template):
            self.__add_mate(mate_template)
        else:
            pack = pb.MateSpeak(
                mate_template_id=mate_template.id,
                text=f"Go raise your level a bit. "
                     f"There's not much I can learn from you right now.",
            )
            self.session.send(pack)

    def __add_mate(self, mate_template):
        mate = Mate()
        mate.init_from_template(mate_template, self.id)
        self.mate_mgr.add_mate(mate)
        pack = pb.HireMateRes(
            is_ok=True,
            mate=mate.gen_mate_pb(),
        )
        self.session.send(pack)

    def sleep(self):
        self.has_treated_crew = False
        self.recruited_crew_cnt = 0
        self.__modify_pay_days()

        # send chat
        pack = pb.Slept()
        self.session.send(pack)

    def see_waitress(self):
        if not self.has_enough_money(c.WAITRESS_COST):
            return

        self.mod_money(-c.WAITRESS_COST)

        pack = pb.WaitressSeen()
        self.session.send(pack)

    def __get_npc_mgr(self):
        return self.session.server.npc_mgr

    def gossip(self, npc_id):
        npc = self.__get_npc_mgr().get_npc(npc_id)

        pack = pb.MateSpeak(
            mate_template_id=npc.mate.mate_template_id,
            text=f"I'm {npc.mate.name} from {c.Nation(npc.mate.nation).name}. "
                 f"I'm heading to {npc.get_target_port_name()}",
        )
        self.session.send(pack)

    def view_captain(self, role_id):
        # is npc
        if role_id > c.NPC_ROLE_START_ID:
            npc = self.__get_npc_mgr().get_npc(role_id)
            mate = npc.mate

            weapon = npc.weapon
            armor = npc.armor

        # is role
        else:
            role = self.session.server.get_role(role_id)
            flag_ship = role.get_flag_ship()
            if flag_ship:
                mate = flag_ship.get_captain()
            else:
                mate = role.mate_mgr.get_mates()[0]

            weapon = role.weapon
            armor = role.armor

        print(f"{role_id=}")
        print(f"{mate=}")

        pack = pb.CaptainInfo(
            name=mate.name,
            nation=mate.nation,
            navigation=mate.navigation,
            accounting=mate.accounting,
            battle=mate.battle,
            lv_in_nav=mate.lv_in_nav,
            lv_in_acc=mate.lv_in_acc,
            lv_in_bat=mate.lv_in_bat,
            img_id=mate.img_id,
            weapon=weapon if weapon else 0,
            armor=armor if armor else 0,
        )
        self.session.send(pack)

    def treat(self):
        if self.has_enough_money(c.TREAT_COST):
            self.mod_money(-c.TREAT_COST)
            self.has_treated = True

            mate_templte = self.get_map().mate_template
            mate_templte_id = mate_templte.id

            pack = pb.MateSpeak(
                mate_template_id=mate_templte_id,
                text='Ahh... Thank you!'
            )
            self.session.send(pack)

            pack = pb.Treated()
            self.session.send(pack)

    def treat_crew(self):
        total_crew = self.ship_mgr.get_total_crew()

        total_cost = total_crew * c.BEER_COST

        if self.money < total_cost:
            return

        if self.has_treated_crew:
            self.session.send(
                pb.BuildingSpeak(
                    text="You can't drink anymore today!",
                )
            )
            return

        self.mod_money(-total_cost)
        self.has_treated_crew = True
        port_map = self.get_map()
        self.recruited_crew_cnt = (port_map.economy_index + port_map.industry_index) // 10

        self.session.send(
            pb.CrewTreated(
                recruited_crew_cnt=self.recruited_crew_cnt
            )
        )

    def __is_cargo_available_in_my_port(self, cargo_id):

        port_map = self.get_map()
        port = self.get_port()

        if port.specialty_id == cargo_id:
            return True

        cargo_template = sObjectMgr.get_cargo_template(cargo_id)

        economy_diff = port_map.economy_index - port.economy
        # cargo_template.required_economy_value needs to be within [-200, 200]
        if economy_diff >= cargo_template.required_economy_value:
            return True
        else:
            return False

    def buy_ship(self, ship_template_id):

        if len(self.ship_mgr.get_ships()) >= c.MAX_SHIPS_CNT:
            return

        if not self.__is_ship_available_in_my_port(ship_template_id):
            return

        ship_template = sObjectMgr.get_ship_template(ship_template_id)
        price = ship_template.buy_price

        if not self.money >= price:
            return

        new_ship_name = self.ship_mgr.get_new_ship_name()

        new_model_ship = Ship(
            id=sIdMgr.gen_new_ship_id(),
            role_id=self.id,

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

        self.money -= price
        self.ship_mgr.add_ship(new_model_ship)

        # tell client
        self.session.send(pb.MoneyChanged(money=self.money))
        self.session.send(pb.GotNewShip(ship=new_model_ship.gen_ship_proto()))

    def __is_ship_available_in_my_port(self, ship_template_id):
        port_map = self.get_map()
        ship_template = sObjectMgr.get_ship_template(ship_template_id)

        if port_map.industry_index >= ship_template.required_industry_value:
            return True
        else:
            return False

    def __get_ships_to_buy(self, ship_ids):
        ships_to_buy = []

        for id in ship_ids:
            ship_template = sObjectMgr.get_ship_template(id)

            if self.__is_ship_available_in_my_port(id):
                ship_to_buy = pb.ShipToBuy(template_id=id, price=ship_template.buy_price)
                ships_to_buy.append(ship_to_buy)

        return ships_to_buy

    def get_ships_to_buy(self):
        port = self.get_port()

        ship_ids = sObjectMgr.get_ship_ids(port.economy_id)

        pack = pb.ShipsToBuy()
        ships_to_buy = self.__get_ships_to_buy(ship_ids)
        pack.ships_to_buy.extend(ships_to_buy)
        self.session.send(pack)

    def sell_ship(self, id):

        if id == self.get_flag_ship().id:
            # send chat
            pack = pb.GotChat(
                chat_type=pb.ChatType.SYSTEM,
                text='You cannot sell your flag ship!'
            )
            self.session.send(pack)

            self.session.send(pb.PopSomeMenus(cnt=4))
            return

        ship = self.ship_mgr.get_ship(id)
        ship_template = sObjectMgr.get_ship_template(ship.ship_template_id)
        sell_price = int(ship_template.buy_price / 2)

        self.money += sell_price
        self.ship_mgr.rm_ship(id)

        self.session.send(pb.MoneyChanged(money=self.money))
        self.session.send(pb.ShipRemoved(id=id))
        self.session.send(pb.PopSomeMenus(cnt=4))

    def has_item(self, item_id):
        return item_id in self.items

    def sell_item(self, item_id):
        if item_id not in self.items:
            return

        sell_price = sObjectMgr.get_item_sell_price(item_id)
        self.money += sell_price
        self.items.remove(item_id)

        self.session.send(
            pb.MoneyChanged(
                money=self.money
            )
        )

        self.session.send(
            pb.ItemRemoved(
                item_id=item_id
            )
        )

    def get_availalbe_items_ids_in_port(self):
        port = self.get_port()
        if not port.items_ids:
            return []

        ids = port.items_ids.split(' ')
        ids = [int(id) for id in ids if sObjectMgr.get_item(int(id))]
        return ids

    def get_nation(self):
        return self.nation

    def is_in_my_capital(self):
        if self.map_id in c.PORT_ID_2_NATION :
            if self.get_nation() == c.PORT_ID_2_NATION[self.map_id]:
                return True

        return False

    def __cure_aura(self, item_id):
        if not self.auras:
            return

        if item_id == c.Item.BALM.value:
            self.remove_aura(c.Aura.STORM.value)
        elif item_id == c.Item.LIME_JUICE.value:
            self.remove_aura(c.Aura.SCURVY.value)
        elif item_id == c.Item.RAT_POISON.value:
            self.remove_aura(c.Aura.RATS.value)

    def add_aura(self, aura_id):
        self.auras.add(aura_id)

        self.session.send(
            pb.AuraAdded(
                aura_id=aura_id
            )
        )

    def change_xy(self, x, y):
        self.session.packet_handler.send_role_disappeared_to_nearby_roles()

        old_x = self.x
        old_y = self.y
        old_map_id = self.map_id

        self.x = x
        self.y = y

        sMapMgr.change_object_map(self,
                                  old_map_id, old_x, old_y,
                                  self.map_id, self.x, self.y)

        self.session.packet_handler.send_role_appeared_to_nearby_roles()

        pack = pb.RoleMoved(
            id=self.id,
            x=self.x,
            y=self.y,
            dir_type=self.dir,
        )
        self.session.send(pack)

    def mod_money(self, amount):
        self.money += amount

        if self.money <= 0:
            self.money = 0

        self.session.send(
            pb.MoneyChanged(
                money=self.money
            )
        )

    def has_enough_money(self, amount):
        if self.money >= amount:
            return True
        return False

    def withdraw(self, amount):
        if self.bank_money < amount:
            return

        self.money += amount
        self.bank_money -= amount

        self.session.send(
            pb.MoneyChanged(
                money=self.money
            )
        )

        self.session.send(
            pb.Withdrawn(
                balance=self.bank_money
            )
        )

    def deposit(self, amount):
        if not self.has_enough_money(amount):
            return

        self.money -= amount
        self.bank_money += amount

        self.session.send(
            pb.MoneyChanged(
                money=self.money
            )
        )

        self.session.send(
            pb.Deposited(
                balance=self.bank_money
            )
        )

    def check_balance(self):
        balance = self.bank_money

        self.session.send(
            pb.YourBalance(
                balance=balance
            )
        )

    def donate(self, ingots_cnt):
        if ingots_cnt < 1:
            return

        if not self.has_enough_money(ingots_cnt * 10000):
            return

        self.add_aura(c.Aura.DONATION.value)
        self.mod_money(-ingots_cnt * 10000)

        self.session.send(pb.DonationMade())


    def pray(self):
        self.add_aura(c.Aura.PRAYER.value)

    def use_item(self, item_id):
        if not self.has_item(item_id):
            return

        # cure aura
        self.__cure_aura(item_id)

        self.items.remove(item_id)
        self.session.send(
            pb.ItemUsed(
                item_id=item_id
            )
        )

    def unequip_item(self, item_id):
        if not self.is_in_port():
            # send chat
            pack = pb.GotChat(
                chat_type=pb.ChatType.SYSTEM,
                text='You can only equip or unequip items in port.'
            )
            self.session.send(pack)

            return

        if item_id == self.weapon:
            self.weapon = None
        elif item_id == self.armor:
            self.armor = None

        self.session.send(
            pb.ItemUnequipped(
                item_id=item_id
            )
        )

    def get_lv(self):
        mate = self.mate_mgr.get_mates()[0]
        lv = max(mate.lv_in_nav, mate.lv_in_acc, mate.lv_in_bat)
        return lv

    def equip_item(self, item_id):
        if not self.is_in_port():
            # send chat
            pack = pb.GotChat(
                chat_type=pb.ChatType.SYSTEM,
                text='You can only equip or unequip items in port.'
            )
            self.session.send(pack)

            return

        if not self.has_item(item_id):
            return

        item = sObjectMgr.get_item(item_id)

        if self.get_lv() < item.lv:
            return

        if item.item_type == c.ItemType.WEAPON.value:
            self.weapon = item_id
        elif item.item_type == c.ItemType.ARMOR.value:
            self.armor = item_id

        self.session.send(
            pb.ItemEquipped(
                item_id=item_id
            )
        )

    def buy_tax_free_permit(self):
        if self.is_in_my_capital():
            self.buy_item(item_id=c.Item.TAX_FREE_PERMIT.value, force_buy=True)

    def buy_letter_of_marque(self):
        if self.is_in_my_capital():
            self.buy_item(item_id=c.Item.LETTER_OF_MARQUE.value, force_buy=True)

    def add_item(self, item_id):
        self.items.append(item_id)

        self.session.send(
            pb.ItemAdded(
                item_id=item_id
            )
        )

    def buy_item(self, item_id, force_buy=False):
        if len(self.items) >= c.MAX_ITEMS_CNT:
            # send chat
            pack = pb.MateSpeak(
                mate_template_id=1,
                text=f'max {c.MAX_ITEMS_CNT} items'
            )
            self.session.send(pack)

            return

        if force_buy:
            pass
        else:
            ids = self.get_availalbe_items_ids_in_port()
            if item_id not in ids:
                return

        item = sObjectMgr.get_item(item_id)
        if self.money < item.buy_price:
            return

        self.mod_money(-item.buy_price)
        self.add_item(item_id)

    def invest(self, ingots_cnt):
        if self.money < ingots_cnt * 10000:
            return

        port_map = sMapMgr.get_map(self.map_id)
        port_map.receive_investment(self, ingots_cnt)
        self.money -= ingots_cnt * 10000

        self.session.send(pb.MoneyChanged(
            money=self.money
        ))

        self.session.send(pb.Invested())

    def set_field(self, key, int_value, str_value):
        if str_value:
            setattr(self, key, str_value)
            self.session.send(pb.RoleFieldSet(
                key=key,
                str_value=str_value,
            ))
        else:
            setattr(self, key, int_value)
            self.session.send(pb.RoleFieldSet(
                key=key,
                int_value=int_value,
            ))

    def __get_grid_xy(self, x, y):
        grid_x = int(y / c.SIZE_OF_ONE_GRID)
        grid_y = int(x / c.SIZE_OF_ONE_GRID)
        return grid_x, grid_y

    def get_map(self):
        return sMapMgr.get_map(self.map_id)

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

    def get_fleet_speed(self, dir):
        """
        fleet_speed = min(speed of all ships)
        maybe use cache to avoid calculating every time
        """
        if self.is_dead:
            return c.DEAD_SPEED

        ships = self.ship_mgr.get_ships()
        speeds = [ship.get_speed(dir) for ship in ships]
        fleet_speed = min(speeds)

        if fleet_speed < c.DEAD_SPEED:
            fleet_speed = c.DEAD_SPEED

        return fleet_speed

    def stop_moving(self):
        self.is_moving = False

        # print(f'{self.id} stopped moving at {self.x} {self.y}')

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
            # edge cases
            if self.x <= c.WORLD_MAP_EDGE_LENGTH and \
                    self.dir in [pb.DirType.W, pb.DirType.NW, pb.DirType.SW]:
                self.change_xy(c.WORLD_MAP_COLUMNS - c.WORLD_MAP_EDGE_LENGTH, self.y)

            if self.x >= c.WORLD_MAP_COLUMNS - c.WORLD_MAP_EDGE_LENGTH and \
                self.dir in [pb.DirType.E, pb.DirType.NE, pb.DirType.SE]:
                self.change_xy(c.WORLD_MAP_EDGE_LENGTH, self.y)

            # normal cases
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

    def __clear_auras(self):
        for aura_id in list(self.auras):
            if aura_id in [c.Aura.PRAYER.value, c.Aura.DONATION.value]:
                continue
            self.remove_aura(aura_id)

    def can_enter_port(self, port_id):
        port_map = sMapMgr.get_map(port_id)
        if not port_map.allied_nation:
            return True

        notority_for_port_nation = self.notorities[port_map.allied_nation - 1]
        if notority_for_port_nation >= 100:
            # send pack
            port = sObjectMgr.get_port(port_id)
            pack = pb.CannotEnterPort(
                reason=f'{port.name} has rejected our request to enter.'
            )
            self.session.send(pack)

            return False

        return True


    def enter_port(self, port_id, x=None, y=None):
        self.is_dead = False
        self.starved_days = 0

        self.__clear_auras()

        # change map_id
        self.map_id = port_id
        harbor_x, harbor_y = sObjectMgr.get_building_xy_in_port(building_id=4, port_id=port_id)

        if x:
            self.x = x
        else:
            self.x = harbor_x

        if y:
            self.y = y
        else:
            self.y = harbor_y

        # send map changed packet
        packet = pb.MapChanged(
            role_id=self.id,
            map_id=port_id,
            x=self.x,
            y=self.y,
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
        return None

    def get_random_ship(self):
        alive_ships = [ship for ship in self.ship_mgr.get_ships() if ship.is_alive()]
        return random.choice(alive_ships)

    def get_non_flag_ships_ids(self):
        flag_ship = self.get_flag_ship()
        return [id for id, ship in self.ship_mgr.id_2_ship.items() if id != flag_ship.id]


    def is_close_to_role(self, target_role):
        distance = 3
        return abs(self.x - target_role.x) <= distance and abs(self.y - target_role.y) <= distance

    def win(self, enemy):

        if self.is_role():
            if self.is_in_battle_with_role():
                ships_cnt = len(self.ship_mgr.get_ships())
                captured_ships_cnt = 0

                # get ships
                for id in enemy.get_non_flag_ships_ids():
                    print(f'## non flagship id {id}')

                    # get chance
                    if random.random() < c.SHIP_CAPTURE_CHANCE:
                        continue

                    if ships_cnt + 1 > c.MAX_SHIPS_CNT:
                        break

                    ships_cnt += 1
                    captured_ships_cnt += 1

                    # add to my role
                    ship = enemy.ship_mgr.get_ship(id)
                    prev_ship_name = ship.name
                    ship.name = self.ship_mgr.get_new_ship_name()
                    ship.role_id = self.id
                    ship.now_crew = ship.min_crew
                    captain = ship.get_captain()
                    captain.clear_duty()
                    ship.clear_mates_onboard()

                    ship.id = sIdMgr.gen_new_ship_id()
                    self.ship_mgr.add_ship(ship)

                    ship_proto = ship.gen_ship_proto()
                    self.session.send(pb.GotNewShip(ship=ship_proto))
                    self.session.send(pb.GotChat(
                        chat_type=pb.ChatType.SYSTEM,
                        text=f'acquired ship {prev_ship_name} as {ship.name}',
                    ))

                    # remove from target role
                    del enemy.ship_mgr.id_2_ship[id]
                    enemy.session.send(pb.ShipRemoved(id=id))
                    enemy.session.send(pb.GotChat(
                        chat_type=pb.ChatType.SYSTEM,
                        text=f'lost ship {prev_ship_name}',
                    ))

                # get half of target's money
                amount = enemy.money // 2
                enemy.mod_money(-amount)
                self.mod_money(amount)

                # tell client
                self.session.send(pb.EscapedRoleBattle())
                enemy.session.send(pb.EscapedRoleBattle())

                enemy.battle_role_id = None
                self.battle_role_id = None

                # mate speak spoil of war
                pack = pb.RandMateSpeak(
                    text=f'We captured {captured_ships_cnt} ships '
                         f'and {amount} gold coins from the enemy.',
                )
                self.session.send(pack)
                self.session.send(pb.ShowWinImg())

                pack = pb.RandMateSpeak(
                    text=f'We lost {captured_ships_cnt} ships '
                         f'and {amount} gold coins to the enemy.',
                )
                enemy.session.send(pack)
                enemy.session.send(pb.ShowLoseImg())

                # notify nearby roles
                sMapMgr.add_object(self)
                sMapMgr.add_object(enemy)
                self.session.packet_handler.send_role_appeared_to_nearby_roles()
                enemy.session.packet_handler.send_role_appeared_to_nearby_roles()

            elif self.is_in_battle_with_npc():
                self.win_npc()

        elif self.is_npc():
            if self.is_in_battle_with_role():
                role = self.battle_role
                role.lose_to_npc()

    async def switch_turn_with_enemy(self):

        if self.is_role():

            # set mine to none
            self.battle_timer = None

            # enemy is role
            if self.is_in_battle_with_role():
                self.__reset_flagship(self.get_flag_ship())

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
                self.__reset_flagship(self.get_flag_ship())

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
        """timers"""

        # movment
        if self.is_moving:
            self.move_timer -= time_diff
            if self.move_timer <= 0:
                self.move(self.dir)
                self.move_timer = self.calc_move_timer()

        # battle timer
        if self.battle_timer:

            # if waited for npc to move (takes more than 0.6s)
            # time_diff can be several seconds if waited for npc to move
            if time_diff >= 0.5:
                time_diff = 0.01

            self.battle_timer -= time_diff

            if self.battle_timer <= 0:
                await self.switch_turn_with_enemy()

        # days at sea
        if self.is_at_sea() and not self.is_in_battle():
            if self.is_npc():
                pass
            else:
                self.at_sea_timer -= time_diff
                if self.at_sea_timer <= 0:
                    self.at_sea_timer = c.SUPPLY_CONSUMPTION_INVERVAL
                    self.__pass_one_day_at_sea()

    def __change_morale_and_health(self):
        if self.has_aura(c.Aura.SCURVY.value):
            self.morale -= 20
            self.health -= 20
        else:
            if self.ration >= 80:
                self.morale += self.ration - 80
                self.health += self.ration - 60
            elif self.ration >= 60:
                self.morale -= 80 - self.ration
                self.health += self.ration - 60
            else:
                self.morale -= 100 - self.ration
                self.health -= 80 - self.ration

        # limit checks
        if self.morale > 100:
            self.morale = 100
        if self.morale < 0:
            self.morale = 0

        if self.health > 100:
            self.health = 100
        if self.health < 0:
            self.health = 0

        # starve
        if self.health <= 0:
            self.die()

        self.session.send(pb.RoleFieldSet(key='morale', int_value=self.morale))
        self.session.send(pb.RoleFieldSet(key='health', int_value=self.health))

    def __consume_supply(self, supply_name):
        # get total_comsumption
        total_crew = self.ship_mgr.get_total_crew()
        total_comsumption = int(total_crew * c.SUPPLY_CONSUMPTION_PER_PERSON * self.ration / 100)

        if total_comsumption <= 0:
            total_comsumption = 1

        if self.has_aura(c.Aura.RATS.value):
            total_comsumption *= 2

        # reduce food from all ships until total_comsumption is met
        ships = self.ship_mgr.get_ships()
        for ship in ships:
            # this ship has enough
            if getattr(ship, supply_name) >= total_comsumption:
                setattr(ship, supply_name, getattr(ship, supply_name) - total_comsumption)
                total_comsumption = 0

                self.session.send(pb.SupplyConsumed(
                    ship_id=ship.id,
                    supply_name=supply_name,
                    now_cnt=getattr(ship, supply_name),
                ))

                break
            # this ship not enough
            else:
                total_comsumption -= getattr(ship, supply_name)
                setattr(ship, supply_name, 0)

                self.session.send(pb.SupplyConsumed(
                    ship_id=ship.id,
                    supply_name=supply_name,
                    now_cnt=0,
                ))

        # not enough food
        is_enough = True
        if total_comsumption > 0:
            is_enough = False

        return is_enough

    def remove_aura(self, aura_id):
        if aura_id in self.auras:
            self.auras.remove(aura_id)
            self.session.send(pb.AuraRemoved(aura_id=aura_id))

    def has_aura(self, aura_id):
        return aura_id in self.auras

    def remove_item(self, item_id):
        if item_id in self.items:
            self.items.remove(item_id)
            self.session.send(pb.ItemRemoved(item_id=item_id))

            # send chat
            pack = pb.GotChat(
                chat_type=pb.ChatType.SYSTEM,
                text=f'lost item {sObjectMgr.get_item(item_id).name}',
            )
            self.session.send(pack)

    def __reduce_notorities(self):
        for id, notority in enumerate(self.notorities):
            if notority > 0:
                self.notorities[id] -= 10
                if self.notorities[id] < 0:
                    self.notorities[id] = 0

                self.session.send(pb.NotorityChanged(
                    nation_id=id + 1,
                    now_value=self.notorities[id],
                ))

    def __destroy_permits_by_chance(self):
        if random.random() < 0.1:
            if self.has_item(c.Item.TAX_FREE_PERMIT.value):
                self.remove_item(c.Item.TAX_FREE_PERMIT.value)
            if self.has_item(c.Item.LETTER_OF_MARQUE.value):
                self.remove_item(c.Item.LETTER_OF_MARQUE.value)

    def __add_aura_by_chance(self):
        # prayer prevention
        if self.has_aura(c.Aura.PRAYER.value):
            if random.random() < 0.05:
                return

        # donation prevention
        if self.has_aura(c.Aura.DONATION.value):
            if random.random() < 0.05:
                return

        # add rats
        if random.random() < 0.05:
            if self.has_item(c.Item.CAT.value):
                pass
            else:
                aura_id = c.Aura.RATS.value
                if not self.has_aura(aura_id):
                    self.auras.add(aura_id)
                    self.session.send(pb.AuraAdded(aura_id=aura_id))

                    self.__destroy_permits_by_chance()

        # add scurvy
        if self.days_at_sea >= 30:
            if random.random() < 0.15:
                aura_id = c.Aura.SCURVY.value
                if not self.has_aura(aura_id):
                    self.auras.add(aura_id)
                    self.session.send(pb.AuraAdded(aura_id=aura_id))

        # add storm
        if random.random() < 0.02 or 1:
            aura_id = c.Aura.STORM.value
            if not self.has_aura(aura_id):
                self.auras.add(aura_id)
                self.session.send(pb.AuraAdded(aura_id=aura_id))

                self.__reduce_notorities()
                self.__destroy_permits_by_chance()

    def __pay_crew_and_mates(self):
        # pay crew
        total_crew = self.ship_mgr.get_total_crew()
        crew_payment = total_crew * c.CREW_WAGE

        # pay mates
        total_mates = len(self.mate_mgr.get_mates())
        if total_mates <= 4:
            mates_payment = 0
        else:
            mates_payment = (total_mates - 4) * c.MATE_WAGE

        total_payment = crew_payment + mates_payment
        self.mod_money(-total_payment)

        # send chat
        pack = pb.GotChat(
            chat_type=pb.ChatType.SYSTEM,
            text=f'paid {crew_payment} to crew and {mates_payment} to mates',
        )
        self.session.send(pack)

    def __modify_pay_days(self):
        self.pay_days += 1
        if self.pay_days >= c.DAYS_TO_PAY_WAGE:
            self.pay_days = 0
            self.__pay_crew_and_mates()

    def __pass_one_day_at_sea(self):
        self.days_at_sea += 1
        self.session.send(pb.OneDayPassedAtSea(days_at_sea=self.days_at_sea))

        self.__modify_pay_days()

        if self.is_dead:
            return

        is_food_enough = self.__consume_supply('food')
        is_water_enough = self.__consume_supply('water')

        if not is_food_enough or not is_water_enough:
            self.starved_days += 1
            if self.starved_days >= 2:
                self.die()
        else:
            self.__change_morale_and_health()

        self.__take_damage_from_storm()

        self.__add_aura_by_chance()

    def __add_rand_item(self):
        if len(self.items) >= c.MAX_ITEMS_CNT:
            item_name = ''
            return item_name

        items = sObjectMgr.get_items()
        item = random.choice(items)
        self.add_item(item.id)

        return item.name

    def win_npc(self):
        ships_cnt = len(self.ship_mgr.get_ships())

        captured_ships = []
        for ship in self.npc_instance.ship_mgr.get_ships():

            # get chance
            if random.random() < c.SHIP_CAPTURE_CHANCE:
                continue

            if ships_cnt + 1 > c.MAX_SHIPS_CNT:
                break

            ships_cnt += 1

            new_ship_id = self.session.server.id_mgr.gen_new_ship_id()
            ship.id = new_ship_id
            ship.name = self.ship_mgr.get_new_ship_name()
            ship.role_id = self.id
            ship.clear_mates_onboard()
            ship.now_crew = ship.min_crew
            self.ship_mgr.add_ship(ship)

            captured_ships.append(ship)

        pack = pb.YouWonNpcBattle()
        ships_prots = [ship.gen_ship_proto() for ship in captured_ships]
        pack.ships.extend(ships_prots)
        self.session.send(pack)
        self.session.send(pb.EscapedNpcBattle())

        # add random item
        item_name = self.__add_rand_item()

        # npc speak
        pack = pb.MateSpeak(
            mate_template_id=self.npc_instance.mate.mate_template_id,
            text='One day, someone from my nation will revenge for me.',
        )
        self.session.send(pack)

        # mate speak spoil of war
        pack = pb.RandMateSpeak(
            text=f'We captured {len(captured_ships)} ships and {item_name} from the enemy.',
        )
        self.session.send(pack)

        # show win img
        self.session.send(pb.ShowWinImg())

        self.npc_instance = None
        self.battle_npc_id = None

        # notify nearby roles
        sMapMgr.add_object(self)
        self.session.packet_handler.send_role_appeared_to_nearby_roles()

        # earn xp
        xp_amount = self.__calc_battle_xp_amount(captured_ships)
        flag_ship = self.get_flag_ship()
        first_mate = flag_ship.get_first_mate()
        if first_mate:
            first_mate.earn_xp(xp_amount, pb.DutyType.FIRST_MATE)

        ships = self.ship_mgr.get_ships()
        for ship in ships:
            captain = ship.get_captain()
            if captain:
                captain.earn_xp(xp_amount, pb.DutyType.FIRST_MATE)

    def __calc_battle_xp_amount(self, captured_ships):
        # get total_capacity
        total_capacity = sum([ship.capacity for ship in captured_ships])

        # get battle_skill
        flag_ship = self.get_flag_ship()
        captain_of_flag_ship = flag_ship.get_captain()
        battle_skill = captain_of_flag_ship.battle

        first_mate = flag_ship.get_first_mate()
        if first_mate:
            battle_skill = max(battle_skill, first_mate.battle)

        # cal xp
        xp_amount = int(total_capacity * battle_skill * 0.1 * c.BATTLE_XP_FACTOR)

        return xp_amount

    def lose_to_npc(self):
        for id in self.get_non_flag_ships_ids():
            self.ship_mgr.rm_ship(id)
            self.session.send(pb.ShipRemoved(id=id))

        self.__lose_money_due_to_death()

        self.session.send(pb.EscapedNpcBattle())
        self.session.send(pb.ShowLoseImg())

        self.npc_instance = None
        self.battle_npc_id = None

        # notify nearby roles
        sMapMgr.add_object(self)
        self.session.packet_handler.send_role_appeared_to_nearby_roles()


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
        self.battle_timer = None

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

    def __take_damage_from_storm(self):
        if self.has_aura(c.Aura.STORM.value):
            for ship in self.ship_mgr.get_ships():
                ship.now_durability -= int(ship.max_durability * 0.4)

                if ship.now_durability < 0:
                    ship.now_durability = 0

                self.session.send(
                    pb.ShipFieldChanged(
                        ship_id=ship.id,
                        key='now_durability',
                        int_value=ship.now_durability,
                    )
                )

            flag_ship = self.get_flag_ship()
            if flag_ship.now_durability <= 0:
                self.die()

    def __lose_money_due_to_death(self):
        self.mod_money(-int(self.money * 0.5))

    def die(self):
        self.is_dead = True
        self.fleet_speed = c.DEAD_SPEED
        self.start_moving(self.x, self.y, self.dir)
        self.session.send(pb.YouDied())

        self.ship_mgr.clear_crew()

        self.__lose_money_due_to_death()

    def stopped_moving(self, x, y, dir):
        self.is_moving = False

        old_x = self.x
        old_y = self.y

        self.x = x
        self.y = y
        self.dir = dir

        sMapMgr.move_object(self, old_x, old_y, self.x, self.y)

        pack = pb.StoppedMoving(
            id=self.id,
            src_x=self.x,
            src_y=self.y,
            dir=self.dir,
        )

        nearby_objects = sMapMgr.get_nearby_objects(self, include_self=True)
        for object in nearby_objects:
            if object.is_role():
                object.session.send(pack)

        # print(f'server: {self.id} stopped moving at ({self.x}, {self.y})')

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
                self.speed = self.get_fleet_speed(dir) #c.PORT_SPEED
                self.move_timer = self.calc_move_timer()
            elif self.is_npc():
                self.speed = c.NPC_SPEED
                # self.move_timer = self.calc_move_timer()

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

    def get_port(self):
        return sObjectMgr.get_port(self.map_id)

    def __get_ratio_from_price_index(self):
        port_map = sMapMgr.get_map(self.map_id)
        price_index = port_map.price_index
        return price_index / 100

    def is_in_allied_port(self):
        port_map = self.get_map()
        if port_map.allied_nation == self.get_nation():
            return True

    def has_tax_free_permit(self):
        if c.Item.TAX_FREE_PERMIT.value in self.items:
            return True
        else:
            return False

    def __get_modified_buy_price(self, price):
        ratio = self.__get_ratio_from_price_index()

        if self.is_in_allied_port() and self.has_tax_free_permit():
            tax_ratio = 0.9
        else:
            tax_ratio = 1

        return int(price * (1 - self.get_discount()) * ratio * tax_ratio)

    def get_available_cargos(self):
        # get cargo by region_id
        port = self.get_port()
        cargo_ids = sObjectMgr.get_cargo_ids(port.economy_id)
        available_cargos = []

        for cargo_id in cargo_ids:
            if not self.__is_cargo_available_in_my_port(cargo_id):
                continue

            cargo_template = sObjectMgr.get_cargo_template(cargo_id)
            available_cargo = pb.AvailableCargo()
            available_cargo.id = cargo_template.id
            available_cargo.name = cargo_template.name

            price = json.loads(cargo_template.buy_price)[str(port.economy_id)]
            available_cargo.price = price
            available_cargo.cut_price = self.__get_modified_buy_price(price)
            available_cargos.append(available_cargo)

        # add specialty of this port
        if port.specialty_id:
            cargo_template = sObjectMgr.get_cargo_template(port.specialty_id)
            available_cargo = pb.AvailableCargo()
            available_cargo.id = cargo_template.id
            available_cargo.name = F'{cargo_template.name}*'
            available_cargo.price = port.specialty_price
            available_cargo.cut_price = self.__get_modified_buy_price(port.specialty_price)
            available_cargos.append(available_cargo)

        pack = pb.GetAvailableCargosRes()
        pack.available_cargos.extend(available_cargos)
        self.session.send(pack)

    def __get_modified_sell_price(self, sell_price):
        ratio = self.__get_ratio_from_price_index()

        if self.is_in_allied_port() and self.has_tax_free_permit():
            tax_ratio = 1.1
        else:
            tax_ratio = 1

        return int(sell_price * (1 + self.get_discount()) * ratio * tax_ratio)

    def get_cargo_cnt_and_sell_price(self, ship_id):
        ship = self.ship_mgr.get_ship(ship_id)

        if not ship.cargo_id:
            return

        # get sell price
        cargo_template = sObjectMgr.get_cargo_template(ship.cargo_id)
        port = self.get_port()
        sell_price = json.loads(cargo_template.sell_price)[str(port.economy_id)]

        pack = pb.CargoToSellInShip()
        pack.cargo_id = ship.cargo_id
        pack.cargo_name = cargo_template.name
        pack.cnt = ship.cargo_cnt
        pack.sell_price = sell_price
        pack.modified_sell_price = self.__get_modified_sell_price(sell_price)
        pack.ship_id = ship_id
        self.session.send(pack)

    def get_discount(self):
        flag_ship = self.get_flag_ship()

        if not flag_ship:
            return 0

        accountant = flag_ship.get_accountant()
        captain = flag_ship.get_captain()

        acc_skill_to_use = None
        if not accountant:
            acc_skill_to_use = captain.accounting
        else:
            acc_skill_to_use = max(captain.accounting, accountant.accounting)

        discount = 0.2 * acc_skill_to_use * 0.01
        return discount

    def buy_cargo(self, cargo_id, cnt, ship_id):
        if not self.__is_cargo_available_in_my_port(cargo_id):
            print("cargo not available in this port")
            return

        # get cost
        cost = 0
        cargo_template = sObjectMgr.get_cargo_template(cargo_id)
        economy_id_str_2_buy_price = json.loads(cargo_template.buy_price)

        port = self.get_port()

        if str(port.economy_id) in economy_id_str_2_buy_price:
            buy_price = economy_id_str_2_buy_price[str(port.economy_id)]
        elif cargo_id == port.specialty_id:
            buy_price = port.specialty_price
        else:
            print("port dosen't have this cargo")
            return

        modified_buy_price = self.__get_modified_buy_price(buy_price)
        cost = cnt * modified_buy_price

        # not enough money
        if not self.money >= cost:
            print("not enough money")
            return

        # not enough space
        ship = self.ship_mgr.get_ship(ship_id)
        if not ship.get_max_cargo() >= cnt + ship.get_supply_cnt():
            print("not enough space")
            return

        # update ram
        self.money -= cost
        ship.add_cargo(cargo_id, cnt)

        # tell client
        pack = pb.MoneyChanged(money=self.money)
        self.session.send(pack)

        pack = pb.ShipCargoChanged(
            ship_id=ship_id,
            cargo_id=cargo_id,
            cnt=cnt,
        )
        self.session.send(pack)

    def __get_xp_amount_from_prfoit(self, profit):
        xp = int(c.TRADE_XP_FACTOR * profit // 100)
        return xp

    def sell_cargo(self, ship_id, cargo_id, cnt):
        ship = self.ship_mgr.get_ship(ship_id)

        if not ship.cargo_id:
            return
        if not ship.cargo_cnt >= cnt:
            return

        # get sell price
        cargo_template = sObjectMgr.get_cargo_template(cargo_id)
        port = self.get_port()
        sell_price = json.loads(cargo_template.sell_price)[str(port.economy_id)]
        modified_sell_price = self.__get_modified_sell_price(sell_price)

        # change ram
        profit = cnt * modified_sell_price
        self.money += profit
        ship.remove_cargo(cargo_id, cnt)

        # earn xp in acc
        flag_ship = self.get_flag_ship()
        xp_amount = self.__get_xp_amount_from_prfoit(profit)
        flag_ship.get_captain().earn_xp(xp_amount, pb.DutyType.ACCOUNTANT)
        accountant = flag_ship.get_accountant()
        if accountant:
            accountant.earn_xp(xp_amount, pb.DutyType.ACCOUNTANT)

        # tell client
        self.session.send(pb.MoneyChanged(money=self.money))
        self.session.send(pb.ShipCargoChanged(ship_id=ship_id,
                                              cargo_id=ship.cargo_id,
                                              cnt=ship.cargo_cnt))
        self.session.send(pb.PopSomeMenus(cnt=2))

    def repair_ship(self, ship_id):
        ship = self.ship_mgr.get_ship(ship_id)
        cost = ship.get_repair_cost()

        if not self.money >= cost:
            return

        self.money -= cost
        ship.repair()

        self.session.send(pb.MoneyChanged(money=self.money))
        self.session.send(
            pb.ShipRepaired(
                ship_id=ship_id,
                max_durability=ship.max_durability,
            )
        )

    def rename_ship(self, id, name):
        ship = self.ship_mgr.get_ship(id)

        ships = self.ship_mgr.get_ships()
        for ship in ships:
            if ship.name == name:
                return

        ship.name = name

        self.session.send(pb.ShipRenamed(id=id, name=name))

    def change_ship_capacity(self, id, max_crew, max_guns):
        ship = self.ship_mgr.get_ship(id)
        ship.change_capacity(max_crew, max_guns)

    def change_ship_weapon(self, ship_id, cannon_id):
        ship = self.ship_mgr.get_ship(ship_id)

        # get cost
        cannon = sObjectMgr.get_cannon(cannon_id)
        cost = cannon.price * ship.max_guns
        if not self.money >= cost:
            return

        self.money -= cost
        ship.change_weapon(cannon_id)

        self.session.send(pb.MoneyChanged(money=self.money))
        self.session.send(pb.ShipWeaponChanged(ship_id=ship_id, cannon_id=cannon_id))

    def recruit_crew(self, ship_id, cnt):
        ship = self.ship_mgr.get_ship(ship_id)

        if not ship.max_crew >= ship.now_crew + cnt:
            return

        if cnt > self.recruited_crew_cnt:
            self.session.send(pb.BuildingSpeak(
                text=f'Only {self.recruited_crew_cnt} sailors are willing to join you today.'))

            return

        self.recruited_crew_cnt -= cnt
        ship.add_crew(cnt)
        self.session.send(pb.CrewRecruited(ship_id=ship_id, cnt=cnt))

    def dismiss_crew(self, ship_id, cnt):
        ship = self.ship_mgr.get_ship(ship_id)

        if not ship.now_crew >= cnt:
            return

        ship.reduce_crew(cnt)

        self.session.send(pb.CrewDismissed(ship_id=ship_id, cnt=cnt))

    def load_supply(self, ship_id, supply_name, cnt):
        ship = self.ship_mgr.get_ship(ship_id)

        # get cost
        cost = cnt * c.SUPPLY_2_COST[supply_name]
        if not self.money >= cost:
            return

        if not ship.can_load(cnt):
            return

        self.money -= cost
        ship.add_supply(supply_name, cnt)

        now_supply = getattr(ship, f'{supply_name}')

        self.session.send(pb.MoneyChanged(money=self.money))
        self.session.send(
            pb.SupplyChanged(ship_id=ship_id, supply_name=supply_name, cnt=now_supply)
        )

    def unload_supply(self, ship_id, supply_name, cnt):
        ship = self.ship_mgr.get_ship(ship_id)

        if cnt > getattr(ship, f'{supply_name}'):
            cnt = getattr(ship, f'{supply_name}')

        ship.remove_supply(supply_name, cnt)

        now_supply = getattr(ship, f'{supply_name}')

        self.session.send(
            pb.SupplyChanged(ship_id=ship_id, supply_name=supply_name, cnt=now_supply)
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

    def sail(self):
        self.has_treated = False

        flag_ship = self.get_flag_ship()
        if not flag_ship:
            return

        for ship in self.ship_mgr.get_ships():
            captain = ship.get_captain()
            if not captain:
                self.session.send(
                    pb.BuildingSpeak(
                        text=f'One of your ships has no captain.'
                    )
                )

                return

        # tell port nearby roles
        self.session.packet_handler.send_role_disappeared_to_nearby_roles()

        # update map_mgr
        port = sObjectMgr.get_port(self.map_id)

        sailable_x, sailable_y = self.__get_sailable_x_y_around_port(port.x, port.y)

        if not sailable_x:
            return

        sMapMgr.change_object_map(self,
                                  self.map_id, self.x, self.y,
                                  0, sailable_x, sailable_y)

        # update model
        self.map_id = 0
        self.x = sailable_x
        self.y = sailable_y

        # tell client
        self.session.send(
            pb.MapChanged(
                role_id=self.id,
                map_id=0,
                x=sailable_x,
                y=sailable_y,
            )
        )

        self.days_at_sea = 0
        self.at_sea_timer = c.SUPPLY_CONSUMPTION_INVERVAL
        self.session.send(
            pb.OneDayPassedAtSea(days_at_sea=self.days_at_sea)
        )

        # tell nearby_roles_at_sea
        self.session.packet_handler.send_role_appeared_to_nearby_roles()

    def __add_notority(self, nation_id, amount):
        if self.has_item(c.Item.LETTER_OF_MARQUE.value):
            amount *= 0.5
            amount = int(amount)

        self.notorities[nation_id - 1] += amount
        if self.notorities[nation_id - 1] > 100:
            self.notorities[nation_id - 1] = 100

        pack = pb.NotorityChanged(
            nation_id=nation_id,
            now_value=self.notorities[nation_id - 1],
        )
        self.session.send(pack)

    def fight_npc(self, npc_id):
        npc = self.session.server.npc_mgr.get_npc(npc_id)

        if self.is_dead:
            return

        if not self.is_close_to_role(npc):
            return

        # add notority to npc nation
        npc_nation = npc.get_nation()
        self.__add_notority(npc_nation, 20)

        self.is_moving = False

        # notify nearby roles
        sMapMgr.rm_object(self)
        self.session.packet_handler.send_role_disappeared_to_nearby_roles()

        self.battle_npc_id = npc_id

        # gen npc_instance (each role has its own instance)
        npc_instance = copy.deepcopy(npc)
        self.npc_instance = npc_instance
        npc_instance.battle_role_id = self.id
        npc_instance.battle_role = self

        self.ship_mgr.init_ships_positions_in_battle(is_attacker=True)
        npc_instance.ship_mgr.init_ships_positions_in_battle(is_attacker=False)

        pack = pb.EnteredBattleWithNpc(
            npc_id=npc_id,
            ships=npc_instance.ship_mgr.gen_ships_prots(),
        )

        self.session.send(pack)

        #### copied
        # init battle_role_id and enemy ships
        # init my ships pos
        for id, ship in self.ship_mgr.id_2_ship.items():
            self.session.send(pb.ShipMoved(
                id=id,
                x=ship.x,
                y=ship.y,
                dir=ship.dir,
                steps_left=ship.steps_left,
            ))

        # init battle_timer (updated each session update)
        self.battle_timer = c.BATTLE_TIMER_IN_SECONDS

        pack = pb.BattleTimerStarted(
            battle_timer=self.battle_timer,
            role_id=self.id,
        )
        self.session.send(pack)

        # npc speak
        pack = pb.MateSpeak(
            mate_template_id=self.npc_instance.mate.mate_template_id,
            text='You are pretty brave to challenge us.',
        )
        self.session.send(pack)

    def get_nation(self):
        return self.nation

    def fight_role(self, role_id):
        target_role = self.session.server.get_role(role_id)

        if self.is_dead or target_role.is_dead:
            return

        if not self.is_close_to_role(target_role):
            return

        # add notority to npc nation
        target_nation = target_role.get_nation()
        self.__add_notority(target_nation, 20)

        # stop moving
        self.is_moving = False
        target_role.is_moving = False

        self.session.packet_handler.send_role_disappeared_to_nearby_roles()
        target_role.session.packet_handler.send_role_disappeared_to_nearby_roles()

        sMapMgr.rm_object(self)
        sMapMgr.rm_object(target_role)

        # init battle_role_id and enemy ships
        self.battle_role_id = target_role.id
        target_role.battle_role_id = self.id

        self.ship_mgr.init_ships_positions_in_battle(is_attacker=True)
        target_role.ship_mgr.init_ships_positions_in_battle(is_attacker=False)

        pack = pb.EnteredBattleWithRole(
            role_id=target_role.id,
            ships=target_role.ship_mgr.gen_ships_prots(),
        )
        self.session.send(pack)

        # init my ships pos
        for id, ship in self.ship_mgr.id_2_ship.items():
            self.session.send(pb.ShipMoved(
                id=id,
                x=ship.x,
                y=ship.y,
                dir=ship.dir,
                steps_left=ship.steps_left,
            ))

        pack = pb.EnteredBattleWithRole(
            role_id=self.id,
            ships=self.ship_mgr.gen_ships_prots(),
        )
        target_role.session.send(pack)

        # init enemy ships pos
        for id, ship in target_role.ship_mgr.id_2_ship.items():
            target_role.session.send(pb.ShipMoved(
                id=id,
                x=ship.x,
                y=ship.y,
                dir=ship.dir,
                steps_left=ship.steps_left,
            ))

        # init battle_timer (updated each session update)
        self.battle_timer = c.BATTLE_TIMER_IN_SECONDS

        pack = pb.BattleTimerStarted(
            battle_timer=self.battle_timer,
            role_id=self.id,
        )
        self.session.send(pack)
        target_role.session.send(pack)


class Model:

    def __init__(self):
        self.role = None
        self.id_2_role = {}
