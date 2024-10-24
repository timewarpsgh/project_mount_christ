import random

import pygame
import sys
from enum import Enum, auto
from login_pb2 import *
import login_pb2 as pb

sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared')

import constants as c

from asset_mgr import sAssetMgr
from map_maker import sMapMaker
from object_mgr import sObjectMgr
from model import Role

FONT_SIZE = 16
YELLOW = (255, 255, 0)
RED = (255, 0, 0)


def get_image(sheet, x, y, width, height, colorkey=(0,0,0), scale=1):
    image = pygame.Surface([width, height])
    rect = image.get_rect()

    image.blit(sheet, (0, 0), (x, y, width, height))
    image.set_colorkey(colorkey)
    image = pygame.transform.scale(image,
                               (int(rect.width * scale),
                                int(rect.height * scale)))
    return image


def lerp(a, b, t):
    """Linear interpolation between two points."""
    return a + (b - a) * t


def x_y_to_image(x, y, is_ship=True):
    if is_ship:
        tile_set_img = sAssetMgr.images['player']['ship-tileset']
    else:
        tile_set_img = sAssetMgr.images['player']['person_tileset']

    tile_size = c.SHIP_SIZE_IN_PIXEL
    # make a [transparent] pygame surface
    ship_surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
    x_coord = -tile_size * (x - 1)
    y_coord = -tile_size * (y - 1)
    rect = pygame.Rect(x_coord, y_coord, tile_size, tile_size)
    ship_surface.blit(tile_set_img, rect)

    return ship_surface


