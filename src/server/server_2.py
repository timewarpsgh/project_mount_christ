import time
import os
import asyncio
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor


import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')

from login_pb2 import Login


EXECUTOR = ThreadPoolExecutor()


class Session:
    def __init__(self, server, reader, writer):
        self.client_addr = writer.get_extra_info('peername')
        self.server = server
        self.reader = reader
        self.writer = writer

        self.client_account_id = None
        self.client_world_id = None
        self.client_pc_id = None
        self.role = None


    def send_to_this_client(self, pc_id, msg):
        small_server = self.server.pc_id_2_small_server[pc_id]
        small_server.send_to_client(msg)

    def send_packet_to_client(self, packet):
        pickled_obj = pickle.dumps(packet)
        packet_class_name = type(packet).__name__
        self.send_to_client(f'{packet_class_name}:{pickled_obj}')
        print(f'\n>>>> Sent Packet: {packet}')

    def send_to_client(self, msg):
        self.writer.write(msg.encode())
        # await self.writer.drain()

    def send_to_other_clients(self, msg):
        """other clients means nearby clients"""
        # get_nearby_roles
        role_id_2_ins = self.server.aoi_mgr.get_nearby_roles(self.role)

        for role_id in role_id_2_ins.keys():
            if role_id == self.client_pc_id:
                continue
            small_server = self.server.pc_id_2_small_server[role_id]
            small_server.send_to_client(msg)

    def send_to_other_non_target_clients(self, msg):
        """other clients means nearby clients"""
        # get_nearby_roles
        role_id_2_ins = self.server.aoi_mgr.get_nearby_roles(self.role)

        for role_id in role_id_2_ins.keys():
            if role_id == self.client_pc_id or role_id == self.role.target_role.pc_id:
                continue
            small_server = self.server.pc_id_2_small_server[role_id]
            small_server.send_to_client(msg)

    async def main(self):


        # self.send_to_client('hello client:')

        # loop
        while True:
            # recv msg
            data = await self.reader.read(5000)
            print(f'got data from client')
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


            if data == b'':
                self.server.rm_session(self.client_addr)
                break

            # send back
            self.writer.write(b'got msg')
            await self.writer.drain()

class Server:

    def __init__(self):
        self.addr_2_session = {}


        self.pc_id_2_role = {}
        self.pc_id_2_small_server = {}

    def add_session(self, session):
        self.addr_2_session[session.client_addr] = session
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