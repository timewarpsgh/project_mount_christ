from dataclasses import dataclass
import pygame
import pygame_gui
import asyncio

from gui import Gui
from graphics import Graphics
from model import Model

@dataclass
class Game:

    def __init__(self, client=None):
        self.client = client

        pygame.init()
        pygame.display.set_caption('Quick Start')

        self.window_surface = pygame.display.set_mode((800, 600))

        # self.background = pygame.Surface((800, 600))
        # self.background.fill(pygame.Color('#550000'))

        self.is_running = True

        self.clock = pygame.time.Clock()

        # init gui
        self.gui = Gui(client)

        # init graphics
        self.graphics = Graphics(client, Model())


    async def run(self):
        while self.is_running:

            # get time_delta(limit frame rate)
            time_delta = self.clock.tick(60) / 1000.0

            # update based on events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False

                self.graphics.process_event(event)
                self.gui.process_event(event)


            # update based on time_delta
            self.gui.update(time_delta)
            self.graphics.update(time_delta)

            # draw graphics
            self.window_surface.fill((0, 0, 0))
            self.graphics.draw(self.window_surface)
            self.gui.draw(self.window_surface)

            # flip
            pygame.display.update()

            await asyncio.sleep(0.001)


def main():
    game = Game()
    asyncio.run(game.run())


if __name__ == '__main__':
    main()
