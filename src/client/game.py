import sys
from dataclasses import dataclass
import pygame
import pygame_gui
import asyncio
from login_pb2 import *

from gui import Gui
from graphics import Graphics
from model import Model
from asset_mgr import sAssetMgr
# import from dir
import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared')

import constants as c

@dataclass
class Game:

    def __init__(self, client=None):
        self.client = client

        pygame.init()
        icon = pygame.image.load(r'D:\data\code\python\project_mount_christ\src\client\ship.ico')
        pygame.display.set_icon(icon)
        pygame.display.set_caption('UW2OL')

        self.window_surface = pygame.display.set_mode((c.WINDOW_WIDTH, c.WINDOW_HEIGHT),
                                                      pygame.DOUBLEBUF | pygame.HWSURFACE)


        self.is_running = True

        self.clock = pygame.time.Clock()

        # load images
        sAssetMgr.load_images()
        sAssetMgr.load_sounds()

        # init gui
        self.gui = Gui(client)

        # init graphics
        self.graphics = Graphics(client, Model())



    async def run(self):
        while self.is_running:

            # get time_delta(limit frame rate)
            time_delta = self.clock.tick(c.FRAME_RATE) / 1000.0

            # update based on events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print('pygame quit event detected')
                    self.client.send(Disconnect())

                self.graphics.process_event(event)
                self.gui.process_event(event)


            # update based on time_delta
            self.gui.update(time_delta)
            self.graphics.update(time_delta)
            self.graphics.model.update(time_delta)

            # draw graphics
            self.window_surface.fill((0, 0, 0))
            self.graphics.draw(self.window_surface)
            self.gui.draw(self.window_surface)

            # flip
            pygame.display.update()

            await asyncio.sleep(0.0000001)


def main():
    game = Game()
    asyncio.run(game.run())


if __name__ == '__main__':
    main()
