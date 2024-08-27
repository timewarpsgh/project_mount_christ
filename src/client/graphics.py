import pygame
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
        self.img_src = image

        # for move_to_smoothly
        self.start_time = None
        self.target_position = None
        self.duration = None

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

        # only move if 4 pixels have changed
        pixcels_to_move = 1
        if abs(position[0] - self.rect.x) >= pixcels_to_move or \
                abs(position[1] - self.rect.y) >= pixcels_to_move:
            self.rect.x = position[0]
            self.rect.y = position[1]
            self.image.get_rect().move(self.rect.x, self.rect.y)

    def change_img(self, img):
        self.image = img

    def move_to(self, x, y):
        self.rect = self.image.get_rect().move(x, y)

    def move_to_smoothly(self, x, y, given_time):
        self.start_time = pygame.time.get_ticks() / 1000.0
        self.start_position = (self.rect.x, self.rect.y)
        self.target_position = (x, y)
        self.duration = given_time


def lerp(a, b, t):
    """Linear interpolation between two points."""
    return a + (b - a) * t


class BackGround(SP):
    def __init__(self, image, x, y):
        super().__init__(image, x, y)


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

    def update(self, time_diff):
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

    def update(self, time_diff):
        self.rect.x += self.unit_x_change
        self.rect.y += self.unit_y_change
        self.step_index += 1
        if self.step_index == self.steps_to_change:
            self.kill()


class RoleSP(SP):

    def __init__(self, model, role, image, x, y, is_mine=True):
        self.is_mine = is_mine
        self.role = role
        self.frames = {
            'at_sea' : {
                pb.DirType.N : [self.__x_y_to_image(1, 2), self.__x_y_to_image(2, 2)],
                pb.DirType.E : [self.__x_y_to_image(3, 2), self.__x_y_to_image(4, 2)],
                pb.DirType.S : [self.__x_y_to_image(5, 2), self.__x_y_to_image(6, 2)],
                pb.DirType.W : [self.__x_y_to_image(7, 2), self.__x_y_to_image(8, 2)],

                pb.DirType.NW: [self.__x_y_to_image(7, 2), self.__x_y_to_image(8, 2)],
                pb.DirType.NE: [self.__x_y_to_image(3, 2), self.__x_y_to_image(4, 2)],
                pb.DirType.SW: [self.__x_y_to_image(7, 2), self.__x_y_to_image(8, 2)],
                pb.DirType.SE: [self.__x_y_to_image(3, 2), self.__x_y_to_image(4, 2)],

            },
            'in_port': {
                pb.DirType.N : [self.__x_y_to_image(1, 1, False), self.__x_y_to_image(2, 1, False)],
                pb.DirType.E : [self.__x_y_to_image(3, 1, False), self.__x_y_to_image(4, 1, False)],
                pb.DirType.S : [self.__x_y_to_image(5, 1, False), self.__x_y_to_image(6, 1, False)],
                pb.DirType.W : [self.__x_y_to_image(7, 1, False), self.__x_y_to_image(8, 1, False)],
            }
        }

        super().__init__(self.frames['in_port'][pb.DirType.N][0], x, y)
        self.model = model

        self.is_using_port_img = False
        self.is_using_sea_img = False
        self.is_using_battle_img = False

        self.now_frame = 0
        self.frame_counter = 0
        self.frame_counter_max = c.FRAME_RATE // 2


    def change_to_next_frame(self):
        if self.now_frame == 0:
            self.now_frame = 1
        else:
            self.now_frame = 0

        if self.role.is_in_port():
            img = self.frames['in_port'][self.role.dir][self.now_frame]
        elif self.role.is_at_sea():
            img = self.frames['at_sea'][self.role.dir][self.now_frame]

        print(f'{self.role.id} changed to next frame, now frame is {self.now_frame} ')
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
                    self.change_img(self.frames['at_sea'][self.role.dir][self.now_frame])

            else:
                self.frame_counter += 1

    def __update_img_based_on_location(self):
        if self.role.is_in_port() and not self.is_using_port_img:
            self.change_img(self.frames['in_port'][self.role.dir][0])
            self.is_using_port_img = True
            self.is_using_sea_img = False
            self.is_using_battle_img = False

        elif self.role.is_at_sea() and not self.is_using_sea_img:
            # self.change_img(sAssetMgr.images['player']['ship_at_sea'])

            self.change_img(self.frames['at_sea'][self.role.dir][0])
            self.is_using_sea_img = True
            self.is_using_port_img = False
            self.is_using_battle_img = False

        elif self.role.is_in_battle() and not self.is_using_battle_img:
            self.change_img(sAssetMgr.images['player']['role_in_battle'])
            self.is_using_battle_img = True
            self.is_using_port_img = False
            self.is_using_sea_img = False

    def __x_y_to_image(self, x, y, is_ship=True):
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

