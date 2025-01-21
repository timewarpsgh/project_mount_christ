import json
import random
import os
# import from dir
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'server', 'models'))

from world_models import Port, CargoTemplate, ShipTemplate, MateTemplate, ItemTemplate, \
    Cannon, Village, Maid, Aura, Event, \
    SESSION as WORLD_SESSION

class ObjectMgr:

    def __init__(self):
        self.id_2_port = self.__load_id_2_port()
        self.id_2_cargo_template = self.__load_id_2_cargo_template()
        self.economy_id_2_cargo_ids = self.__calculate_economy_id_2_cargo_ids()
        self.id_2_village = self.__load_id_2_village()
        self.id_2_ship_template = self.__load_id_2_ship_template()
        self.id_2_mate_template = self.__load_id_2_mate_template()
        self.economy_id_2_ship_ids = self.__init_economy_id_2_ship_ids()
        self.id_2_cannon = self.__load_id_2_cannon()
        self.id_2_item = self.__load_id_2_item()
        self.id_2_maid = self.__load_id_2_maid()
        self.id_2_aura = self.__load_id_2_aura()
        self.id_2_event = self.__load_id_2_event()

    def __load_id_2_aura(self):
        id_2_aura = {}
        for aura in WORLD_SESSION.query(Aura).all():
            id_2_aura[aura.id] = aura
        return id_2_aura

    def __load_id_2_event(self):
        id_2_event = {}
        for event in WORLD_SESSION.query(Event).all():
            id_2_event[event.id] = event
        return id_2_event

    def __load_id_2_maid(self):
        id_2_maid = {}
        for maid in WORLD_SESSION.query(Maid).all():
            id_2_maid[maid.id] = maid
        return id_2_maid

    def __load_id_2_item(self):
        id_2_item = {}
        for item in WORLD_SESSION.query(ItemTemplate).all():
            id_2_item[item.id] = item
        return id_2_item

    def __load_id_2_cannon(self):
        id_2_cannon = {}
        for cannon in WORLD_SESSION.query(Cannon).all():
            id_2_cannon[cannon.id] = cannon
        return id_2_cannon

    def __init_economy_id_2_ship_ids(self):
        economy_id_2_ship_ids = {
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

        return economy_id_2_ship_ids


    def __load_id_2_ship_template(self):
        id_2_ship_template = {}

        for ship_template in WORLD_SESSION.query(ShipTemplate).all():
            id_2_ship_template[ship_template.id] = ship_template

        return id_2_ship_template

    def __load_id_2_mate_template(self):
        id_2_mate_template = {}

        for mate_template in WORLD_SESSION.query(MateTemplate).all():
            id_2_mate_template[mate_template.id] = mate_template

        return id_2_mate_template

    def __load_id_2_village(self):
        id_2_village = {}

        for village in WORLD_SESSION.query(Village).all():
            id_2_village[village.id] = village

        return id_2_village

    def __calculate_economy_id_2_cargo_ids(self):
        economy_id_2_cargo_ids = {}

        for id, cargo_template in self.id_2_cargo_template.items():
            economy_id_2_buy_price = json.loads(cargo_template.buy_price)

            for economy_id, buy_price in economy_id_2_buy_price.items():
                if int(economy_id) not in economy_id_2_cargo_ids:
                    economy_id_2_cargo_ids[int(economy_id)] = []
                economy_id_2_cargo_ids[int(economy_id)].append(id)

        return economy_id_2_cargo_ids

    def __load_id_2_port(self):
        id_2_port = {}
        for port in WORLD_SESSION.query(Port).all():
            id_2_port[port.id] = port
        return id_2_port

    def __load_id_2_cargo_template(self):
        id_2_cargo_template = {}

        for cargo_template in WORLD_SESSION.query(CargoTemplate).all():
            id_2_cargo_template[cargo_template.id] = cargo_template

        return id_2_cargo_template

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

    def get_rand_village_id(self):
        village_id = random.randint(1, len(self.id_2_village))
        return village_id

    def get_ship_template(self, id):
        return self.id_2_ship_template[id]

    def get_mate_template(self, id):
        return self.id_2_mate_template[id]

    def get_ship_ids(self, economy_id):
        return self.economy_id_2_ship_ids[economy_id]

    def get_cannon(self, id):
        return self.id_2_cannon[id]

    def get_cannons(self):
        return self.id_2_cannon.values()

    def get_item(self, id):
        return self.id_2_item.get(id)

    def get_items(self):
        return list(self.id_2_item.values())

    def get_item_sell_price(self, id):
        return int(self.id_2_item[id].buy_price // 2)

    def get_maid(self, id):
        return self.id_2_maid[id]

    def get_aura(self, id):
        return self.id_2_aura[id]

    def get_event(self, id):
        return self.id_2_event.get(id)


# singleton
sObjectMgr = ObjectMgr()
print(f'########## inited sObjectMgr')
print(len(sObjectMgr.id_2_port), 'ports')
print(len(sObjectMgr.id_2_cargo_template), 'cargo_templates')
