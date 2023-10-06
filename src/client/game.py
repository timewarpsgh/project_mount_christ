from dataclasses import dataclass
import pygame
import pygame_gui
import asyncio

from gui import Gui


@dataclass
class Game:

    def __init__(self, client=None):
        self.client = client

        pygame.init()
        pygame.display.set_caption('Quick Start')

        self.window_surface = pygame.display.set_mode((800, 600))

        self.background = pygame.Surface((800, 600))
        self.background.fill(pygame.Color('#550000'))

        self.is_running = True

        self.clock = pygame.time.Clock()

        # init gui
        self.gui = Gui(client)


    async def run(self):
        while self.is_running:

            # get time_delta(limit frame rate)
            time_delta = self.clock.tick(60) / 1000.0

            # update
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False

                self.gui.process_event(event)


            self.gui.update(time_delta)

            # draw
            self.window_surface.blit(self.background, (0, 0))
            self.gui.draw(self.window_surface)

            # flip
            pygame.display.update()

            await asyncio.sleep(0.001)


def main():
    game = Game()
    asyncio.run(game.run())


if __name__ == '__main__':
    main()
