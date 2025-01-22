import os
import sys
from queue import Queue
import asyncio


from packet_handler import PacketHandler

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared', 'packets'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from login_pb2 import *
import constants as c


from shared import Connection

from game import Game


IS_GAME_ON = True
ACCOUNT_AND_PWD = ''

class Client(Connection):

    def __init__(self):
        Connection.__init__(self, reader=None, writer=None)

        self.game = None
        self.packet_handler = PacketHandler(self)

        self.account_and_password = ACCOUNT_AND_PWD

    async def on_disconnect(self):
        exit()


    async def gui_co(self):
        if IS_GAME_ON:
            self.game = Game(self)
            await self.game.run()
        else:
            return

    async def main(self):
        reader, writer = await asyncio.open_connection(
            c.HOST, c.PORT)
        self.reader = reader
        self.writer = writer

        # Schedule three calls *concurrently*:
        await asyncio.gather(
            self.send_co(),
            self.recv_co(),
            self.gui_co(),
        )


def main():
    args = sys.argv




    c = Client()

    if len(args) == 1:
        pass
    else:
        account_and_password = args[1]
        print(account_and_password)

        c.account_and_password = account_and_password


    asyncio.run(c.main())


if __name__ == '__main__':
    main()