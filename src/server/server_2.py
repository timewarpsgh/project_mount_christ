import time
import os
import asyncio
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor


import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')

from login_pb2 import Login


class Session:
    def __init__(self, server, reader, writer):
        self.addr = writer.get_extra_info('peername')
        self.server = server
        self.reader = reader
        self.writer = writer

        self.got_packets = []
        self.to_send_packets = []

    def receive_packets(self, data):
        print(f'######### got data from client')
        print(data)
        opcode_bytes = data[:2]
        print(f'opcode_bytes: {opcode_bytes}')
        obj_len_bytes = data[2:4]
        print(f'obj_len_bytes: {obj_len_bytes}')
        obj_bytes = data[4:]

        print(f'obj_bytes: {obj_bytes}')
        login2 = Login()
        login2.ParseFromString(obj_bytes)
        print(login2.account)
        print(login2.password)

        self.got_packets.append(login2)
        print(f'got packet')

    def process_got_packets(self):
        while self.got_packets:
            packet = self.got_packets.pop()
            print(f'processing packet {packet}')
            self.to_send_packets.append(b'got login request')
            print(f'to_send_packets: {self.to_send_packets}')

    async def send_co(self):
        while True:
            await asyncio.sleep(0.1)

            while self.to_send_packets:
                packet = self.to_send_packets.pop()
                self.writer.write(packet)

            await self.writer.drain()

    async def recv_co(self):
        while True:
            # recv msg
            data = await self.reader.read(5000)
            print(f'got data from client')

            # if disconn
            if data == b'':
                self.server.rm_session(self.addr)
                break

            self.receive_packets(data)
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
              f'{self.addr_2_session}')

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