# import from dir
import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared')

import constants as c
import login_pb2 as pb

class PortMap:
    def __init__(self, id):
        self.id = id
        self.id_2_object = {}

        self.mate = None
        self.maid = None

        self.economy_index = 100
        self.industry_index = 100

        self.allied_nation = None
        self.price_index = 1.00
        self.governor = None




    def add_object(self, object, x=None, y=None):
        self.id_2_object[object.id] = object

        print('port map objs')
        print(self.id_2_object.keys())

    def rm_object(self, object, x=None, y=None):
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
        cell_x = y // c.CELL_TILES_COUNT
        cell_y = x // c.CELL_TILES_COUNT

        return self.cells[cell_x][cell_y]

    def add_object(self, object, x=None, y=None):
        if x and y:
            object_x = x
            object_y = y
        else:
            object_x = object.x
            object_y = object.y

        cell = self.__get_cell(object_x, object_y)

        print(f'added role {object.id} to cell {cell.x}, {cell.y}')

        cell.add_object(object)

    def rm_object(self, object, x=None, y=None):
        if x and y:
            object_x = x
            object_y = y
        else:
            object_x = object.x
            object_y = object.y


        cell = self.__get_cell(object_x, object_y)
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
            print(f'{object.id} moved '
                  f'from cell {old_cell.x}, {old_cell.y} '
                  f'to cell {new_cell.x}, {new_cell.y} ')

            old_nearby_cells = self.__get_nearby_cells(old_cell)
            new_nearby_cells = self.__get_nearby_cells(new_cell)
            intersection = old_nearby_cells & new_nearby_cells
            to_notify_new_nearby_cells = new_nearby_cells - intersection
            to_notify_old_nearby_cells = old_nearby_cells - intersection

            self.__notify_new_and_old_nearby_cells(
                object,
                to_notify_new_nearby_cells,
                to_notify_old_nearby_cells
            )

    def __notify_new_and_old_nearby_cells(self, object,
                                          to_notify_new_nearby_cells,
                                          to_notify_old_nearby_cells):

        # to_notify_new_nearby_cells
        for cell in to_notify_new_nearby_cells:
            objects = cell.get_all_objects()

            for my_obj in objects:
                # notify object appeared and started moving
                if my_obj.is_role():
                    my_obj.session.send(
                        pb.RoleAppeared(
                            id=object.id,
                            name=object.name,
                            x=object.x,
                            y=object.y,
                        )
                    )

                    if object.is_moving:
                        pack = pb.StartedMoving(
                            id=object.id,
                            src_x=object.x,
                            src_y=object.y,
                            dir=object.dir,
                            speed=object.speed,
                        )
                        my_obj.session.send(pack)

                # notify role appeared and started moving
                if object.is_role():
                    object.session.send(
                        pb.RoleAppeared(
                            id=my_obj.id,
                            name=my_obj.name,
                            x=my_obj.x,
                            y=my_obj.y,
                        )
                    )
                    if my_obj.is_moving:
                        pack = pb.StartedMoving(
                            id=my_obj.id,
                            src_x=my_obj.x,
                            src_y=my_obj.y,
                            dir=my_obj.dir,
                            speed=my_obj.speed,
                        )
                        object.session.send(pack)



        # to_notify_old_nearby_cells
        for cell in to_notify_old_nearby_cells:
            objects = cell.get_all_objects()

            for my_obj in objects:
                if my_obj.is_role():
                    my_obj.session.send(
                        pb.RoleDisappeared(
                            id=object.id,
                        )
                    )

                if object.is_role():
                    object.session.send(
                        pb.RoleDisappeared(
                            id=my_obj.id,
                        )
                    )

    def __get_nearby_cells(self, cell):
        # get 9 cells around cell
        nearby_cells = set()
        for x in range(cell.x - 1, cell.x + 2):
            for y in range(cell.y - 1, cell.y + 2):
                if x >= 0 and x < self.rows and y >= 0 and y < self.cols:
                    nearby_cells.add(self.cells[x][y])
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
        print(f'added role {object.id} to map {map.id}')

    def rm_object(self, object):
        map = self.get_map(object.map_id)
        map.rm_object(object)
        print(f'removed role {object.id} from map {map.id}')

    def move_object(self, object, old_x, old_y, new_x, new_y):
        map = self.get_map(object.map_id)
        map.move_object(object, old_x, old_y, new_x, new_y)

    def change_object_map(self, object, old_map_id, old_x, old_y, new_map_id, new_x, new_y):
        old_map = self.get_map(old_map_id)
        old_map.rm_object(object, old_x, old_y)
        print(f'removed role {object.id} from map {old_map_id}')

        new_map = self.get_map(new_map_id)
        new_map.add_object(object, new_x, new_y)
        print(f'added role {object.id} to map {new_map_id}')

    def get_nearby_objects(self, object, include_self=False):
        return self.get_map(object.map_id).get_nearby_objects(object, include_self)


sMapMgr = MapMgr()
