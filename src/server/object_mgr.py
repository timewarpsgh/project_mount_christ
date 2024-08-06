import json

# import from dir
import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\server\models')

from world_models import Port, CargoTemplate, \
    SESSION as WORLD_SESSION

class ObjectMgr:

    def __init__(self):
        self.id_2_port = {}
        self.__load_id_2_port()
        self.id_2_cargo_template = {}
        self.__load_id_2_cargo_template()

        self.economy_id_2_cargo_ids = {}
        self.__calculate_economy_id_2_cargo_ids()

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

    def get_cargo_template(self, id):
        return self.id_2_cargo_template[id]

    def get_cargo_ids(self, economy_id):

        return self.economy_id_2_cargo_ids[economy_id]

# singleton
sObjectMgr = ObjectMgr()
print(f'########## inited sObjectMgr')
print(len(sObjectMgr.id_2_port), 'ports')
print(len(sObjectMgr.id_2_cargo_template), 'cargo_templates')

print(sObjectMgr.economy_id_2_cargo_ids)