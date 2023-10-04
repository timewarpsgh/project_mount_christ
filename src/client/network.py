import os
import sys

import asyncio

sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')


from login_pb2 import Login, NewAccount
from opcodes import OpCodeType

sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared')
from shared import Packet, opcode_2_protbuf_obj, protbuf_obj_2_opcode_value


class Client:

    def __init__(self):
        self.reader = None
        self.writer = None

        self.gui = None

    async def send_co(self):
        # send login
        login = Login()

        login.account = '1234哈哈'
        login.password = '222'

        opcode_value = protbuf_obj_2_opcode_value(login)

        packet = Packet(login, opcode_value)


        self.writer.write(packet.get_bytes())
        await self.writer.drain()

        await asyncio.sleep(0.5)


        # encode object
        new_account = NewAccount()

        new_account.account = 'login2'
        new_account.password = 'login2'

        opcode_value = protbuf_obj_2_opcode_value(new_account)

        packet = Packet(new_account, opcode_value)

        self.writer.write(packet.get_bytes())
        await self.writer.drain()
        print('sent login 2!!')

    async def recv_co(self):
        while True:
            # recv
            data = await self.reader.read(5000)

            # exit if got ''
            if not data:
                exit()

            print(f'got data {data}')


            # await self.handle_server_msg(data)

    async def gui_co(self):
        if GUI_ON:
            gui = GUI(client=self)
            self.gui = gui
            await gui.run()
        else:
            return

    async def start(self):
        # conn
        reader, writer = await asyncio.open_connection(
            'localhost', 12345)
        self.reader = reader
        self.writer = writer

        # Schedule three calls *concurrently*:
        await asyncio.gather(
            self.send_co(),
            self.recv_co(),
            # self.gui_co(),
            # self.send_gui_msgs_co(),
            # self.send_model_msgs_co(),
        )

    def main(self):
        asyncio.run(self.start())


def main():
    c = Client()
    c.main()


if __name__ == '__main__':
    main()