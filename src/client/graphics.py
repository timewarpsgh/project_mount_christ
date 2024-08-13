import pygame
import os
import sys
from login_pb2 import *

sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')


FONT_SIZE = 16
YELLOW = (255, 255, 0)
RED = (255, 0, 0)


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


    def update(self, time_delta):
        pass

    def draw(self, window_surface):
        if not self.client.packet_handler.is_in_game:
            return

        # draw objs
        self.sprites.draw(window_surface)
