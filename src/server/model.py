from dataclasses import dataclass
import asyncio
import random
import login_pb2 as pb
# import from dir
import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared')

import constants as c
from object_mgr import sObjectMgr

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

    x: int=None
    y: int=None

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

        damage = 10
        ship.now_durability -= damage

        is_sunk = False
        if ship.now_durability <= 0:
            is_sunk = True


        return damage, is_sunk

    def engage(self, ship):
        self.now_crew -= 5
        ship.now_crew -= 5

    def move(self, dir):
        if dir == pb.DirType.E:
            self.x += 50

    def is_target_in_range(self, ship):
        return abs(self.x - ship.x) <= 200 and abs(self.y - ship.y) <= 200

    def attack(self, ship):
        # shoot or engage based on strategy
        pass

    def is_alive(self):
        return self.now_durability > 0

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

    def init_ships_positions_in_battle(self, is_attacker=True):

        for id, ship in enumerate(self.id_2_ship.values()):
            if is_attacker:
                ship.x = 150
                ship.y = 40 + id * 80
            else:
                ship.x = 500
                ship.y = 40 + id * 80

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

    def __get_grid_xy(self, x, y):
        grid_x = int(y / c.SIZE_OF_ONE_GRID)
        grid_y = int(x / c.SIZE_OF_ONE_GRID)
        return grid_x, grid_y

    def move(self, dir):

        distance = 1

        if dir == pb.DirType.E:
            self.x += distance
        elif dir == pb.DirType.W:
            self.x -= distance
        elif dir == pb.DirType.N:
            self.y -= distance
        elif dir == pb.DirType.S:
            self.y += distance

        # make packet
        pack = pb.RoleMoved()
        pack.id = self.id
        pack.x = self.x
        pack.y = self.y
        pack.dir_type = dir
        self.session.packet_handler.send_to_nearby_roles(pack, include_self=True)

        # check opened grid?
        grid_x, grid_y = self.__get_grid_xy(self.x, self.y)
        if self.seen_grids[grid_x][grid_y] == 0:
            self.seen_grids[grid_x][grid_y] = 1
            self.session.send(pb.OpenedGrid(grid_x=grid_x, grid_y=grid_y))

    def enter_port(self, port_id):
        # change map_id
        self.map_id = port_id

        # change x y to harbor x y
        # should be inited beforehand (later)

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
        self.session.packet_handler.send_to_nearby_roles(packet, include_self=True)

    def get_enemy_role(self):
        self.session.packet_handler.get_enemy_role()

    def get_flag_ship(self):
        for id, ship in self.ship_mgr.id_2_ship.items():
            mate_id = ship.captain
            if not mate_id:
                continue

            mate = self.mate_mgr.get_mate(mate_id)
            if mate.name == self.name:
                return ship


    def get_random_ship(self):
        ship_ids = self.ship_mgr.id_2_ship.keys()
        return self.ship_mgr.id_2_ship[random.choice(list(ship_ids))]

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

            ship_proto = ship.gen_ship_proto()
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

    async def npc_all_ships_attack_me(self):
        # get enemy role
        enemy_npc = self.npc_instance
        enemy_role = self
        flag_ship = enemy_role.get_flag_ship()

        for ship in enemy_npc.ship_mgr.id_2_ship.values():

            enemy_ship = enemy_role.get_random_ship()

            damage, is_sunk = ship.shoot(enemy_ship)

            pack = pb.ShipAttacked(
                src_id=ship.id,
                dst_id=enemy_ship.id,
                attack_method_type=pb.AttackMethodType.SHOOT,
                dst_damage=damage,
            )
            self.session.send(pack)

            pack = pb.GotChat(
                text=f"{ship.name} shot {enemy_ship.name} and dealt {damage} damage",
                chat_type=pb.ChatType.SYSTEM
            )
            self.session.send(pack)

            if is_sunk:

                if enemy_ship.id == flag_ship.id:
                    self.lose_to_npc()
                    return

                if enemy_ship.id not in enemy_role.ship_mgr.id_2_ship:
                    continue

                enemy_role.ship_mgr.rm_ship(enemy_ship.id)

                pack = pb.ShipRemoved(
                    id=enemy_ship.id
                )
                self.session.send(pack)

            await asyncio.sleep(1)

        # give back timer
        self.battle_timer = c.BATTLE_TIMER_IN_SECONDS
        pack = pb.BattleTimerStarted(
            battle_timer=self.battle_timer,
            role_id=self.id,
        )
        self.session.send(pack)


    async def switch_turn_with_enemy(self):
        # set mine to none
        self.battle_timer = None

        # enemy is role
        if self.battle_role_id:
            enemy_role = self.session.packet_handler.get_enemy_role()
            enemy_role.battle_timer = c.BATTLE_TIMER_IN_SECONDS

            pack = pb.BattleTimerStarted(
                battle_timer=enemy_role.battle_timer,
                role_id=enemy_role.id,
            )
            self.session.send(pack)
            enemy_role.session.send(pack)

        # if enemy is npc
        elif self.battle_npc_id:
            enemy_npc = self.npc_instance
            enemy_npc.battle_timer = c.BATTLE_TIMER_IN_SECONDS

            pack = pb.BattleTimerStarted(
                battle_timer=enemy_npc.battle_timer,
                role_id=0,
            )
            self.session.send(pack)

            # enemy npc attack
            await self.npc_all_ships_attack_me()

    async def update(self, time_diff):
        # movment
        if self.is_moving:
            print('updating move timer')

            self.move_timer -= time_diff

            print('updated move timer')
            if self.move_timer <= 0:
                self.move(self.dir)
                self.move_timer = c.MOVE_TIMER_IN_PORT

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

    def lose_to_npc(self):
        for id in self.get_non_flag_ships_ids():
            self.ship_mgr.rm_ship(id)
            self.session.send(pb.ShipRemoved(id=id))

        self.session.send(pb.EscapedNpcBattle())

        self.npc_instance = None
        self.battle_npc_id = None

    async def all_ships_attack_npc(self):
        # get enemy role
        enemy_npc = self.npc_instance
        # flag_ship = enemy_npc.get_flag_ship()
        flag_ship = enemy_npc.get_flag_ship()

        for ship in self.ship_mgr.id_2_ship.values():

            # enemy_ship = enemy_npc.get_random_ship()

            enemy_ship = flag_ship

            # move and check is_in_range

            # for i in range(3):
            #     ship.move(pb.DirType.E)
            #     pack = pb.ShipMoved(
            #         id=ship.id,
            #         x=ship.x,
            #         y=ship.y,
            #     )
            #     self.send_to_self_and_enemy(pack)
            #     await asyncio.sleep(0.3)
            #
            # if not ship.is_target_in_range(enemy_ship):
            #     continue

            damage, is_sunk = ship.shoot(enemy_ship)

            pack = pb.ShipAttacked(
                src_id=ship.id,
                dst_id=enemy_ship.id,
                attack_method_type=pb.AttackMethodType.SHOOT,
                dst_damage=damage,
            )
            self.session.send(pack)

            pack = pb.GotChat(
                text=f"{ship.name} shot {enemy_ship.name} and dealt {damage} damage",
                chat_type=pb.ChatType.SYSTEM
            )
            self.session.send(pack)

            if is_sunk:

                if enemy_ship.id == flag_ship.id:
                    self.win_npc()
                    return

                if enemy_ship.id not in enemy_npc.ship_mgr.id_2_ship:
                    continue

                enemy_npc.ship_mgr.rm_ship(enemy_ship.id)

                pack = pb.ShipRemoved(
                    id=enemy_ship.id
                )
                self.session.send(pack)

            await asyncio.sleep(1)

        # switch battle timer
        await self.switch_turn_with_enemy()

    def send_to_self_and_enemy(self, pack):
        self.session.packet_handler.send_to_self_and_enemy(pack)

    async def all_ships_attack_role(self):
        # get enemy role
        enemy_role = self.session.packet_handler.get_enemy_role()
        flag_ship = enemy_role.get_flag_ship()

        for ship in self.ship_mgr.id_2_ship.values():

            enemy_ship = enemy_role.get_random_ship()

            damage, is_sunk = ship.shoot(enemy_ship)

            pack = pb.ShipAttacked(
                src_id=ship.id,
                dst_id=enemy_ship.id,
                attack_method_type=pb.AttackMethodType.SHOOT,
                dst_damage=damage,
            )
            self.send_to_self_and_enemy(pack)

            pack = pb.GotChat(
                text=f"{ship.name} shot {enemy_ship.name} and dealt {damage} damage",
                chat_type=pb.ChatType.SYSTEM
            )
            self.send_to_self_and_enemy(pack)

            if is_sunk:

                if enemy_ship.id == flag_ship.id:
                    self.win(enemy_role)
                    return

                if enemy_ship.id not in enemy_role.ship_mgr.id_2_ship:
                    continue

                enemy_role.ship_mgr.rm_ship(enemy_ship.id)

                pack = pb.ShipRemoved(
                    id=enemy_ship.id
                )
                self.send_to_self_and_enemy(pack)

            await asyncio.sleep(1)

        # switch battle timer
        await self.switch_turn_with_enemy()

class Model:

    def __init__(self):
        self.role = None
        self.id_2_role = {}
