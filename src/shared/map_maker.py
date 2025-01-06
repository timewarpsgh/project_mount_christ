import numpy as np
from PIL import Image

# add relative directory to python_path
import sys, os
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')
# sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

import login_pb2 as pb

# import from common(dir)
import constants as c
import pygame
import random
from object_mgr import sObjectMgr

class MapMaker():

    def __init__(self):
        self.world_map_tiles = None
        self.world_map_piddle = None
        self.x_tile = None
        self.y_tile = None

        self.port_piddle = None
        self.time_of_day = None

        self.time_change_timer = 0
        self.time_of_day_index = 0

        self.partial_world_maps = {}

    def get_time_of_day(self):
        if self.time_of_day:
            return self.time_of_day
        else:
            return 'random'

    def make_port_piddle_and_map(self, port_index, time_of_day='random', save_img=False):
        port_index -= 1
        """make a port's tile matrix and image"""
        # normal and supply ports
        if port_index <= 99:
            pass
        else:
            port_index = 100

        # make piddle
        port_piddle = self.make_port_piddle(port_index)
        self.port_piddle = port_piddle

        # make map
        port_map_pil_img, time_type = self.make_port_map(port_piddle, port_index, time_of_day)

        if save_img:
            print('port img saved!!!')
            port_map_pil_img.save(f"D:\data\imgs\port_imgs\\{i}.png")

        self.time_of_day = time_type

        mode = port_map_pil_img.mode
        size = port_map_pil_img.size
        data = port_map_pil_img.tobytes()

        port_map = pygame.image.frombytes(data, size, mode)



        # ret
        return (port_piddle, port_map)

    def make_port_piddle(self, port_index):
        """piddle is a 2D-array(matrix)"""
        # get path
        port_index_with_leading_zeros = str(port_index).zfill(3)
        map_path = f"../../data/imgs/ports/PORTMAP.{port_index_with_leading_zeros}"

        # get piddle
        with open(map_path, 'rb') as file:
            bytes = file.read()
            list_of_numbers = list(bytes)
            list_of_numbers = [number + 1 for number in list_of_numbers]

            piddle = np.array(list_of_numbers)
            piddle = piddle.reshape(96, 96)
            return piddle

    def make_port_map(self, port_piddle, port_index, time_of_day):
        """make port image"""
        # port_id to port_chip_file_num
        tileset = sObjectMgr.get_port(port_index + 1).tile_set

        port_tile_set = 2 * tileset
        port_chip_file_num = str(port_tile_set).zfill(3)

        # read img
        time_type = ''
        if time_of_day == 'random':
            time_type = random.choice(list(c.TimeType))
        else:
            time_type = time_of_day

        img = Image.open(f"../../data/imgs/ports/PORTCHIP.{port_chip_file_num}  {time_type.value}.png")
        CHIP_TILES_COUNT = 16

        # cut to tiles
        port_tiles = ['']
        for k in range(CHIP_TILES_COUNT):
            for i in range(CHIP_TILES_COUNT):
                left = i * c.PIXELS_COVERED_EACH_MOVE
                upper = k * c.PIXELS_COVERED_EACH_MOVE
                width = height = c.PIXELS_COVERED_EACH_MOVE
                right = left + width
                lower = upper + height

                region = (left, upper, right, lower)
                img_cropped = img.crop(region)
                port_tiles.append(img_cropped)

        # make port map image
        MAP_TILES_COUNT = 96
        MAP_SIZE = MAP_TILES_COUNT * CHIP_TILES_COUNT
        port_img = Image.new('RGB', (MAP_SIZE, MAP_SIZE), 'red')

        for r in range(MAP_TILES_COUNT):
            for i in range(MAP_TILES_COUNT):
                left = i * c.PIXELS_COVERED_EACH_MOVE
                upper = r * c.PIXELS_COVERED_EACH_MOVE
                position = (left, upper)
                img = port_tiles[port_piddle[r, i]]
                port_img.paste(img, position)

        # ret
        return port_img, time_type

    def set_world_map_tiles(self):
        # init dict
        self.world_map_tiles = {}

        # each time option
        for time_option in c.TIME_OF_DAY_OPTIONS:
            # read img
            img = Image.open(f"../../data/imgs/world_map/{time_option}.png")

            # cut to tiles
            world_map_tiles = ['']
            for k in range(8):
                for i in range(16):
                    left = i * c.PIXELS_COVERED_EACH_MOVE
                    upper = k * c.PIXELS_COVERED_EACH_MOVE
                    width = height = c.PIXELS_COVERED_EACH_MOVE
                    right = left + width
                    lower = upper + height

                    region = (left, upper, right, lower)
                    img_cropped = img.crop(region)
                    world_map_tiles.append(img_cropped)

            # set
            self.world_map_tiles[time_option] = world_map_tiles

    def set_world_piddle(self):
        """world map(sea) matrix"""
        # columns and rows
        COLUMNS = c.WORLD_MAP_COLUMNS;
        ROWS = c.WORLD_MAP_ROWS;

        # get piddle from txt
        num_array = ''
        with open("../../data/imgs/world_map/w_map_piddle_array.txt", 'r') as myfile:
            num_array = myfile.read()

        nums_list = num_array.split(',')
        piddle = np.array(nums_list)
        piddle = piddle.reshape(ROWS, COLUMNS)

        # set
        self.world_map_piddle = piddle

    def make_partial_world_map(self, x_tile, y_tile, time_of_day='random', save_img=False):
        """a small rectangular part of the world map.
            can be used after setting world_map_tiles and world_map_piddle.
        """

        # set partial_map_center
        self.x_tile = x_tile
        self.y_tile = y_tile

        # sea image with size 73 * 73
        COLUMNS = ROWS = c.PARTIAL_WORLD_MAP_TILES
        HALF_TILES = c.PARTIAL_WORLD_MAP_TILES_IN_ONE_DIRECTION
        sea_piddle = self.world_map_piddle[y_tile-HALF_TILES:y_tile+HALF_TILES+1, x_tile-HALF_TILES:x_tile+HALF_TILES+1]

        # for each time_type
        for time_type in list(c.TimeType):
            # small piddle to image
            sea_img = Image.new(
                'RGB',
                (COLUMNS * c.PIXELS_COVERED_EACH_MOVE, ROWS * c.PIXELS_COVERED_EACH_MOVE),
                'red'
            )

            tiles = self.world_map_tiles[time_type.value]

            for r in range(ROWS):
                for i in range(COLUMNS):
                    left = i * c.PIXELS_COVERED_EACH_MOVE
                    upper = r * c.PIXELS_COVERED_EACH_MOVE
                    position = (left, upper)
                    img = tiles[int(sea_piddle[r, i])]
                    sea_img.paste(img, position)

            # save img
            if save_img:
                sea_img.save("sea_img.png")

            # PIL image to pygame image
            mode = sea_img.mode
            size = sea_img.size
            data = sea_img.tobytes()
            sea_img = pygame.image.frombytes(data, size, mode)

            # set partial_world_maps
            self.partial_world_maps[time_type.value] = sea_img

        # set to not drawing
        self.drawing_partial_map = False

        # ret
        if time_of_day == 'random':
            sea_img = random.choice(list(self.partial_world_maps.values()))
        else:
            sea_img = self.partial_world_maps[time_of_day]

        return sea_img


    def can_move_in_port_back(self, map_id, now_x, now_y, dir):

        piddle = self.port_piddle

        # x and y reversed!!!!
        y = now_x
        x = now_y

        # basic 4 directions
        if dir == pb.DirType.N:
            if now_y <= 0:
                return False

            # not in asia
            if map_id < 94:
                if piddle[x, y] in c.WALKABLE_TILES and piddle[x, y + 1] in c.WALKABLE_TILES:
                    return True
            # in asia
            else:
                if piddle[x, y] in c.WALKABLE_TILES_FOR_ASIA and piddle[x, y + 1] in c.WALKABLE_TILES_FOR_ASIA:
                    return True

        elif dir == pb.DirType.S:
            if now_y >= c.PORT_MAP_EDGE:
                return False

            if piddle[x + 2, y] in c.WALKABLE_TILES and piddle[x + 2, y + 1] in c.WALKABLE_TILES:
                return True

        elif dir == pb.DirType.W:
            if now_x <= 0:
                return False

            if piddle[x + 1, y - 1] in c.WALKABLE_TILES:
                return True

        elif dir == pb.DirType.E:
            if now_x >= c.PORT_MAP_EDGE:
                return False

            if piddle[x + 1, y + 2] in c.WALKABLE_TILES:
                return True

        # ret
        return False

    def can_move_in_port(self, map_id, now_x, now_y, dir):

        piddle = self.port_piddle

        # x and y reversed!!!!
        y = now_x
        x = now_y

        edge_len = 16

        # basic 4 directions
        if dir == pb.DirType.N:
            if now_y <= edge_len:
                return False

            if piddle[now_y - 1, now_x] in c.WALKABLE_TILES and piddle[now_y - 1, now_x + 1] in c.WALKABLE_TILES:
                return True

        elif dir == pb.DirType.S:
            if now_y >= (c.PORT_MAP_EDGE - edge_len + 6):
                return False

            if piddle[x + 2, y] in c.WALKABLE_TILES and piddle[x + 2, y + 1] in c.WALKABLE_TILES:
                return True

        elif dir == pb.DirType.W:
            if now_x <= edge_len:
                return False

            if piddle[now_y + 1, now_x - 1] in c.WALKABLE_TILES and piddle[now_y, now_x - 1] in c.WALKABLE_TILES:
                return True

        elif dir == pb.DirType.E:
            if now_x >= c.PORT_MAP_EDGE - edge_len:
                return False

            if piddle[now_y + 1, now_x + 2] in c.WALKABLE_TILES and piddle[now_y, now_x + 2] in c.WALKABLE_TILES:
                return True

        # ret
        return False

    def can_move_at_sea(self, now_x, now_y, dir):
        # get piddle
        piddle = self.world_map_piddle

        # x and y reversed!!!!
        y = now_x
        x = now_y

        tile_list = c.DIRECT_2_SEA_MOVE_COLLISION_TILES[dir]
        for tile in tile_list:
            dx = tile[0]
            dy = tile[1]
            tile_id = int(piddle[x + dx, y + dy])
            if not tile_id in c.SAILABLE_TILES:
                return False

        return True

    def can_land(self, now_x, now_y):
        if self.can_move_at_sea(now_x, now_y, pb.DirType.N) and \
                self.can_move_at_sea(now_x, now_y, pb.DirType.S) and \
                self.can_move_at_sea(now_x, now_y, pb.DirType.E) and \
                self.can_move_at_sea(now_x, now_y, pb.DirType.W) and \
                self.can_move_at_sea(now_x, now_y, pb.DirType.NE) and \
                self.can_move_at_sea(now_x, now_y, pb.DirType.NW) and \
                self.can_move_at_sea(now_x, now_y, pb.DirType.SE) and \
                self.can_move_at_sea(now_x, now_y, pb.DirType.SW):

            return False
        else:
            return True

    def get_alt_dir_at_sea(self, now_x, now_y, now_dir):
        for alt_direction in c.NOW_DIRECT_2_ALTERNATIVE_DIRECTS[now_dir]:
            if self.can_move_at_sea(now_x, now_y, alt_direction):
                return alt_direction
        return None

    def update(self, time_diff, role):
        self.time_change_timer -= time_diff
        if self.time_change_timer <= 0:
            self.time_change_timer = c.SUPPLY_CONSUMPTION_INVERVAL / 4
            self.time_of_day = list(c.TimeType)[self.time_of_day_index]

            self.time_of_day_index += 1
            if self.time_of_day_index >= 4:
                self.time_of_day_index = 0

            # for testing
            # self.time_of_day_index = 1

            print(f'{self.time_of_day=}')
            partial_world_map_img = self.partial_world_maps[self.time_of_day.value]
            role.graphics.sp_background.change_img(partial_world_map_img)


sMapMaker = MapMaker()


if __name__ == '__main__':
    map_maker = MapMaker()
    for i in range(1, 102):
        map_maker.make_port_piddle_and_map(i, c.TimeType.DAY)


