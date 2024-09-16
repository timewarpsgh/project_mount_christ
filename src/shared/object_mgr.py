import json

# import from dir
import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\server\models')

from world_models import Port, CargoTemplate, ShipTemplate, MateTemplate, Cannon, Village, \
    SESSION as WORLD_SESSION

class ObjectMgr:

    def __init__(self):
        self.id_2_port = {}
        self.__load_id_2_port()
        self.id_2_cargo_template = {}
        self.__load_id_2_cargo_template()

        self.economy_id_2_cargo_ids = {}
        self.__calculate_economy_id_2_cargo_ids()

        self.id_2_village = {}
        self.__load_id_2_village()

        self.id_2_ship_template = {}
        self.__load_id_2_ship_template()

        self.id_2_mate_template = {}
        self.__load_id_2_mate_template()


        self.economy_id_2_ship_ids = {}
        self.__init_economy_id_2_ship_ids()

        self.id_2_cannon = self.__load_id_2_cannon()

    def __load_id_2_cannon(self):
        id_2_cannon = {}
        for cannon in WORLD_SESSION.query(Cannon).all():
            id_2_cannon[cannon.id] = cannon
        return id_2_cannon

    def __init_economy_id_2_ship_ids(self):
        self.economy_id_2_ship_ids = {
            #### 'Iberia', ####
            0: [1, 19, 6, 8, 20, 9, 10, 11],

            #### 'Northern Europe', ####
            1: [2, 19, 7, 13, 14, 9, 20, 22, 11, 15, 16, 17],

            #### 'The Mediterranean', ####
            2: [19, 5, 6, 4, 20, 9, 10, 21],

            #### 'Ottoman Empire', ####
            4: [19, 6, 20, 9, 12, 10, 21],

            #### 'Middle East' , Southeast Asia, and Far East ####
            9: [19, 3, 12],
            10: [19, 3, 12],
            11: [19, 3, 12],
            12: [19, 3, 12, 18],

            #### 'Africa', ####
            3: [19, 7, 9, 10],
            5: [19, 7, 9, 10],
            8: [19, 7, 9, 10],

            #### 'America', ####
            6: [8, 13, 9, 10, 11],
            7: [8, 13, 9, 10, 11]
        }


    def __load_id_2_ship_template(self):
        for ship_template in WORLD_SESSION.query(ShipTemplate).all():
            self.id_2_ship_template[ship_template.id] = ship_template

    def __load_id_2_mate_template(self):
        for mate_template in WORLD_SESSION.query(MateTemplate).all():
            self.id_2_mate_template[mate_template.id] = mate_template

    def __load_id_2_village(self):
        for village in WORLD_SESSION.query(Village).all():
            self.id_2_village[village.id] = village

    def __calculate_economy_id_2_cargo_ids(self):
        for id, cargo_template in self.id_2_cargo_template.items():
            economy_id_2_buy_price = json.loads(cargo_template.buy_price)

            for economy_id, buy_price in economy_id_2_buy_price.items():
                if int(economy_id) not in self.economy_id_2_cargo_ids:
                    self.economy_id_2_cargo_ids[int(economy_id)] = []
                self.economy_id_2_cargo_ids[int(economy_id)].append(id)

        print('########## inited economy_id_2_cargo_ids')

    def __load_id_2_port(self):
        for port in WORLD_SESSION.query(Port).all():
            self.id_2_port[port.id] = port

    def __load_id_2_cargo_template(self):
        for cargo_template in WORLD_SESSION.query(CargoTemplate).all():
            self.id_2_cargo_template[cargo_template.id] = cargo_template

    def get_port(self, id):
        return self.id_2_port[id]

    def get_building_xy_in_port(self, building_id, port_id):
        port = self.get_port(port_id)
        dict = json.loads(port.building_locations)

        if str(building_id) not in dict:
            return None, None

        x = dict[str(building_id)]['x']
        y = dict[str(building_id)]['y']
        return x, y

    def get_cargo_template(self, id):
        return self.id_2_cargo_template[id]

    def get_cargo_ids(self, economy_id):

        return self.economy_id_2_cargo_ids[economy_id]

    def get_village(self, id):
        return self.id_2_village[id]

    def get_ship_template(self, id):
        return self.id_2_ship_template[id]

    def get_mate_template(self, id):
        return self.id_2_mate_template[id]

    def get_ship_ids(self, economy_id):
        return self.economy_id_2_ship_ids[economy_id]

# singleton
sObjectMgr = ObjectMgr()
print(f'########## inited sObjectMgr')
print(len(sObjectMgr.id_2_port), 'ports')
print(len(sObjectMgr.id_2_cargo_template), 'cargo_templates')
