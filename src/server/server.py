import time
import os
import asyncio
import traceback
from queue import Queue
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor


from packet_handler import PacketHandler

# import from dir
import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')

sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared')
from shared import Connection

from object_mgr import sObjectMgr
from npc_mgr import sNpcMgr
from id_mgr import sIdMgr
from map_maker import sMapMaker
from map_mgr import sMapMgr


class Session(Connection):

    def __init__(self, server, reader, writer):
        Connection.__init__(self, reader, writer)

        self.server = server
        self.addr = writer.get_extra_info('peername')
        self.packet_handler = PacketHandler(self)

        self.previous_time = asyncio.get_event_loop().time()



    def on_disconnect(self):
        print('someone disconnectd!!!!')
        role = self.packet_handler.role
        if role:
            nearby_roles = sMapMgr.get_nearby_objects(role)
            sMapMgr.rm_object(role)

            for nearby_role in nearby_roles:
                nearby_role.session.packet_handler.on_disconnect_signal(role)

            self.server.rm_role(role.id)

        self.server.rm_session(self.addr)

    async def update(self):


        while True:
            if self.packet_handler.role:

                current_time = asyncio.get_event_loop().time()
                time_diff = current_time - self.previous_time
                self.previous_time = current_time

                await self.packet_handler.role.update(time_diff)

            else:
                pass

            await asyncio.sleep(0.1)



    async def main(self):

        await asyncio.gather(
            self.recv_co(),
            self.send_co(),
            self.update()
        )


class Server:

    def __init__(self):
        self.addr_2_session = {}
        self.id_2_role = {}

        self.id_mgr = sIdMgr

    def get_npc(self, id):
        return sNpcMgr.get_npc(id)

    def get_role(self, id):
        return self.id_2_role[id]

    def add_role(self, id, role):
        self.id_2_role[id] = role

    def rm_role(self, id):
        del self.id_2_role[id]
        print(f'role removed! now {self.id_2_role=}')

    def get_nearby_roles(self, role_id):
        nearby_roles = []
        for id, role in self.id_2_role.items():
            if id == role_id:
                continue
            nearby_roles.append(role)
        return nearby_roles

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
        try:
            await session.main()
        except Exception as e:

            print(f'some error occured: {e}')
            traceback.print_exc()
        else:
            pass

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