class HudLeft(SP):

    def __init__(self, model, image, x, y):
        super().__init__(image, x, y)

        self.model = model

    def update(self, time_diff):
        if not self.model.role:
            return

        new_image = self.img_src.copy()

        x = 10

        new_image.blit(Text('Century 16').image, (x, 18))
        new_image.blit(Text('Spring').image, (x, 142))

        new_image.blit(Text('Lv \n  1').image, (x, 240))

        ingots = Text(f'Gold Ingots \n  {self.model.role.money // 10000}').image
        coins = Text(  f'Gold Coins \n  {self.model.role.money % 10000}').image
        new_image.blit(ingots, (x, 280))
        new_image.blit(coins, (x, 320))


        self.change_img(new_image)


class HudRight(SP):

    def __init__(self, model, image, x, y):
        super().__init__(image, x, y)
        self.model = model

    def update(self, time_diff):
        if not self.model.role:
            return

        new_image = self.img_src.copy()
        x = 10
        if self.model.role.is_in_port():

            port = sObjectMgr.get_port(self.model.role.map_id)
            region = c.REGIONS[port.region_id]

            new_image.blit(Text(f'{port.name}').image, (x, 5))
            new_image.blit(Text(f'{region}').image, (x, 20))

            new_image.blit(Text(f'Economy \n  {port.economy}').image, (x, 120))
            new_image.blit(Text(f'Industry \n  {port.industry}').image, (x, 160))

        elif self.model.role.is_at_sea():
            new_image.blit(Text(f'At Sea').image, (x, 5))
            new_image.blit(Text(f'Speed \n  10 Knots').image, (x, 120))
            new_image.blit(Text(f'Days spent \n  8').image, (x, 160))
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

        self.sp_background = BackGround(self.imgs['background'], 0, 0)
        self.sp_role = RoleSP(model, self.model.role, None, c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2)
        # self.sp_role_name = SP(self.font.render('name', True, YELLOW), c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2)
        self.sp_hud_left = HudLeft(model, sAssetMgr.images['huds']['hud_left'], 0, 0)
        self.sp_hud_right = HudRight(model, sAssetMgr.images['huds']['hud_right'], c.WINDOW_WIDTH - c.HUD_WIDTH, 0)

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
        self.sp_background.move_to_smoothly(x, y, given_time=0.2)

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

            partial_sea_map = sMapMaker.make_partial_world_map(x, y)
            self.sp_background.change_img(partial_sea_map)

            x, y = self.role_xy_at_sea_2_xy_on_screen(x, y)
            self.sp_background.move_to(x, y)


    def change_background_sp_to_port(self, port_id, x, y):

        port_piddle, port_map = sMapMaker.make_port_piddle_and_map(port_id)

        self.sp_background.change_img(port_map)

        # so port img looks right after enter port
        self.sp_background.start_time = None
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
        x = (role.x - self.model.role.x) * c.PIXELS_COVERED_EACH_MOVE + c.WINDOW_WIDTH // 2
        y = (role.y - self.model.role.y) * c.PIXELS_COVERED_EACH_MOVE + c.WINDOW_HEIGHT // 2
        sp_role = RoleSP(self.model, role, self.imgs['role'], x, y, is_mine=False)
        sp_role_name = SP(self.font.render(role.name, True, YELLOW), x, y)

        self.sprites.add(sp_role)
        self.sprites.add(sp_role_name)

        self.id_2_sp_role[role.id] = sp_role
        self.id_2_sp_role_name[role.id] = sp_role_name

    def rm_sp_role(self, id):
        self.id_2_sp_role[id].kill()
        del self.id_2_sp_role[id]
        self.id_2_sp_role_name[id].kill()
        del self.id_2_sp_role_name[id]

    def get_sp_role(self, id):
        return self.id_2_sp_role[id]

    def move_sp_role(self, id, x, y, given_time):
        # self.id_2_sp_role[id].move_to(x, y)
        # self.id_2_sp_role_name[id].move_to(x, y)

        self.id_2_sp_role[id].move_to_smoothly(x, y, given_time)
        self.id_2_sp_role_name[id].move_to_smoothly(x, y, given_time)

    def process_event(self, event):
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
                self.client.send(FightRole(role_id=2))

            if event.key == pygame.K_y:
                self.client.send(FightNpc(npc_id=1))

            if event.key == pygame.K_p:
                self.client.send(Sail())

        elif event.type == pygame.KEYUP:
            if event.key in [pygame.K_d, pygame.K_a, pygame.K_w, pygame.K_s]:
                if self.model.role.is_in_port():
                    self.model.role.stop_moving()

    def update(self, time_diff):
        # update sprites group
        self.sprites.update(time_diff)

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

    def hide_role_sprite(self):
        self.sp_role.change_img(sAssetMgr.images['player']['role_in_battle'])

    def unhide_role_sprite(self):
        self.sp_role.change_img(self.sp_role.frames['in_port'][pb.DirType.N][0])