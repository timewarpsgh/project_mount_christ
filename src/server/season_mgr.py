import random
import asyncio

# import from dir
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared', 'packets'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

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

        self.update_timer = c.SEASON_CHANGE_INTERVAL

        self.__randomize_wind_and_current()

    def __randomize_wind_and_current(self):
        self.wind_dir = random.choice(pb.DirType.values())
        self.wind_speed = random.choice(WIND_SPEED_LIST)

        self.current_dir = random.choice(pb.DirType.values())
        self.current_speed = random.choice(CURRENT_SPEED_LIST)

    # async def run_loop_to_update(self, server):
    #     while True:
    #         await asyncio.sleep(c.SEASON_CHANGE_INTERVAL)
    #         self.update()
    #         pack = self.gen_season_changed_pb()
    #         roles = server.get_roles()
    #         for role in roles:
    #             role.session.send(pack)

    def update(self, time_diff, server):
        self.update_timer -= time_diff

        if self.update_timer <= 0:
            self.update_timer = c.SEASON_CHANGE_INTERVAL

            self.season += 1
            if self.season > pb.SeasonType.WINTER:
                self.season = pb.SeasonType.SPRING

            self.__randomize_wind_and_current()

            pack = self.gen_season_changed_pb()
            roles = server.get_roles()
            for role in roles:
                role.session.send(pack)



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