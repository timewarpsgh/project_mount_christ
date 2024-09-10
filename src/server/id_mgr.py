import json

# import from dir
import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\server\models')


from role_models import SESSION as ROLE_SESSION, \
    Mate as MateModel, \
    Ship as ShipModel

class IdMgr:

    def __init__(self):
        self.ships_last_id = self.__get_ships_last_id()
        self.mates_lats_id = self.__get_mates_last_id()

    def __get_ships_last_id(self):
        # query largest id in db
        return ROLE_SESSION.query(ShipModel.id).order_by(ShipModel.id.desc()).first()[0]

    def __get_mates_last_id(self):
        # query largest id in db
        return ROLE_SESSION.query(MateModel.id).order_by(MateModel.id.desc()).first()[0]

    def gen_new_ship_id(self):
        self.ships_last_id += 1
        return self.ships_last_id

    def gen_new_mate_id(self):
        self.mates_lats_id += 1
        return self.mates_lats_id


sIdMgr = IdMgr()