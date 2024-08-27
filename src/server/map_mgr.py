# import from dir
import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared')

import constants as c


class PortMap:
    def __init__(self, id):
        self.id = id
        self.id_2_object = {}

    def add_object(self, object):
        self.id_2_object[object.id] = object

        print('port map objs')
        print(self.id_2_object.keys())

    def rm_object(self, object):
        del self.id_2_object[object.id]

    def get_nearby_objects(self, object, include_self):
        # all
        if include_self:
            return list(self.id_2_object.values())
        else:
            objects = []
            for obj in self.id_2_object.values():
                if obj.id != object.id:
                    objects.append(obj)
            return objects
    def move_object(self, object, old_x, old_y, new_x, new_y):
        """ has no cell, so no need to move """
        pass


class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.id_2_object = {}

    def add_object(self, object):
        self.id_2_object[object.id] = object

    def rm_object(self, object):
        del self.id_2_object[object.id]

    def get_all_objects(self):
        return list(self.id_2_object.values())


class SeaMap:
    def __init__(self):
        self.id = 0
        self.cols = (c.WORLD_MAP_COLUMNS // c.CELL_TILES_COUNT) + 1 # 167 cells
        self.rows = (c.WORLD_MAP_ROWS // c.CELL_TILES_COUNT) + 1 # 84 cells
        self.cells = self.__init_cells()  # 2d array

    def __init_cells(self):

        cells = [[0] * self.cols for i in range(self.rows) ]
        for x in range(self.rows):
            for y in range(self.cols):
                cell = Cell(x, y)
                cells[x][y] = cell

        return cells

    def __get_cell(self, x, y):
        cell_x = x // c.CELL_TILES_COUNT
        cell_y = y // c.CELL_TILES_COUNT
        return self.cells[cell_x][cell_y]

    def add_object(self, object):
        cell = self.__get_cell(object.x, object.y)
        cell.add_object(object)

    def rm_object(self, object):
        cell = self.__get_cell(object.x, object.y)
        cell.rm_object(object)

    def move_object(self, object, old_x, old_y, new_x, new_y):
        """from old cell to new cell"""
        old_cell = self.__get_cell(old_x, old_y)
        new_cell = self.__get_cell(new_x, new_y)

        if old_cell.x == new_cell.x and old_cell.y == new_cell.y:
            return
        else:
            old_cell.rm_object(object)
            new_cell.add_object(object)

    def __get_nearby_cells(self, cell):
        # get 9 cells around cell
        nearby_cells = []
        for x in range(cell.x - 1, cell.x + 2):
            for y in range(cell.y - 1, cell.y + 2):
                if x >= 0 and x < self.rows and y >= 0 and y < self.cols:
                    nearby_cells.append(self.cells[x][y])
        return nearby_cells

    def get_nearby_objects(self, object, include_self):
        cell = self.__get_cell(object.x, object.y)
        cells = self.__get_nearby_cells(cell)
        objects = []
        for cell in cells:
            objs = cell.get_all_objects()
            for obj in objs:
                if include_self:
                    objects.append(obj)
                else:
                    if obj.id != object.id:
                        objects.append(obj)


        return objects


class MapMgr:

    def __init__(self):
        self.id_2_map = self.__init_maps()

    def __init_maps(self):
        id_2_map = {}
        id_2_map[0] = SeaMap()

        port_maps_cnt = 130
        for i in range(1, port_maps_cnt + 1):
            id_2_map[i] = PortMap(i)

        return id_2_map
    def get_map(self, id):
        return self.id_2_map[id]

    def add_object(self, object):
        map = self.get_map(object.map_id)
        map.add_object(object)

    def rm_object(self, object):
        map = self.get_map(object.map_id)
        map.rm_object(object)

    def move_object(self, object, old_x, old_y, new_x, new_y):
        map = self.get_map(object.map_id)
        map.move_object(object, old_x, old_y, new_x, new_y)

    def change_object_map(self, object, old_map_id, old_x, old_y, new_map_id, new_x, new_y):
        old_map = self.get_map(old_map_id)
        old_map.rm_object(object)

        new_map = self.get_map(new_map_id)
        new_map.add_object(object)

    def get_nearby_objects(self, object, include_self=False):
        return self.get_map(object.map_id).get_nearby_objects(object, include_self)


sMapMgr = MapMgr()