class SpriteSheet():
    def __init__(self, image, collumns, rows):
        self.image = image
        self.rect = self.image.get_rect()
        self.collumns = collumns
        self.rows = rows

        self.unit_width = int(self.rect.width / self.collumns)
        self.unit_height = int(self.rect.height / self.rows)

        self.frame_count = self.rows * self.collumns
        self.frames = [None] * self.frame_count
        for frame_id in range(self.frame_count):
            image_x = (frame_id % self.collumns) *  self.unit_width
            image_y = (frame_id // self.rows) *  self.unit_height
            self.frames[frame_id] = get_image(self.image, image_x, image_y,
                                              self.unit_width, self.unit_height)

    def get_frames(self):
        return self.frames


class ShipDot():
    """on mini_map in battle"""
    def __init__(self, color):
        self.image = pygame.Surface((c.SHIP_DOT_SIZE, c.SHIP_DOT_SIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect()


class Text():
    def __init__(self, text, color=c.BLACK, x=None, y=None):
        self.image = sAssetMgr.font.render(text, True, color)
        self.rect = self.image.get_rect()

        if x is not None:
            self.rect.x = x
        if y is not None:
            self.rect.y = y

class PortNpc():

    def __init__(self, frames=None, x=None, y=None, animation=None):
        self.frames = frames
        # close to building entrance
        self.x = x
        self.y = y
        self.animation = animation

    def get_xy_relative_to_role(self, role):
        x = (self.x - role.x) * c.PIXELS_COVERED_EACH_MOVE \
            + c.WINDOW_WIDTH // 2
        y = (self.y - role.y) * c.PIXELS_COVERED_EACH_MOVE \
            + c.WINDOW_HEIGHT // 2

        return x, y


class SP(pygame.sprite.Sprite):

    def __init__(self, image, x, y, z=0):
        pygame.sprite.Sprite.__init__(self)


        self.image = image
        self.rect = image.get_rect().move(x, y)
        self.img_src = image
        self.z = z

        # for move_to_smoothly
        self.start_time = None
        self.target_position = None
        self.duration = None

    def on_click(self, event):
        pass

    def stop_moving(self):
        self.start_time = None

    def update(self, time_diff):

        if not self.start_time:
            return

        # Calculate elapsed time and interpolate the position
        current_time = pygame.time.get_ticks() / 1000.0
        elapsed_time = current_time - self.start_time

        if elapsed_time < self.duration:
            t = elapsed_time / self.duration
            position = (lerp(self.start_position[0], self.target_position[0], t),
                        lerp(self.start_position[1], self.target_position[1], t))
        else:
            position = self.target_position
            self.start_time = None

        # only move if 1 pixels have changed
        pixcels_to_move = 1
        if abs(position[0] - self.rect.x) >= pixcels_to_move or \
                abs(position[1] - self.rect.y) >= pixcels_to_move:
            self.move_to(position[0], position[1])

    def change_img(self, img):
        self.image = img

    def move_to(self, x, y):
        self.rect = self.image.get_rect().move(x, y)

    def move_to_smoothly(self, x, y, given_time):
        self.start_time = pygame.time.get_ticks() / 1000.0
        self.start_position = (self.rect.x, self.rect.y)
        self.target_position = (x, y)
        self.duration = given_time


class Animation(SP):

    def __init__(self, frames, time_between_frames, x, y, loop_cnt=1):
        self.frames = frames
        self.time_between_frames = time_between_frames
        self.frame_index = 0
        self.frame_change_timer = time_between_frames
        self.__reset_frame_timer()

        self.loop_cnt = loop_cnt
        self.now_loop = 1

        image = self.frames[0]
        super().__init__(image, x, y, z=1)

    def __reset_frame_timer(self):
        self.frame_change_timer = self.time_between_frames

    def update(self, time_diff):
        super().update(time_diff)

        self.frame_change_timer -= time_diff
        if self.frame_change_timer <= 0:
            self.__reset_frame_timer()

            if self.frame_index < len(self.frames) - 1:
                self.frame_index += 1
                self.change_img(self.frames[self.frame_index])
            else:
                self.now_loop += 1
                if self.now_loop > self.loop_cnt:
                    self.kill()
                else:
                    self.frame_index = 0
                    self.change_img(self.frames[0])


class MoveMark():

    def __init__(self, x, y, dir):
        self.x = c.WINDOW_WIDTH // 2 + x * c.BATTLE_TILE_SIZE
        self.y = c.WINDOW_HEIGHT // 2 + y * c.BATTLE_TILE_SIZE
        self.img = sAssetMgr.images['in_battle']['move_mark']
        self.rect = self.img.get_rect().move(self.x, self.y)
        self.dir = dir

    def on_click(self, client):
        client.send(pb.FlagShipMove(battle_dir_type=self.dir))


class ShootMark():

    def __init__(self, x, y, target_ship_id):
        self.x = x
        self.y = y
        self.img = sAssetMgr.images['in_battle']['shoot_mark']
        self.rect = self.img.get_rect().move(self.x, self.y)
        self.target_ship_id = target_ship_id

    def on_click(self, client):
        client.send(
            pb.FlagShipAttack(
                attack_method_type=pb.AttackMethodType.SHOOT,
                target_ship_id=self.target_ship_id,
            )
        )

class EngageMark():

    def __init__(self, x, y, target_ship_id):
        self.x = x
        self.y = y
        self.img = sAssetMgr.images['in_battle']['engage_sign']
        self.rect = self.img.get_rect().move(self.x, self.y)
        self.target_ship_id = target_ship_id

    def on_click(self, client):
        client.send(
            pb.FlagShipAttack(
                attack_method_type=pb.AttackMethodType.ENGAGE,
                target_ship_id=self.target_ship_id,
            )
        )


class BackGround(SP):
    def __init__(self, model, image, x, y):
        super().__init__(image, x, y, z=0)
        self.model = model

        self.mini_map_bg = pygame.Surface((c.MINI_MAP_SIZE, c.MINI_MAP_SIZE)).convert_alpha()
        self.mini_map_bg.fill(c.TRANS_GRAY)

        self.my_ship_dot = ShipDot(c.YELLOW)
        self.enemy_ship_dot = ShipDot(c.RED)

    def update(self, time_diff):
        super().update(time_diff)

        # in battle update
        if self.model.role:
            if not self.model.role.is_in_battle():
                return

            if self.model.role.battle_timer > 0:
                self.model.role.battle_timer -= time_diff

            self.__update_battle_scene()

    def __update_battle_scene(self):
        battle_ground_img = self.__init_new_battle_ground_img()
        self.__paste_battle_timer(battle_ground_img)
        my_flag_ship = self.model.role.get_flag_ship()

        ships_positions = self.__paste_ships(battle_ground_img, my_flag_ship)

        if not self.model.role.has_attacked:
            self.__paste_move_marks(battle_ground_img, my_flag_ship, ships_positions)
            self.__paste_attack_marks(battle_ground_img, my_flag_ship)

        # paste ships stats
        self.__paste_my_ships_stats(battle_ground_img)
        self.__paste_enemy_ships_stats(battle_ground_img)

        # paste mini map
        self.__paste_mini_map(battle_ground_img)

        self.change_img(battle_ground_img)

    def __paste_mini_map(self, battle_ground_img):
        self.__paste_dots_on_mini_map()
        battle_ground_img.blit(self.mini_map_bg, (10, 270))

    def __paste_dots_on_mini_map(self):

        # clear
        self.mini_map_bg.fill(c.TRANS_GRAY)

        # get flag ship
        flag_ship = self.model.role.get_flag_ship()

        off_set = c.MINI_MAP_SIZE // 2

        # draw my ships dots
        for id, ship in enumerate(self.model.role.ship_mgr.get_ships()):
            if ship.name == flag_ship.name:
                x = off_set
                y = off_set
            else:
                x = (ship.x - flag_ship.x) * 3 + off_set
                y = (ship.y - flag_ship.y) * 3 + off_set

            self.mini_map_bg.blit(self.my_ship_dot.image, (x, y))

        # draw enemy ships dots
        for ship in self.model.get_enemy().ship_mgr.get_ships():
            x = (ship.x - flag_ship.x) * 3 + off_set
            y = (ship.y - flag_ship.y) * 3 + off_set

            self.mini_map_bg.blit(self.enemy_ship_dot.image, (x, y))

    def __paste_enemy_ships_stats(self, battle_ground_img):
        # ships states
        for id, ship in enumerate(self.model.get_enemy().ship_mgr.get_ships()):
            num_text = Text(str(id), c.BLACK,
                            c.WINDOW_WIDTH - 80, (id + 2) * 20)
            hp_text = Text(str(ship.now_durability), c.YELLOW,
                           c.WINDOW_WIDTH - 80 + 20, (id + 2) * 20)
            crew_text = Text(str(ship.now_crew), c.WHITE,
                             c.WINDOW_WIDTH - 80 + 40, (id + 2) * 20)

            for item in [num_text, hp_text, crew_text]:
                battle_ground_img.blit(item.image, item.rect)

    def __paste_my_ships_stats(self, battle_ground_img):
        # ships states
        for id, ship in enumerate(self.model.role.ship_mgr.get_ships()):
            # all ships
            num_text = Text(str(id), c.BLACK, 10, (id + 2) * 20)
            hp_text = Text(str(ship.now_durability), c.YELLOW, 30, (id + 2) * 20)
            crew_text = Text(str(ship.now_crew), c.WHITE, 50, (id + 2) * 20)

            for item in [num_text, hp_text, crew_text]:
                battle_ground_img.blit(item.image, item.rect)

            # non flag ships
            if id != 0:

                strategy_name = c.STRATEGY_2_TEXT[ship.strategy] if ship.strategy is not None else ''
                strategy_text = Text(strategy_name, c.ORANGE, 80, (id + 2) * 20)

                target_name = ship.target_ship.name if ship.target_ship else ''
                target_text = Text(str(target_name), c.CRIMSON, 130, (id + 2) * 20)

                for item in [strategy_text, target_text]:
                    battle_ground_img.blit(item.image, item.rect)

    def __paste_attack_marks(self, battle_ground_img, my_flag_ship):
        enemy = self.model.get_enemy()

        shoot_marks = []
        engage_marks = []

        for ship in enemy.ship_mgr.get_ships():
            if not ship.is_alive():
                continue
            if my_flag_ship.steps_left <= 0:
                continue

            x, y = ship.get_screen_xy(my_flag_ship)

            if my_flag_ship.can_engage(ship):
                engage_mark = EngageMark(x, y, ship.id)
                battle_ground_img.blit(engage_mark.img, (engage_mark.x, engage_mark.y))
                engage_marks.append(engage_mark)

            elif my_flag_ship.can_shoot(ship):
                shoot_mark = ShootMark(x, y, ship.id)
                battle_ground_img.blit(shoot_mark.img, (shoot_mark.x, shoot_mark.y))
                shoot_marks.append(shoot_mark)

        self.model.role.graphics.shoot_marks = shoot_marks
        self.model.role.graphics.engage_marks = engage_marks

    def __init_new_battle_ground_img(self):
        battle_ground_img = sAssetMgr.images['in_battle']['battle']
        width, height = battle_ground_img.get_rect().size
        battle_ground_img = pygame.transform.scale(battle_ground_img, (width, height))
        return battle_ground_img

    def __paste_battle_timer(self, battle_ground_img):
        if self.model.role.is_battle_timer_mine:
            text = 'your turn'
        else:
            text = 'enemy turn'

        timer_text = Text(f'{text} {int(self.model.role.battle_timer)}', c.YELLOW, 10, 10)
        battle_ground_img.blit(timer_text.image, timer_text.rect)

    def __paste_ships(self, battle_ground_img, my_flag_ship):
        ships_positions = []

        # my ships
        my_ships = self.model.role.ship_mgr.id_2_ship.values()
        for id, ship in enumerate(my_ships):
            ship.role = self.model.role
            ship_in_battle_img = sAssetMgr.images['ship_in_battle'][str(ship.dir)]

            x, y = ship.get_screen_xy(my_flag_ship)
            battle_ground_img.blit(ship_in_battle_img, (x, y))

            if ship.is_alive():
                ship_name_text = Text(f'{id}', c.WHITE)
                battle_ground_img.blit(ship_name_text.image, (x , y))

            ships_positions.append([x, y])

        # enemy ships
        enemy = self.model.get_enemy()
        enemy_ships = enemy.ship_mgr.id_2_ship.values()
        for id, ship in enumerate(enemy_ships):
            ship_in_battle_img = sAssetMgr.images['ship_in_battle']['enemy'][str(ship.dir)]
            x, y = ship.get_screen_xy(my_flag_ship)
            battle_ground_img.blit(ship_in_battle_img, (x, y))

            if ship.is_alive():
                ship_name_text = Text(f'{id}', c.YELLOW)
                battle_ground_img.blit(ship_name_text.image, (x, y))

            ships_positions.append([x, y])

        return ships_positions

    def __paste_move_marks(self, battle_ground_img, my_flag_ship, ships_positions):
        move_marks_offsets = c.DIR_2_MOVE_MARKS_OFFSETS[my_flag_ship.dir]
        left_move_mark = MoveMark(move_marks_offsets[0][0],
                                  move_marks_offsets[0][1],
                                  pb.BattleDirType.LEFT)
        right_move_mark = MoveMark(move_marks_offsets[1][0],
                                   move_marks_offsets[1][1],
                                   pb.BattleDirType.RIGHT)
        cur_move_mark = MoveMark(move_marks_offsets[2][0],
                                 move_marks_offsets[2][1],
                                 pb.BattleDirType.CUR)

        move_marks = [left_move_mark, right_move_mark, cur_move_mark]
        valid_move_marks = []
        if my_flag_ship.steps_left >= 1:
            for move_mark in move_marks:
                if [move_mark.x, move_mark.y] in ships_positions:
                    continue

                battle_ground_img.blit(move_mark.img, (move_mark.x, move_mark.y))
                valid_move_marks.append(move_mark)

        self.model.role.graphics.move_marks = valid_move_marks


class SaySP(SP):

    def __init__(self, text, x, y):
        image = sAssetMgr.font.render(text, True, c.WHITE)
        super().__init__(image, x, y, z=3)
        self.timer = 5

    def update(self, time_diff):
        self.timer -= time_diff
        if self.timer <= 0:
            self.kill()

        super().update(time_diff)

class ShootDamageNumber(SP):

    def __init__(self, number, x, y, color=c.YELLOW):
        image = sAssetMgr.font.render(str(number), True, color)
        super().__init__(image, x, y)

        self.frames = [None] * 50
        self.frame_timer = 0
        scale = 3
        for i in range(len(self.frames)):
            scale -= 0.03
            self.frames[i] = pygame.transform.scale(self.image,
                                                (int(self.rect.width * scale),
                                                 int(self.rect.height * scale)))
        self.frame_index = -1

        self.image = self.frames[-1]

        self.rect.x = x
        self.rect.y = y

        self.x_speed = 1.4
        self.y_speed = 3
        self.d_y = 0.15

    def update(self, time_diff):
        self.frame_timer -= time_diff
        if self.frame_timer <= 0:
            self.frame_timer = 0.020
            self._change_state()

    def _change_state(self):
        if self.frame_index < len(self.frames) - 1:
            self.frame_index += 1
            self.image = self.frames[self.frame_index]

            self.rect.y -= self.y_speed
            self.y_speed -= self.d_y
            self.rect.x += self.x_speed
        else:
            self.kill()


class CannonBall(SP):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(sAssetMgr.images['in_battle']['cannon'], x1, y1)
        self.move_to_smoothly(x2, y2, given_time=0.6)

    def update(self, time_diff):
        super().update(time_diff)

        if not self.start_time:
            self.kill()


class RoleSP(SP):

    def __init__(self, model, role, image, x, y, is_mine=True, z=1):
        self.is_mine = is_mine
        self.role = role
        self.frames = {
            'at_sea' : {
                pb.DirType.N : [x_y_to_image(1, 2), x_y_to_image(2, 2)],
                pb.DirType.E : [x_y_to_image(3, 2), x_y_to_image(4, 2)],
                pb.DirType.S : [x_y_to_image(5, 2), x_y_to_image(6, 2)],
                pb.DirType.W : [x_y_to_image(7, 2), x_y_to_image(8, 2)],

                pb.DirType.NW: [x_y_to_image(7, 2), x_y_to_image(8, 2)],
                pb.DirType.NE: [x_y_to_image(3, 2), x_y_to_image(4, 2)],
                pb.DirType.SW: [x_y_to_image(7, 2), x_y_to_image(8, 2)],
                pb.DirType.SE: [x_y_to_image(3, 2), x_y_to_image(4, 2)],

            },
            'in_port': {
                pb.DirType.N : [x_y_to_image(1, 1, False), x_y_to_image(2, 1, False)],
                pb.DirType.E : [x_y_to_image(3, 1, False), x_y_to_image(4, 1, False)],
                pb.DirType.S : [x_y_to_image(5, 1, False), x_y_to_image(6, 1, False)],
                pb.DirType.W : [x_y_to_image(7, 1, False), x_y_to_image(8, 1, False)],
            },
            'man_in_port': {
                pb.DirType.N: [x_y_to_image(17, 1, False), x_y_to_image(18, 1, False)],
                pb.DirType.E: [x_y_to_image(19, 1, False), x_y_to_image(20, 1, False)],
                pb.DirType.S: [x_y_to_image(21, 1, False), x_y_to_image(22, 1, False)],
                pb.DirType.W: [x_y_to_image(23, 1, False), x_y_to_image(24, 1, False)],
            },
            'woman_in_port': {
                pb.DirType.N: [x_y_to_image(9, 1, False), x_y_to_image(10, 1, False)],
                pb.DirType.E: [x_y_to_image(11, 1, False), x_y_to_image(12, 1, False)],
                pb.DirType.S: [x_y_to_image(13, 1, False), x_y_to_image(14, 1, False)],
                pb.DirType.W: [x_y_to_image(15, 1, False), x_y_to_image(16, 1, False)],
            },
            'others_at_sea': {
                pb.DirType.N: [x_y_to_image(1, 4), x_y_to_image(2, 4)],
                pb.DirType.E: [x_y_to_image(3, 4), x_y_to_image(4, 4)],
                pb.DirType.S: [x_y_to_image(5, 4), x_y_to_image(6, 4)],
                pb.DirType.W: [x_y_to_image(7, 4), x_y_to_image(8, 4)],

                pb.DirType.NW: [x_y_to_image(7, 4), x_y_to_image(8, 4)],
                pb.DirType.NE: [x_y_to_image(3, 4), x_y_to_image(4, 4)],
                pb.DirType.SW: [x_y_to_image(7, 4), x_y_to_image(8, 4)],
                pb.DirType.SE: [x_y_to_image(3, 4), x_y_to_image(4, 4)],

            },
        }

        super().__init__(self.frames['in_port'][pb.DirType.N][0], x, y, z)
        self.model = model

        self.is_using_port_img = False
        self.is_using_sea_img = False
        self.is_using_battle_img = False

        self.now_frame = 0
        self.frame_counter = 0
        self.frame_counter_max = c.FRAME_RATE // 2


    def on_click(self, event):
        print("Sprite was clicked!")
        # show menu in dialogs
        if self.model.role.is_in_battle():
            return

        if self.is_mine:
            return

        if self.role.is_dynamic_port_npc:
            return

        self.model.role.graphics.client.game.gui.options_dialog.show_role_menu(self.role)

    def change_to_next_frame(self):
        if self.now_frame == 0:
            self.now_frame = 1
        else:
            self.now_frame = 0

        if self.role.is_in_port():
            if self.role.is_man_in_port():
                img = self.frames['man_in_port'][self.role.dir][self.now_frame]
            elif self.role.is_woman_in_port():
                img = self.frames['woman_in_port'][self.role.dir][self.now_frame]
            else:
                img = self.frames['in_port'][self.role.dir][self.now_frame]
        elif self.role.is_at_sea():
            if self.is_mine:
                img = self.frames['at_sea'][self.role.dir][self.now_frame]
            else:
                img = self.frames['others_at_sea'][self.role.dir][self.now_frame]
        self.change_img(img)

    def update(self, time_diff):
        if not self.model.role:
            return

        super().update(time_diff)

        self.__update_img_based_on_location()
        self.__update_at_sea_frame()

    def __update_at_sea_frame(self):
        if self.role.is_at_sea():

            if self.frame_counter == self.frame_counter_max:
                self.frame_counter = 0
                self.now_frame += 1
                if self.now_frame == len(self.frames['at_sea'][pb.DirType.N]):
                    self.now_frame = 0

                if self.role.is_at_sea():
                    if self.is_mine:
                        self.change_img(self.frames['at_sea'][self.role.dir][self.now_frame])
                    else:
                        self.change_img(self.frames['others_at_sea'][self.role.dir][self.now_frame])
            else:
                self.frame_counter += 1


    def __update_img_based_on_location(self):
        if self.role.is_in_port() and not self.is_using_port_img:

            if self.role.is_man_in_port():
                self.change_img(self.frames['man_in_port'][self.role.dir][0])
            elif self.role.is_woman_in_port():
                self.change_img(self.frames['woman_in_port'][self.role.dir][0])
            else:
                self.change_img(self.frames['in_port'][self.role.dir][0])

            self.is_using_port_img = True
            self.is_using_sea_img = False
            self.is_using_battle_img = False

        elif self.role.is_at_sea() and not self.is_using_sea_img:
            # self.change_img(sAssetMgr.images['player']['ship_at_sea'])
            if self.is_mine:
                self.change_img(self.frames['at_sea'][self.role.dir][0])
            else:
                self.change_img(self.frames['others_at_sea'][self.role.dir][0])
            self.is_using_sea_img = True
            self.is_using_port_img = False
            self.is_using_battle_img = False

        elif self.role.is_in_battle() and not self.is_using_battle_img:
            self.change_img(sAssetMgr.images['player']['role_in_battle'])
            self.is_using_battle_img = True
            self.is_using_port_img = False
            self.is_using_sea_img = False



class HudLeft(SP):

    def __init__(self, model, image, x, y):
        super().__init__(image, x, y, z=3)

        self.model = model

    def update(self, time_diff):
        if not self.model.role:
            return

        # hide while in battle
        if self.model.role.is_in_battle():
            self.move_to(-500, 0)
        else:
            self.move_to(0, 0)

        new_image = self.img_src.copy()

        x = 10

        new_image.blit(Text('Century 16').image, (x, 18))
        new_image.blit(Text('Spring').image, (x, 142))

        if self.model.role.is_in_port():
            lv = self.model.role.get_lv()

            new_image.blit(Text(f'Lv \n  {lv}').image, (x, 240))

            ingots = Text(f'Gold Ingots \n  {self.model.role.money // 10000}').image
            coins = Text(  f'Gold Coins \n  {self.model.role.money % 10000}').image
            new_image.blit(ingots, (x, 280))
            new_image.blit(coins, (x, 320))

        elif self.model.role.is_at_sea():
            # show supplies
            role = self.model.role
            new_image.blit(Text(f"R/M/H \n  "
                                f"{role.ration}/{role.morale}/{role.health}").image, (x, 240))

            ship_mgr = self.model.role.ship_mgr

            food_water = Text(f"Food/Water \n  "
                              f"{ship_mgr.get_total_supply(pb.SupplyType.FOOD)}/"
                              f"{ship_mgr.get_total_supply(pb.SupplyType.WATER)}").image
            material_cannon = Text(f"Material/Cannon \n  "
                              f"{ship_mgr.get_total_supply(pb.SupplyType.MATERIAL)}/"
                              f"{ship_mgr.get_total_supply(pb.SupplyType.CANNON)}").image
            new_image.blit(food_water, (x, 280))
            new_image.blit(material_cannon, (x, 320))

        name = Text( f'{self.model.role.name}  {time_diff}').image
        new_image.blit(name, (x, 400))

        self.change_img(new_image)


class HudRight(SP):

    def __init__(self, model, image, x, y):
        super().__init__(image, x, y, z=3)
        self.model = model

    def update(self, time_diff):
        if not self.model.role:
            return

        # hide while in battle
        if self.model.role.is_in_battle():
            self.move_to(2000, 0)
        else:
            self.move_to(c.WINDOW_WIDTH - c.HUD_WIDTH, 0)

        new_image = self.img_src.copy()
        x = 10

        # in port
        if self.model.role.is_in_port():

            port = sObjectMgr.get_port(self.model.role.map_id)

            region = c.REGIONS[port.region_id] if port.region_id is not None else ''

            new_image.blit(Text(f'{port.name}').image, (x, 5))
            new_image.blit(Text(f'{region}').image, (x, 20))

            new_image.blit(Text(f'Economy \n  {port.economy}').image, (x, 120))
            new_image.blit(Text(f'Industry \n  {port.industry}').image, (x, 160))

        # at sea
        elif self.model.role.is_at_sea():
            new_image.blit(Text(f'At Sea').image, (x, 5))

            # auras
            for id, aura in enumerate(self.model.role.auras):
                aura = sObjectMgr.get_aura(aura)

                my_x = x + id * 30
                new_image.blit(Text(f'{aura.name[:3]}').image, (my_x, 20))

            start_y = 75
            d_y = 45

            speed = self.model.role.speed
            new_image.blit(Text(f'Speed \n  {speed/4} Knots').image, (x, start_y))
            new_image.blit(Text(f'Days \n  {self.model.role.days_at_sea}').image, (x, start_y + d_y * 1))

            season_mgr = self.model.season_mgr
            season = season_mgr.season
            wind_dir = season_mgr.wind_dir
            wind_speed = season_mgr.wind_speed
            current_dir = season_mgr.current_dir
            current_speed = season_mgr.current_speed

            new_image.blit(Text(f'Season \n  {c.INT_2_SEASON[season]}').image, (x, start_y + d_y * 2))

            # wind
            wind_angle = wind_dir * 45
            rotated_image = pygame.transform.rotate(
                sAssetMgr.images['huds']['direction'],
                (360 - wind_angle)
            )
            new_image.blit(rotated_image, (x + 20, 230))

            new_image.blit(Text(f'Wind \n  {wind_speed}').image, (x, start_y + d_y * 3))
            
            # current
            current_angle = current_dir * 45
            rotated_image = pygame.transform.rotate(
                sAssetMgr.images['huds']['direction'],
                (360 - current_angle)
            )
            new_image.blit(rotated_image, (x + 20, 275))
            
            
            new_image.blit(Text(f'Current \n  {current_speed}').image, (x, start_y + d_y * 4))


        else:
            pass

        self.change_img(new_image)


class Graphics:

    def __init__(self, client=None, model=None):
        self.font = pygame.font.Font(r"D:\data\code\python\project_mount_christ\data\fonts\siyuanheiti.ttf", FONT_SIZE)

        # client
        self.client = client

        # model
        self.model = model

        # imgs
        self.imgs = self.__load_images()

        # sprites
        self.sprites = pygame.sprite.Group()

        self.sp_background = BackGround(model, self.imgs['background'], 0, 0)
        self.sp_role = RoleSP(model, self.model.role, None, c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2, z=1.5)
        # self.sp_role_name = SP(self.font.render('name', True, YELLOW), c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2)

        self.sp_building_bg = None
        self.sp_hud_left = HudLeft(model, sAssetMgr.images['huds']['hud_left'], 0, 0)
        self.sp_hud_right = HudRight(model, sAssetMgr.images['huds']['hud_right'], c.WINDOW_WIDTH - c.HUD_WIDTH, 0)

        self.sprites.add(self.sp_background)
        self.sprites.add(self.sp_role)
        # self.sprites.add(self.sp_role_name)
        self.sprites.add(self.sp_hud_left)
        self.sprites.add(self.sp_hud_right)

        self.id_2_sp_role = {}
        self.id_2_sp_role_name = {}
        self.id_2_sp_say = {}

        # move marks in battle
        self.move_marks = []
        self.shoot_marks = []
        self.engage_marks = []

        # port npcs
        self.port_npcs = []
        self.dynamic_port_npcs = []
        self.dynamic_port_npc_update_timer = 0


    def clear_marks(self):
        self.move_marks = []
        self.shoot_marks = []
        self.engage_marks = []

    def __load_images(self):
        imgs = {}

        imgs['background'] = self.__load_image(r'D:\data\code\python\project_mount_christ\data\imgs\port.png')
        imgs['role'] = self.__load_image(r'D:\data\code\python\project_mount_christ\data\imgs\role.png')
        imgs['hud'] = self.__load_image(r'D:\data\code\python\project_mount_christ\data\imgs\hud.png')
        imgs['sea'] = self.__load_image(r'D:\data\code\python\project_mount_christ\data\imgs\sea.png')
        imgs['battle_ground'] = self.__load_image(r'D:\data\code\python\project_mount_christ\data\imgs\in_battle\battle.PNG')

        return imgs

    def __load_image(self, path_to_img, set_transparent=True):
        image = pygame.image.load(path_to_img).convert()

        if set_transparent:
            colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
            return image
        else:
            return image

    def move_port_bg(self, x, y):
        x, y = self.role_xy_in_port_2_xy_on_screen(x, y)
        self.sp_background.move_to_smoothly(x, y, given_time=0.2)

    def move_sea_bg(self, x, y):
        print('xx', x, y)

        # if out of range
        if abs(x - sMapMaker.x_tile) >= 12 or abs(y - sMapMaker.y_tile) >= 12:
            print("out of box! time to draw new map")

            # in edge cases, do not draw new map
            if y > (1080 - 40) or y < 40 or x > (2160 - 40) or x < 40:
                self.x_tile = x
                self.y_tile = y
                self.drawing_partial_map = False

            # make new sea image
            else:

                new_partial_sea_map = sMapMaker.make_partial_world_map(
                    x, y, sMapMaker.get_time_of_day().value
                )
                self.sp_background.change_img(new_partial_sea_map)

            # move img
            role = self.model.role

            prev_x, prev_y = self.role_xy_at_sea_2_xy_on_screen(role.last_x, role.last_y)
            self.sp_background.move_to(prev_x, prev_y)

            x, y = self.role_xy_at_sea_2_xy_on_screen(x, y)
            self.sp_background.move_to_smoothly(x, y, given_time=role.calc_move_timer())

        # else
        else:
            role = self.model.role
            x, y = self.role_xy_at_sea_2_xy_on_screen(x, y)
            self.sp_background.move_to_smoothly(x, y, given_time=role.calc_move_timer())

    def role_xy_in_port_2_xy_on_screen(self, x, y):
        x = -x * c.PIXELS_COVERED_EACH_MOVE + c.WINDOW_WIDTH // 2
        y = -y * c.PIXELS_COVERED_EACH_MOVE + c.WINDOW_HEIGHT // 2

        return x, y

    def role_xy_at_sea_2_xy_on_screen(self, x, y):

        x = -(x - sMapMaker.x_tile - 5) * c.PIXELS_COVERED_EACH_MOVE - \
            (c.PIXELS_COVERED_EACH_MOVE * c.PARTIAL_WORLD_MAP_TILES_IN_ONE_DIRECTION // 2)

        y = -(y - sMapMaker.y_tile + 3) * c.PIXELS_COVERED_EACH_MOVE - \
            (c.PIXELS_COVERED_EACH_MOVE * c.PARTIAL_WORLD_MAP_TILES_IN_ONE_DIRECTION // 2)
        return x, y

    def change_background_sp_to_sea(self, x=None, y=None):
        print('chaning bg')
        if not x or not y:

            self.sp_background.change_img(self.imgs['sea'])
        else:
            if sMapMaker.world_map_piddle is None:
                sMapMaker.set_world_piddle()
                sMapMaker.set_world_map_tiles()

            partial_sea_map = sMapMaker.make_partial_world_map(
                x, y,
                sMapMaker.get_time_of_day().value.lower())
            self.sp_background.change_img(partial_sea_map)

            x, y = self.role_xy_at_sea_2_xy_on_screen(x, y)
            self.sp_background.move_to(x, y)

        sAssetMgr.play_sea_music()

    def change_background_sp_to_port(self, port_id, x, y):

        port_piddle, port_map = sMapMaker.make_port_piddle_and_map(port_id, sMapMaker.get_time_of_day())
        self.sp_background.change_img(port_map)

        # so port img looks right after enter port
        self.sp_background.start_time = None
        x, y = self.role_xy_in_port_2_xy_on_screen(x, y)
        self.sp_background.move_to(x, y)

        # remove port npcs
        if sMapMaker.get_time_of_day() == c.TimeType.NIGHT:
            self.remove_port_npcs()
            self.remove_dynamic_port_npcs()
        else:
            port_id = self.model.role.map_id

            if not self.port_npcs:
                self.add_port_npcs(port_id)
            if not self.dynamic_port_npcs:
                self.add_dynamic_port_npcs(port_id)

    def add_sp_building_bg(self, building_name):
        # bg and figure
        building_bg_img = sAssetMgr.images['buildings']['building_bg']
        building_bg_img = pygame.transform.scale(building_bg_img, building_bg_img.get_rect().size)  # 800, 400

        building_bg_img.blit(sAssetMgr.images['buildings'][building_name], (5, 5))
        figure_image_width = sAssetMgr.images['buildings'][building_name].get_rect().width
        building_bg_img.blit(sAssetMgr.images['buildings']['building_chat'], (figure_image_width + 10, 5))

        # draw on layer 2
        self.sp_building_bg = SP(building_bg_img, c.HUD_WIDTH, 0, z=2)
        self.sprites.add(self.sp_building_bg)

    def remove_sp_building_bg(self):
        if self.sp_building_bg:
            self.sp_building_bg.kill()
            self.sp_building_bg = None

    def change_background_sp_to_battle_ground(self):
        self.sp_background.change_img(self.imgs['battle_ground'])
        self.sp_background.move_to(0, 0)

        self.get_options_dialog().pop_some_menus(10)

        sAssetMgr.play_battle_music()

    def add_sp_role(self, role):
        # x = (role.x - self.model.role.x) * c.PIXELS_COVERED_EACH_MOVE + c.WINDOW_WIDTH // 2
        # y = (role.y - self.model.role.y) * c.PIXELS_COVERED_EACH_MOVE + c.WINDOW_HEIGHT // 2

        x, y = role.get_x_y_between_roles(role, self.model.role)

        sp_role = RoleSP(self.model, role, self.imgs['role'], x, y, is_mine=False)

        if role.is_npc():
            role_name = ''
        else:
            role_name = role.name

        sp_role_name = SP(self.font.render(role_name, True, YELLOW), x, y - 10, z=1)

        self.sprites.add(sp_role)
        self.sprites.add(sp_role_name)

        self.id_2_sp_role[role.id] = sp_role
        self.id_2_sp_role_name[role.id] = sp_role_name

    def add_say_sp(self, role, text):
        if role.id in self.id_2_sp_say:
            self.id_2_sp_say[role.id].kill()

        x, y = role.get_x_y_between_roles(role, self.model.role)
        say_sp = SaySP(text, x, y - c.SAY_SP_Y_OFFSET)
        self.sprites.add(say_sp)

        self.id_2_sp_say[role.id] = say_sp

    def rm_sp_role(self, id):
        if id in self.id_2_sp_role:
            self.id_2_sp_role[id].kill()
            del self.id_2_sp_role[id]

        if id in self.id_2_sp_role_name:
            self.id_2_sp_role_name[id].kill()
            del self.id_2_sp_role_name[id]

    def get_sp_role(self, id):
        return self.id_2_sp_role[id]

    def move_sp_role(self, id, x, y, given_time):
        # self.id_2_sp_role[id].move_to(x, y)
        # self.id_2_sp_role_name[id].move_to(x, y)

        self.id_2_sp_role[id].move_to_smoothly(x, y, given_time)
        self.id_2_sp_role_name[id].move_to_smoothly(x, y, given_time)

        if id in self.id_2_sp_say:
            self.id_2_sp_say[id].move_to_smoothly(x, y - c.SAY_SP_Y_OFFSET, given_time)

    def get_options_dialog(self):
        return self.client.game.gui.options_dialog

    def process_event(self, event):
        if not self.model.role:
            return

        # when mouse clicked, check if any sprite clicked
        if event.type == pygame.MOUSEBUTTONDOWN:
            for sprite in self.sprites:  # Assuming all_sprites is a Group of your sprites
                if sprite.rect.collidepoint(event.pos):
                    sprite.on_click(event)

        # when enter pressed, turn on chat cursor
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if not self.client.game.gui.chat_dialog.command_entry.is_focused:
                    self.client.game.gui.chat_dialog.command_entry.focus()
                else:
                    text = self.client.game.gui.chat_dialog.command_entry.get_text()
                    if not text:
                        self.client.game.gui.chat_dialog.command_entry.unfocus()

        # don't check keys if chat cursor is on
        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            if self.client.game.gui.chat_dialog.command_entry.is_focused:
                return

        # key down
        if event.type == pygame.KEYDOWN:
            # movements
            if event.key == pygame.K_d:
                # move east
                # self.client.send(pb.StartMoving(dir_type=pb.DirType.E))
                self.model.role.start_moving(pb.DirType.E)

            elif event.key == pygame.K_a:
                # move west
                # self.client.send(pb.StartMoving(dir_type=pb.DirType.W))
                self.model.role.start_moving(pb.DirType.W)
            elif event.key == pygame.K_w:
                # move north
                # self.client.send(pb.StartMoving(dir_type=pb.DirType.N))
                self.model.role.start_moving(pb.DirType.N)
            elif event.key == pygame.K_s:
                # move south
                # self.client.send(pb.StartMoving(dir_type=pb.DirType.S))
                self.model.role.start_moving(pb.DirType.S)

            # other 4 dirs at sea
            if event.key == pygame.K_q:
                self.model.role.start_moving(pb.DirType.NW)
            if event.key == pygame.K_e:
                self.model.role.start_moving(pb.DirType.NE)
            if event.key == pygame.K_z:
                self.model.role.start_moving(pb.DirType.SW)
            if event.key == pygame.K_x:
                self.model.role.start_moving(pb.DirType.SE)

            # test key
            if event.key == pygame.K_t:
                self.model.role.is_moving = False
                self.sp_background.start_time = None
                self.client.send(FightRole(role_id=2))

            if event.key == pygame.K_y:
                self.model.role.is_moving = False
                self.sp_background.start_time = None
                self.client.send(FightNpc(npc_id=2000000001))

            if event.key == pygame.K_p:

                if self.model.role.is_in_port():
                    self.client.send(Sail())
                elif self.model.role.is_at_sea():
                    self.get_options_dialog().enter_port()
                elif self.model.role.is_in_battle():
                    self.get_options_dialog().escape_battle()

            if event.key == pygame.K_l:
                if self.model.role.is_in_battle():
                    self.get_options_dialog().all_ships_attack()

            if event.key == pygame.K_f:
                if self.model.role.is_in_building:
                    self.get_options_dialog().exit_building()
                else:
                    self.get_options_dialog().enter_building()

        # key up
        elif event.type == pygame.KEYUP:
            if event.key in [pygame.K_d, pygame.K_a, pygame.K_w, pygame.K_s]:
                if self.model.role.is_in_port():
                    self.model.role.stop_moving()

        # mouse clicks
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not self.model.role:
                return

            if not self.model.role.is_in_battle():
                return

            # check move mark clicks
            for move_mark in self.model.role.graphics.move_marks:
                if move_mark.rect.collidepoint(event.pos):
                    move_mark.on_click(self.client)

            # check shoot mark clicks
            for shoot_mark in self.model.role.graphics.shoot_marks:
                if shoot_mark.rect.collidepoint(event.pos):
                    shoot_mark.on_click(self.client)
                    self.model.role.has_attacked = True
                    self.model.role.graphics.clear_marks()

            # check engage mark clicks
            for engage_mark in self.model.role.graphics.engage_marks:
                if engage_mark.rect.collidepoint(event.pos):
                    engage_mark.on_click(self.client)
                    self.model.role.has_attacked = True
                    self.model.role.graphics.clear_marks()

            # hold if role sprite clicked
            if self.model.role.graphics.sp_role.rect.collidepoint(event.pos):

                self.client.send(pb.FlagShipAttack(attack_method_type=pb.AttackMethodType.HOLD))
                self.model.role.has_attacked = True
                self.model.role.graphics.clear_marks()

    def update(self, time_diff):
        self.sprites.update(time_diff)

        self.__update_dynamic_port_npcs(time_diff)

    def __update_dynamic_port_npcs(self, time_diff):
        self.dynamic_port_npc_update_timer -= time_diff
        if self.dynamic_port_npc_update_timer <= 0:
            self.dynamic_port_npc_update_timer = c.DYNAMIC_PORT_NPC_UPDATE_TIMER
            for dpn in self.dynamic_port_npcs:
                # randchoice
                rand_dir = random.choice([pb.DirType.N, pb.DirType.E, pb.DirType.S, pb.DirType.W])
                dpn.is_moving = True
                dpn.dir = rand_dir
                dpn.move_timer = 0
                dpn.speed = c.PORT_SPEED

    def draw(self, window_surface):
        if not self.client.packet_handler.is_in_game:
            # draw login_bg
            scaled_login_bg =  pygame.transform.scale(
                sAssetMgr.images['buildings']['login_bg'],
                (c.WINDOW_WIDTH, c.WINDOW_HEIGHT)
            )
            window_surface.blit(scaled_login_bg, (0, 0))

            return

        # draw 1st background
        window_surface.blit(sAssetMgr.images['buildings']['building_bg'], (110, 0))

        # draw sprites in layer order
        layers = [0, 1, 1.5, 2, 3]
        for layer in layers:
            for sprite in self.sprites.sprites():
                if sprite.z == layer:
                    window_surface.blit(sprite.image, sprite.rect)

    def show_damage(self, damage, x, y, color=c.YELLOW):
        shoot_damage_number = ShootDamageNumber(damage, x, y, color)
        self.sprites.add(shoot_damage_number)


    def show_cannon(self, x1, y1, x2, y2):
        cannon = CannonBall(x1, y1, x2, y2)
        self.sprites.add(cannon)

    def show_engage_sign(self, x, y):
        frames = [
            sAssetMgr.images['in_battle']['engage_sign_1'],
            sAssetMgr.images['in_battle']['engage_sign']
        ]
        time_between_frames = 0.1
        anim = Animation(frames, time_between_frames, x, y, loop_cnt=2)
        self.sprites.add(anim)

    def show_explosion(self, x, y):
        image = sAssetMgr.images['in_battle']['explosion']
        frames = SpriteSheet(image, 4, 4).get_frames()
        time_between_frames = 0.03
        anim = Animation(frames, time_between_frames, x, y)
        self.sprites.add(anim)

    def remove_port_npcs(self):
        for npc in self.port_npcs:
            npc.animation.kill()
        self.port_npcs = []

    def get_port_npcs(self):
        return self.port_npcs

    def add_port_npcs(self, port_id):
        # dog
        dog = PortNpc()

        dog.frames = [
            x_y_to_image(29, 1, is_ship=False),
            x_y_to_image(30, 1, is_ship=False)
        ]

        building_x, building_y = sObjectMgr.get_building_xy_in_port(
            building_id=c.Building.BAR.value,
            port_id=self.model.role.map_id
        )

        dog.x = building_x + 1
        dog.y = building_y + 1

        x, y = dog.get_xy_relative_to_role(self.model.role)


        dog.animation = Animation(dog.frames, 0.5, x, y, 1000)
        self.sprites.add(dog.animation)
        self.port_npcs.append(dog)

        # oldman
        old_man = PortNpc()
        old_man.frames = [
            x_y_to_image(27, 1, is_ship=False),
            x_y_to_image(28, 1, is_ship=False)
        ]

        building_x, building_y = sObjectMgr.get_building_xy_in_port(
            building_id=c.Building.INN.value,
            port_id=self.model.role.map_id
        )
        old_man.x = building_x + 1
        old_man.y = building_y + 1

        x, y = old_man.get_xy_relative_to_role(self.model.role)


        old_man.animation = Animation(old_man.frames, 0.5, x, y, 1000)
        self.sprites.add(old_man.animation)
        self.port_npcs.append(old_man)

        # market_guy
        market_guy = PortNpc()
        market_guy.frames = [
            x_y_to_image(25, 1, is_ship=False),
            x_y_to_image(26, 1, is_ship=False)
        ]

        building_x, building_y = sObjectMgr.get_building_xy_in_port(
            building_id=c.Building.MARKET.value,
            port_id=self.model.role.map_id
        )

        market_guy.x = building_x + 1
        market_guy.y = building_y + 1

        x, y = market_guy.get_xy_relative_to_role(self.model.role)

        market_guy.animation = Animation(market_guy.frames, 0.5, x, y, 1000)
        self.sprites.add(market_guy.animation)
        self.port_npcs.append(market_guy)

    def add_dynamic_port_npcs(self, port_id):
        self.__add_dynamic_port_npc(c.Building.MARKET.value, 2000000101, self.model.role.map_id)
        self.__add_dynamic_port_npc(c.Building.INN.value, 2000000102, self.model.role.map_id)
        self.__add_dynamic_port_npc(c.Building.BAR.value, 2000000103, self.model.role.map_id)
        self.__add_dynamic_port_npc(c.Building.BAR.value, 2000000104, self.model.role.map_id)

    def __add_dynamic_port_npc(self, building_id, role_id, port_id):
        building_x, building_y = sObjectMgr.get_building_xy_in_port(
            building_id=building_id,
            port_id=port_id
        )

        role = Role(
            id=role_id,
            name='',
            map_id=port_id,
            x=building_x,
            y=building_y,
            dir=pb.DirType.N,
            graphics=self,
            is_dynamic_port_npc=True,
        )

        self.add_sp_role(role)
        self.model.add_role(role)
        self.dynamic_port_npcs.append(role)

    def remove_dynamic_port_npcs(self):
        for role in self.dynamic_port_npcs:
            self.rm_sp_role(role.id)
            self.model.remove_role(role.id)

        self.dynamic_port_npcs = []
