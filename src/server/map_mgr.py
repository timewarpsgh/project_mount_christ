import random

# import from dir
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared', 'packets'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

import constants as c
import login_pb2 as pb
from object_mgr import sObjectMgr


class PortMap:
    def __init__(self, id):
        self.id = id
        self.id_2_object = {}

        self.mate_template = self.__init_mate_template()
        self.maid = None

        self.price_index = self.__init_price_index()
        self.economy_index = self.__get_random_economy_index()
        self.industry_index = self.__get_random_industry_index()

        self.allied_nation = self.__get_random_allied_nation()
        self.nation_2_investment = self.__init_nation_2_investment()

        self.role_name_2_investment = {}

        self.governor_name = None

        self.same_nation_tax = 0
        self.other_nation_tax = 0
        self.allow_withdraw = 1

    def __init_price_index(self):
        return random.randint(80, 120)

    def __init_nation_2_investment(self):
        nation_2_investment = {}
        for nation in c.Nation:
            nation_2_investment[nation.value] = 0

        return nation_2_investment

    def __get_random_allied_nation(self):
        if self.id in c.PORT_ID_2_NATION:
            return c.PORT_ID_2_NATION[self.id]
        else:
            return random.choice(list(c.Nation)).value

    def __get_random_economy_index(self):
        port_template = sObjectMgr.get_port(self.id)
        if port_template.economy:
            index = port_template.economy + random.randint(-200, 200)
        else:
            index = 0

        return index

    def __get_random_industry_index(self):
        port_template = sObjectMgr.get_port(self.id)
        if port_template.industry:
            index = port_template.industry + random.randint(-200, 200)
        else:
            index = 0

        return index

    def __init_mate_template(self):
        # 50 mate templates
        if self.id > 100:
            return None

        if self.id % 2 == 0:
            mate_template_id = self.id // 2
            mate_template = sObjectMgr.get_mate_template(mate_template_id)

            if mate_template_id <= 4:
                return None

            return mate_template
        else:
            return None

    def add_object(self, object, x=None, y=None):
        self.id_2_object[object.id] = object

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


    def receive_investment(self, role, ingots_cnt):
        # add to nation
        flag_ship = role.get_flag_ship()
        captain = flag_ship.get_captain()
        self.nation_2_investment[captain.nation] += ingots_cnt

        # add to self
        if role.name not in self.role_name_2_investment:
            self.role_name_2_investment[role.name] = ingots_cnt
        else:
            self.role_name_2_investment[role.name] += ingots_cnt

        # sort from high to low
        my_dict = self.role_name_2_investment
        sorted_dict = dict(sorted(my_dict.items(), key=lambda item: item[1], reverse=True))
        self.role_name_2_investment = sorted_dict

    def __get_new_allied_nation(self):
        # get the nation with the most investment from self.nation_2_investment
        nation = max(self.nation_2_investment, key=self.nation_2_investment.get)

        if self.nation_2_investment[nation] == 0:
            return self.allied_nation
        else:
            return nation

    def __get_new_governor_name(self):
        roles_names = list(self.role_name_2_investment.keys())
        if roles_names:
            new_governor_name = roles_names[0]
        else:
            new_governor_name = self.governor_name

        return new_governor_name

    def update(self):
        """called every year"""
        self.price_index = self.__init_price_index()
        self.economy_index = self.__get_random_economy_index()
        self.industry_index = self.__get_random_industry_index()

        self.allied_nation = self.__get_new_allied_nation()
        self.nation_2_investment = self.__init_nation_2_investment()

        self.governor_name = self.__get_new_governor_name()

        self.role_name_2_investment = {}





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

        # print(f'added role {object.id} to cell {cell.x}, {cell.y}')

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
            # print(f'{object.id} moved '
            #       f'from cell {old_cell.x}, {old_cell.y} '
            #       f'to cell {new_cell.x}, {new_cell.y} ')

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

        self.port_timer = c.ONE_YEAR_INTERVAL

    def __init_maps(self):
        id_2_map = {}
        id_2_map[0] = SeaMap()

        port_maps_cnt = 130
        for i in range(1, port_maps_cnt + 1):
            id_2_map[i] = PortMap(i)

        return id_2_map

    def get_port_maps(self):
        port_maps = []
        for id in range(1, 101):
            port_maps.append(self.id_2_map[id])

        return port_maps

    def get_map(self, id):
        return self.id_2_map[id]

    def add_object(self, object):
        map = self.get_map(object.map_id)
        map.add_object(object)
        # print(f'added role {object.id} to map {map.id}')

    def rm_object(self, object):
        map = self.get_map(object.map_id)
        map.rm_object(object)
        # print(f'removed role {object.id} from map {map.id}')

    def move_object(self, object, old_x, old_y, new_x, new_y):
        map = self.get_map(object.map_id)
        map.move_object(object, old_x, old_y, new_x, new_y)

    def change_object_map(self, object, old_map_id, old_x, old_y, new_map_id, new_x, new_y):
        old_map = self.get_map(old_map_id)
        old_map.rm_object(object, old_x, old_y)
        # print(f'removed role {object.id} from map {old_map_id}')

        new_map = self.get_map(new_map_id)
        new_map.add_object(object, new_x, new_y)
        print(f'added role {object.id} to map {new_map_id}')

    def get_nearby_objects(self, object, include_self=False):
        return self.get_map(object.map_id).get_nearby_objects(object, include_self)

    def __update_port_maps(self):
        for port_map in self.get_port_maps():
            port_map.update()

    def update(self, time_diff):
        self.port_timer -= time_diff
        if self.port_timer <= 0:
            self.__update_port_maps()
            self.port_timer = c.ONE_YEAR_INTERVAL


sMapMgr = MapMgr()
