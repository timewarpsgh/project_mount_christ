import os
import sys
from queue import Queue
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

        self.got_packets = Queue() # each packet is a protbuf
        self.to_send_packets = Queue() # each packet is a protbuf
        self.__bytes_buffer = b''

        self.gui = None

    def send(self, protbuf_obj):
        self.to_send_packets.put(protbuf_obj)

    async def send_co(self):
        while True:
            await asyncio.sleep(0.1)

            while not self.to_send_packets.empty():
                protbuf_obj = self.to_send_packets.get()
                print(f'\n### sent packet {type(protbuf_obj)}')
                opcode_value = protbuf_obj_2_opcode_value(protbuf_obj)
                packet = Packet(protbuf_obj, opcode_value)
                self.writer.write(packet.get_bytes())

            await self.writer.drain()

    def receive_packets(self, bytes):
        self.__bytes_buffer += bytes

        while len(self.__bytes_buffer) >= 4:
            opcode_bytes = self.__bytes_buffer[:2]
            obj_len_bytes = self.__bytes_buffer[2:4]
            obj_bytes_cnt = int.from_bytes(obj_len_bytes)

            if len(self.__bytes_buffer) >= 4 + obj_bytes_cnt:
                obj_bytes = self.__bytes_buffer[4:4 + obj_bytes_cnt]

                protbuf_obj = opcode_2_protbuf_obj(opcode_bytes)

                protbuf_obj.ParseFromString(obj_bytes)
                self.got_packets.put(protbuf_obj)
                print(f'### got packet {type(protbuf_obj)}')

                # slice bytes_buffer
                self.__bytes_buffer = self.__bytes_buffer[4 + obj_bytes_cnt: ]
            else:
                break

    def process_got_packets(self):
        while not self.got_packets.empty():
            packet = self.got_packets.get()
            print(f'### processing packet {type(packet)}')

    async def recv_co(self):
        while True:
            # recv msg
            bytes = await self.reader.read(5000)

            # if disconn
            if bytes == b'':
                exit()

            self.receive_packets(bytes)
            self.process_got_packets()

    async def gui_co(self):
        # FOR TESING
        login = Login()
        login.account = '111'
        login.password = '222'
        self.send(login)

        await asyncio.sleep(0.3)

        new_account = NewAccount()
        new_account.account = '33'
        new_account.password = '44'
        self.send(new_account)


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