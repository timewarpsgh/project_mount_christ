import pygame
import os
import sys
from login_pb2 import *
import login_pb2 as pb

sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared')

import constants as c

from asset_mgr import sAssetMgr
from map_maker import sMapMaker
from object_mgr import sObjectMgr

FONT_SIZE = 16
YELLOW = (255, 255, 0)
RED = (255, 0, 0)


class Text():
    def __init__(self, text, color=c.BLACK):
        self.image = sAssetMgr.font.render(text, True, color)
        self.rect = self.image.get_rect()


class SP(pygame.sprite.Sprite):

    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.image = image
        self.rect = image.get_rect().move(x, y)

    def change_img(self, img):
        self.image = img

    def move_to(self, x, y):
        self.rect = self.image.get_rect().move(x, y)


class ShootDamageNumber(SP):
    def __init__(self, number, x, y, color=c.YELLOW):
        image = sAssetMgr.font.render(str(number), True, color)
        super().__init__(image, x, y)

        self.frames = [None] * 60
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

    def update(self):
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
    def __init__(self, x, y, d_x, d_y):

        super().__init__(sAssetMgr.images['in_battle']['cannon'], x, y)

        self.d_x = d_x
        self.d_y = d_y

        self.steps_to_change = 60
        self.step_index = 0

        self.unit_x_change = int(self.d_x / self.steps_to_change)
        self.unit_y_change = int(self.d_y / self.steps_to_change)

    def update(self):
        self.rect.x += self.unit_x_change
        self.rect.y += self.unit_y_change
        self.step_index += 1
        if self.step_index == self.steps_to_change:
            self.kill()


