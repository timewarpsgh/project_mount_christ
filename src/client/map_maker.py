import numpy as np
from PIL import Image

# add relative directory to python_path
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

# import from common(dir)
import constants as c
import pygame
import random
from object_mgr import sObjectMgr

class MapMaker():
    def __init__(self):
        pass

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

        # make map
        port_map_pil_img = self.make_port_map(port_piddle, port_index, time_of_day)

        if save_img:
            print('port img saved!!!')
            port_map_pil_img.save(f"test_port_img.png")

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
        file_name = ''
        if time_of_day == 'random':
            file_name = random.choice(c.TIME_OF_DAY_OPTIONS)
        else:
            file_name = time_of_day

        img = Image.open(f"../../data/imgs/ports/PORTCHIP.{port_chip_file_num}  {file_name}.png")
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
        return port_img

    def set_world_map_tiles(self):
        # init dict
        self.world_map_tiles = {}

        # each time option
        for time_option in c.TIME_OF_DAY_OPTIONS:
            # read img
            img = Image.open(f"../../assets/images/world_map/{time_option}.png")

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
        with open("../../assets/images/world_map/w_map_piddle_array.txt", 'r') as myfile:
            num_array = myfile.read()

        nums_list = num_array.split(',')
        piddle = np.array(nums_list)
        piddle = piddle.reshape(ROWS, COLUMNS)

        # set
        self.world_map_piddle = piddle

    def make_partial_world_map(self, x_tile, y_tile, time_of_day='random'):
        """a small rectangular part of the world map.
            can be used after setting world_map_tiles and world_map_piddle.
        """
        # set partial_map_center
        self.x_tile = x_tile
        self.y_tile = y_tile

        # sea image with size 73 * 73
        COLUMNS = ROWS = c.PARTIAL_WORLD_MAP_TILES
        sea_img = Image.new('RGB', (COLUMNS * c.PIXELS_COVERED_EACH_MOVE, ROWS * c.PIXELS_COVERED_EACH_MOVE), 'red')
        HALF_TILES = c.PARTIAL_WORLD_MAP_TILES_IN_ONE_DIRECTION
        sea_piddle = self.world_map_piddle[y_tile-HALF_TILES:y_tile+HALF_TILES+1, x_tile-HALF_TILES:x_tile+HALF_TILES+1]
        print(sea_piddle.shape)

        # small piddle to image
        tiles = []
        if time_of_day == 'random':
            random_time = random.choice(c.TIME_OF_DAY_OPTIONS)
            tiles = self.world_map_tiles[random_time]
        else:
            tiles = self.world_map_tiles[time_of_day]

        for r in range(ROWS):
            for i in range(COLUMNS):
                left = i * c.PIXELS_COVERED_EACH_MOVE
                upper = r * c.PIXELS_COVERED_EACH_MOVE
                position = (left, upper)
                img = tiles[int(sea_piddle[r, i])]
                sea_img.paste(img, position)

        # PIL image to pygame image
        mode = sea_img.mode
        size = sea_img.size
        data = sea_img.tobytes()
        sea_img = pygame.image.fromstring(data, size, mode)

        # set to not drawing
        self.drawing_partial_map = False

        # ret
        return sea_img

        # sea_img.save("sea_img.png")

    def make_world_map(self):
        pass

sMapMaker = MapMaker()


if __name__ == '__main__':
    map_maker = MapMaker()
    # map_maker.make_port_piddle(1

    port_id = 17
    port_piddle, port_map = map_maker.make_port_piddle_and_map(port_id, 'random', save_img=True)

