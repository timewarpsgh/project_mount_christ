import pygame
import os
import sys
from login_pb2 import *

sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared')

import constants as c

from asset_mgr import sAssetMgr

FONT_SIZE = 16
YELLOW = (255, 255, 0)
RED = (255, 0, 0)


class Text():
    def __init__(self, text, color=c.BLACK):
        self.image = sAssetMgr.font.render(text, True, color)
        self.rect = self.image.get_rect()


# class BattleStates(pygame.sprite.Sprite):
#     def __init__(self):
#         pygame.sprite.Sprite.__init__(self)
#
#         self.image = pygame.Surface((c.WINDOW_WIDTH, c.WINDOW_HIGHT)).convert_alpha()
#         self.image.fill(c.TRANS_BLANK)
#
#         self.rect = self.image.get_rect()
#         self.rect.x = 0
#         self.rect.y = 0
#
#     def update(self):
#         self._change_state()
#         self._draw()
#
#     def _change_state(self):
#         self.image.fill(c.TRANS_BLANK)
#         self.__draw_my_ships_states()
#
#     def __draw_my_ships_states(self):
#         # my timer
#         timer_text = Text('50', c.YELLOW)
#         timer_text.rect.x = 20
#         timer_text.rect.y = 5
#         self.image.blit(timer_text.image, timer_text.rect)
#
#     def _draw(self):
#         self.game.screen_surface.blit(self.image, self.rect)


class SP(pygame.sprite.Sprite):

    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.image = image
        self.rect = image.get_rect().move(x, y)

    def change_img(self, img):
        self.image = img

    def move_to(self, x, y):
        self.rect = self.image.get_rect().move(x, y)


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
        self.sp_role = SP(self.imgs['role'], 300, 150)
        self.sp_role_name = SP(self.font.render('name', True, YELLOW), 300, 150)
        self.sp_hud = SP(self.imgs['hud'], 0, 0)

        self.sprites.add(self.sp_background)
        self.sprites.add(self.sp_role)
        self.sprites.add(self.sp_role_name)
        self.sprites.add(self.sp_hud)


        self.id_2_sp_role = {}
        self.id_2_sp_role_name = {}

    def __load_images(self):
        imgs = {}

        imgs['background'] = self.__load_image(r'D:\data\code\python\project_mount_christ\data\imgs\port.png')
        imgs['role'] = self.__load_image(r'D:\data\code\python\project_mount_christ\data\imgs\role.png')
        imgs['hud'] = self.__load_image(r'D:\data\code\python\project_mount_christ\data\imgs\hud.png')
        imgs['sea'] = self.__load_image(r'D:\data\code\python\project_mount_christ\data\imgs\sea.png')
        imgs['battle_ground'] = self.__load_image(r'D:\data\code\python\project_mount_christ\data\imgs\battle_ground.png')

        return imgs

    def __load_image(self, path_to_img, set_transparent=True):
        image = pygame.image.load(path_to_img).convert()

        if set_transparent:
            colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
            return image
        else:
            return image

    def change_background_sp_to_sea(self):
        print('chaning bg')
        self.sp_background.change_img(self.imgs['sea'])

    def change_background_sp_to_port(self):
        self.sp_background.change_img(self.imgs['background'])

    def change_background_sp_to_battle_ground(self):
        self.sp_background.change_img(self.imgs['battle_ground'])

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

    def update(self, time_diff):
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
                timer_text.rect.x = 100
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
                    battle_ground_img.blit(ship_in_battle_img, (80, 50 + 40 * id))

                # draw enemy ships
                enemy_role = self.model.get_enemy_role()

                enemy_ships = enemy_role.ship_mgr.id_2_ship.values()
                for id, ship in enumerate(enemy_ships):
                    ship_in_battle_img = sAssetMgr.images['ship_in_battle']['up']
                    battle_ground_img.blit(ship_in_battle_img, (500, 50 + 40 * id))

                # self.sp_background.change_img(new_img)
                self.sp_background.change_img(battle_ground_img)
    def draw(self, window_surface):
        if not self.client.packet_handler.is_in_game:
            return

        # draw objs
        self.sprites.draw(window_surface)
