import os
import sys
from queue import Queue
import asyncio

from packet_handler import PacketHandler

sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')


from login_pb2 import *


sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared')
from shared import Connection


class Client(Connection):

    def __init__(self):
        Connection.__init__(self, reader=None, writer=None)

        self.gui = None
        self.packet_handler = PacketHandler(self)

    def on_disconnect(self):
        exit()

    async def gui_co(self):
        # FOR TESING
        new_account = NewAccount()
        new_account.account = 'test_account_name1'
        new_account.password = 'test_pwd'
        self.send(new_account)

        await asyncio.sleep(0.3)

        login = Login()
        login.account = 'test_account_name11'
        login.password = 'test_pwd'
        self.send(login)

        await asyncio.sleep(0.3)

        new_role = NewRole()
        new_role.name = 'test_role_name'
        self.send(new_role)

        # if GUI_ON:
        #     gui = GUI(client=self)
        #     self.gui = gui
        #     await gui.run()
        # else:
        #     return

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