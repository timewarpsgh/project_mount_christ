import random


# import from dir
import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared')

import constants as c
import login_pb2 as pb

WIND_SPEED_LIST = list(range(0, 9))
CURRENT_SPEED_LIST = list(range(0, 4))


class SeasonMgr:

    def __init__(self):
        self.season = pb.SeasonType.SPRING

        self.wind_dir = None
        self.wind_speed = None

        self.current_dir = None
        self.current_speed = None

        self.__randomize_wind_and_current()
        print()

    def __randomize_wind_and_current(self):
        self.wind_dir = random.choice(pb.DirType.values())
        self.wind_speed = random.choice(WIND_SPEED_LIST)

        self.current_dir = random.choice(pb.DirType.values())
        self.current_speed = random.choice(CURRENT_SPEED_LIST)

    def update(self):
        self.season += 1
        if self.season > pb.SeasonType.WINTER:
            self.season = pb.SeasonType.SPRING

        self.__randomize_wind_and_current()


    def gen_season_changed_pb(self):
        pack = pb.SeasonChanged(
            season=self.season,
            wind_dir=self.wind_dir,
            wind_speed=self.wind_speed,
            current_dir=self.current_dir,
            current_speed=self.current_speed,
        )
        return pack


sSeasonMgr = SeasonMgr()