import os
import sys
from queue import Queue
import asyncio

from packet_handler import PacketHandler

sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')


from login_pb2 import *


sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared')
from shared import Connection

from game import Game


IS_GAME_ON = True


class Client(Connection):

    def __init__(self):
        Connection.__init__(self, reader=None, writer=None)

        self.game = None
        self.packet_handler = PacketHandler(self)

    def on_disconnect(self):
        exit()

    async def gui_co(self):
        if IS_GAME_ON:
            self.game = Game(self)
            await self.game.run()
        else:
            return

    async def main(self):
        # conn
        reader, writer = await asyncio.open_connection(
            'localhost', 12345)
        self.reader = reader
        self.writer = writer

        # Schedule three calls *concurrently*:
        await asyncio.gather(
            self.send_co(),
            self.recv_co(),
            self.gui_co(),
        )


def main():
    c = Client()
    asyncio.run(c.main())


if __name__ == '__main__':
    main()