class RoleSP(SP):

    def __init__(self, model, image, x, y):
        super().__init__(image, x, y)
        self.model = model

        self.is_using_port_img = False
        self.is_using_sea_img = False
        self.is_using_battle_img = False

        self.frames = {
            'at_sea' : {
                # dir type
                pb.DirType.N : [self.__ship_x_y_ship_image(1, 2), self.__ship_x_y_ship_image(2, 2)],
                pb.DirType.E : [self.__ship_x_y_ship_image(3, 2), self.__ship_x_y_ship_image(4, 2)],
                pb.DirType.S : [self.__ship_x_y_ship_image(5, 2), self.__ship_x_y_ship_image(6, 2)],
                pb.DirType.W: [self.__ship_x_y_ship_image(7, 2), self.__ship_x_y_ship_image(8, 2)],
            },
            'in_port': {
                'n': [],

            }
        }

        self.now_frame = 0
        self.frame_counter = 0
        self.frame_counter_max = 30


    def update(self):
        if not self.model.role:
            return

        self.__update_img_based_on_location()
        self.__update_frame()

    def __update_frame(self):
        if self.frame_counter == self.frame_counter_max:
            self.frame_counter = 0
            self.now_frame += 1
            if self.now_frame == len(self.frames['at_sea'][pb.DirType.N]):
                self.now_frame = 0

            if self.model.role.is_at_sea():
                self.change_img(self.frames['at_sea'][self.model.role.dir][self.now_frame])

        else:
            self.frame_counter += 1

    def __update_img_based_on_location(self):
        if self.model.role.is_in_port() and not self.is_using_port_img:
            self.change_img(sAssetMgr.images['player']['person_in_port'])
            self.is_using_port_img = True
            self.is_using_sea_img = False
            self.is_using_battle_img = False

        elif self.model.role.is_at_sea() and not self.is_using_sea_img:
            # self.change_img(sAssetMgr.images['player']['ship_at_sea'])

            self.change_img(self.__ship_x_y_ship_image(3, 2))
            self.is_using_sea_img = True
            self.is_using_port_img = False
            self.is_using_battle_img = False

        elif self.model.role.is_in_battle() and not self.is_using_battle_img:
            self.change_img(sAssetMgr.images['player']['role_in_battle'])
            self.is_using_battle_img = True
            self.is_using_port_img = False
            self.is_using_port_img = False

    def __ship_x_y_ship_image(self, x, y):
        ship_tile_set_img = sAssetMgr.images['player']['ship-tileset']
        tile_size = c.SHIP_SIZE_IN_PIXEL
        # make a [transparent] pygame surface
        ship_surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
        x_coord = -tile_size * (x - 1)
        y_coord = -tile_size * (y - 1)
        rect = pygame.Rect(x_coord, y_coord, tile_size, tile_size)
        ship_surface.blit(ship_tile_set_img, rect)

        return ship_surface


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

        self.sp_background = SP(self.imgs['background'], 0, 0)
        self.sp_role = RoleSP(model, sAssetMgr.images['player']['person_in_port'], c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2)
        # self.sp_role_name = SP(self.font.render('name', True, YELLOW), c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2)
        self.sp_hud_left = SP(sAssetMgr.images['huds']['hud_left'], 0, 0)
        self.sp_hud_right = SP(sAssetMgr.images['huds']['hud_right'], c.WINDOW_WIDTH - c.HUD_WIDTH, 0)

        self.sprites.add(self.sp_background)
        self.sprites.add(self.sp_role)
        # self.sprites.add(self.sp_role_name)
        self.sprites.add(self.sp_hud_left)
        self.sprites.add(self.sp_hud_right)


        self.id_2_sp_role = {}
        self.id_2_sp_role_name = {}

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
        self.sp_background.move_to(x, y)

    def move_sea_bg(self, x, y):
        # if out of range
        if abs(x - sMapMaker.x_tile) >= 12 or abs(y - sMapMaker.y_tile) >= 12:
            print("out of box! time to draw new map")

            # edge case
            tile_size = c.PIXELS_COVERED_EACH_MOVE
            x_in_pixels = x * tile_size
            y_in_pixels = y * tile_size

            if y_in_pixels > c.WORLD_MAP_MAX_Y_TO_DRAW_NEW_PARTIAL_WORLD_MAP or \
                    y_in_pixels < c.WORLD_MAP_MIN_Y_TO_DRAW_NEW_PARTIAL_WORLD_MAP:
                return

            if x_in_pixels > c.WORLD_MAP_MAX_X_TO_DRAW_NEW_PARTIAL_WORLD_MAP or \
                    x_in_pixels < c.WORLD_MAP_MIN_X_TO_DRAW_NEW_PARTIAL_WORLD_MAP:
                return

            # make new sea image
            new_partial_sea_map = sMapMaker.make_partial_world_map(x, y)
            self.sp_background.change_img(new_partial_sea_map)

            # move img
            x, y = self.role_xy_at_sea_2_xy_on_screen(x, y)
            self.sp_background.move_to(x, y)

        # else
        else:
            x, y = self.role_xy_at_sea_2_xy_on_screen(x, y)
            self.sp_background.move_to(x, y)

    def role_xy_in_port_2_xy_on_screen(self, x, y):
        x = -x * c.PIXELS_COVERED_EACH_MOVE + c.WINDOW_WIDTH // 2
        y = -y * c.PIXELS_COVERED_EACH_MOVE + c.WINDOW_HEIGHT // 2

        return x, y

    def role_xy_at_sea_2_xy_on_screen(self, x, y):
        x = -(x - sMapMaker.x_tile - 3) * c.PIXELS_COVERED_EACH_MOVE - \
            (c.PIXELS_COVERED_EACH_MOVE * c.PARTIAL_WORLD_MAP_TILES_IN_ONE_DIRECTION // 2)

        y = -(y - sMapMaker.y_tile + 4) * c.PIXELS_COVERED_EACH_MOVE - \
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

            partial_sea_map = sMapMaker.make_partial_world_map(x, y, save_img=True)
            self.sp_background.change_img(partial_sea_map)

            x, y = self.role_xy_at_sea_2_xy_on_screen(x, y)
            self.sp_background.move_to(x, y)


    def change_background_sp_to_port(self, port_id, x, y):

        port_piddle, port_map = sMapMaker.make_port_piddle_and_map(port_id, save_img=True)

        self.sp_background.change_img(port_map)

        x, y = self.role_xy_in_port_2_xy_on_screen(x, y)
        self.sp_background.move_to(x, y)

    def change_background_sp_to_building(self, building_name):
        # bg and figure
        building_bg_img = sAssetMgr.images['buildings']['building_bg']
        building_bg_img = pygame.transform.scale(building_bg_img, building_bg_img.get_rect().size)  # 800, 400

        building_bg_img.blit(sAssetMgr.images['buildings'][building_name], (5, 5))
        figure_image_width = sAssetMgr.images['buildings'][building_name].get_rect().width
        building_bg_img.blit(sAssetMgr.images['buildings']['building_chat'], (figure_image_width + 10, 5))

        self.sp_background.change_img(building_bg_img)
        self.sp_background.move_to(c.HUD_WIDTH, 0)

    def change_background_sp_to_battle_ground(self):
        self.sp_background.change_img(self.imgs['battle_ground'])
        self.sp_background.move_to(0, 0)

    def add_sp_role(self, role):
        sp_role = SP(self.imgs['role'], role.x, role.y)
        sp_role_name = SP(self.font.render(role.name, True, YELLOW), role.x, role.y)

        self.sprites.add(sp_role)
        self.sprites.add(sp_role_name)

        self.id_2_sp_role[role.id] = sp_role
        self.id_2_sp_role_name[role.id] = sp_role_name

    def rm_sp_role(self, id):
        self.id_2_sp_role[id].kill()
        del self.id_2_sp_role[id]
        self.id_2_sp_role_name[id].kill()
        del self.id_2_sp_role_name[id]

    def move_sp_role(self, id, x, y):
        print(self.id_2_sp_role)
        print(id)

        self.id_2_sp_role[id].move_to(x, y)
        self.id_2_sp_role_name[id].move_to(x, y)

    def process_event(self, event):
        if event.type == pygame.KEYDOWN:
            # movements
            if event.key == pygame.K_d:
                # move east
                move = Move()
                move.dir_type = DirType.E
                self.client.send(move)

            elif event.key == pygame.K_a:
                # move west
                move = Move()
                move.dir_type = DirType.W
                self.client.send(move)

            elif event.key == pygame.K_w:
                # move north
                move = Move()
                move.dir_type = DirType.N
                self.client.send(move)

            elif event.key == pygame.K_s:
                # move south
                move = Move()
                move.dir_type = DirType.S
                self.client.send(move)

            # test key
            elif event.key == pygame.K_t:
                self.client.send(FightRole(role_id=2))

            elif event.key == pygame.K_y:
                self.client.send(FightNpc(npc_id=1))

    def update(self, time_diff):
        # update sprites group
        self.sprites.update()

        if self.model.role:
            if not self.model.role.battle_timer:
                return

            if self.model.role.battle_timer > 0:
                self.model.role.battle_timer -= time_diff

                # update and draw battle timer
                if self.model.role.is_battle_timer_mine:
                    text = 'your turn'
                else:
                    text = 'enemy turn'

                timer_text = Text(f'{text} {int(self.model.role.battle_timer)}', c.YELLOW)
                timer_text.rect.x = 300
                timer_text.rect.y = 50

                battle_ground_img = self.imgs['battle_ground']
                # new img now
                width, height = battle_ground_img.get_rect().size

                battle_ground_img = pygame.transform.scale(battle_ground_img, (width, height))  # 800, 400

                battle_ground_img.blit(timer_text.image, timer_text.rect)

                # draw my ships
                my_ships = self.model.role.ship_mgr.id_2_ship.values()
                for id, ship in enumerate(my_ships):
                    ship_in_battle_img = sAssetMgr.images['ship_in_battle']['up']


                    battle_ground_img.blit(ship_in_battle_img, (ship.x, ship.y))

                # draw enemy ships

                enemy_role = self.model.get_enemy_role()

                if not enemy_role:
                    enemy_npc = self.model.get_npc_by_id(self.model.role.battle_npc_id)
                    if not enemy_npc:
                        return

                    enemy_ships = enemy_npc.ship_mgr.id_2_ship.values()
                else:

                    enemy_ships = enemy_role.ship_mgr.id_2_ship.values()

                for id, ship in enumerate(enemy_ships):
                    ship_in_battle_img = sAssetMgr.images['ship_in_battle']['up']
                    battle_ground_img.blit(ship_in_battle_img, (ship.x, ship.y))

                # self.sp_background.change_img(new_img)
                self.sp_background.change_img(battle_ground_img)

    def draw(self, window_surface):
        if not self.client.packet_handler.is_in_game:
            return

        # draw objs
        self.sprites.draw(window_surface)

    def show_damage(self, damage, x, y):
        shoot_damage_number = ShootDamageNumber(damage, x, y)
        self.sprites.add(shoot_damage_number)


    def show_cannon(self, x, y, d_x, d_y):
        cannon = CannonBall(x, y, d_x, d_y)
        self.sprites.add(cannon)