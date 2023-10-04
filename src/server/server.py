import time
import os
import asyncio
from queue import Queue
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor


from packet_handler import PacketHandler

# import from dir
import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')

from login_pb2 import Login, NewAccount, LoginRes, LoginResType
from opcodes import OpCodeType

sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared')
from shared import Packet, opcode_2_protbuf_obj, protbuf_obj_2_opcode_value


class Session:

    def __init__(self, server, reader, writer):
        self.addr = writer.get_extra_info('peername')
        self.server = server
        self.reader = reader
        self.writer = writer

        self.got_packets = Queue() # each packet is a protbuf
        self.to_send_packets = Queue() # each packet is a protbuf
        self.__bytes_buffer = b''

        self.packet_handler = PacketHandler(self)

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
                print(f'\n### got packet {type(protbuf_obj)}')

                # slice bytes_buffer
                self.__bytes_buffer = self.__bytes_buffer[4 + obj_bytes_cnt: ]
            else:
                break

    def send(self, protbuf_obj):
        self.to_send_packets.put(protbuf_obj)

    def process_got_packets(self):
        while not self.got_packets.empty():
            packet = self.got_packets.get()
            print(f'### processing packet {type(packet)}')

            self.packet_handler.handle_packet(packet)

    async def send_co(self):
        while True:
            await asyncio.sleep(0.1)

            while not self.to_send_packets.empty():
                protbuf_obj = self.to_send_packets.get()
                print(f'### sent packet {type(protbuf_obj)}')
                opcode_value = protbuf_obj_2_opcode_value(protbuf_obj)
                packet = Packet(protbuf_obj, opcode_value)
                self.writer.write(packet.get_bytes())

            await self.writer.drain()

    async def recv_co(self):
        while True:
            # recv msg
            bytes = await self.reader.read(5000)

            # if disconn
            if bytes == b'':
                self.server.rm_session(self.addr)
                break

            self.receive_packets(bytes)
            self.process_got_packets()

    async def main(self):

        await asyncio.gather(
            self.recv_co(),
            self.send_co(),
        )


class Server:

    def __init__(self):
        self.addr_2_session = {}

    def add_session(self, session):
        self.addr_2_session[session.addr] = session
        print(f'\n#### !!new connection, now self.connected_clients: '
              f'{self.addr_2_session}\n')

    def rm_session(self, addr):
        del self.addr_2_session[addr]
        print(f'client disconnected!!')
        print(f'addr_2_session: {self.addr_2_session}')

    async def client_connected(self, reader, writer):
        session = Session(self, reader, writer)
        self.add_session(session)
        await session.main()

    async def main(self):
        server = await asyncio.start_server(
            self.client_connected, 'localhost', 12345)

        addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
        print(f'Serving on {addrs}')

        async with server:
            await server.serve_forever()


def main():
    server = Server()
    asyncio.run(server.main())


if __name__ == '__main__':
    main()