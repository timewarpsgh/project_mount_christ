import os
import sys

import asyncio

sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')


from login_pb2 import Login
from opcodes import OpCodeType


class SerMsgMgr:

    async def S_CREATE_ACCOUNT_RESP(self, packet):
        pass

    async def S_LOGIN_RESP(self, packet):
        pass

    async def S_GET_WORLDS_RESP(self, packet):
        pass

    async def S_GET_PCS_IN_WORLD_RESP(self, packet):
        pass


class Packet:

    def __init__(self, probuf_obj):
        two_bytes_for_opcode = OpCodeType.C_LOGIN.value.to_bytes(2)
        bytes_for_obj = probuf_obj.SerializeToString()
        two_bytes_for_obj_len = len(bytes_for_obj).to_bytes(2)
        self.bytes = two_bytes_for_opcode + two_bytes_for_obj_len + bytes_for_obj
        print(f'packet bytes: {self.bytes}')


class Client:

    def __init__(self, client_id):
        self.client_id = client_id

        self.pc = None
        self.pc_id_2_role = None
        self.gui = None
        self.reader = None
        self.writer = None

        # msgs from gui(controller) to model
        self.gui_msgs_queue = []
        # msgs from model to gui(view)
        self.model_msgs_queue = []

    def parse_msg(self, msg):
        split_items = msg.split('@')
        cmd = split_items[0]
        args = split_items[1:]

        # turn digits from str to int
        new_args = []
        for arg in args:
            if arg.lstrip("-").isdigit():
                new_args.append(int(arg))
            else:
                new_args.append(arg)

        return cmd, new_args

    def run_cmd_in_gui(self, func, args):
        len_of_args = len(args)
        if len_of_args == 0:
            func()
        elif len_of_args == 1:
            func(args[0])
        elif len_of_args == 2:
            func(args[0], args[1])
        elif len_of_args == 3:
            func(args[0], args[1], args[2])
        elif len_of_args == 4:
            func(args[0], args[1], args[2], args[3])
        elif len_of_args == 5:
            func(args[0], args[1], args[2], args[3], args[4])
        else:
            print(f'!!!!!!!!! too many args !!!!!!!')

    async def run_cmd_in_role(self, func, args):
        len_of_args = len(args)
        if len_of_args == 0:
            await func()
        elif len_of_args == 1:
            await func(args[0])
        elif len_of_args == 2:
            await func(args[0], args[1])
        elif len_of_args == 3:
            await func(args[0], args[1], args[2])
        elif len_of_args == 4:
            await func(args[0], args[1], args[2], args[3])
        else:
            print(f'!!!!!!!!! too many args !!!!!!!')

    async def send_msg_and_run_cmd(self, msg):

        # parse cmd
        cmd, args = self.parse_msg(msg)

        # send msg
        print(f'\n###### Sent: {msg}\n')
        self.writer.write(msg.encode())
        await self.writer.drain()

        # if cmd in role
        if cmd in CMDS_IN_ROLE_DICT:
            # run cmd in role
            func = getattr(self.pc, cmd)
            print(f'\n!!!!! gonna run {cmd} with {args}')
            await self.run_cmd_in_role(func, args)
            print(f'\n!!!!! Ran {cmd} with {args}')

    def send_msg_to_gui(self, msg):
        # parse cmd
        cmd, args = self.parse_msg(msg)
        if cmd in CMDS_IN_MODEL_MSG_MGR:
            # run cmd in role
            func = getattr(ModelMsgMgr, cmd)
            args.insert(0, self.gui)
            self.run_cmd_in_gui(func, args)
            print(f'\n!!!!! GUI Ran {cmd} with {args}')

    async def send_gui_msgs_co(self):
        while True:
            if self.gui_msgs_queue:
                msg = self.gui_msgs_queue.pop(0)
                await self.send_msg_and_run_cmd(msg)
            else:
                await asyncio.sleep(0.01)

    async def send_model_msgs_co(self):
        while True:
            if self.model_msgs_queue:
                msg = self.model_msgs_queue.pop(0)
                if self.gui:
                    self.send_msg_to_gui(msg)
            else:
                await asyncio.sleep(0.01)

    def make_packet(self, cmd, args):

        if len(args) == 1:
            packet = eval(cmd)(args[0])
            return packet

        elif len(args) == 2:
            packet = eval(cmd)(args[0], args[1])
            return packet

        else:
            print(f'\n### len of args > 2!!')

    async def send_co(self):
        # get auto_send_msgs bases on client

        # encode object
        login = Login()

        login.account = '1234哈哈'
        login.password = '222'
        print(login.account)
        print(login.password)

        bytes = login.SerializeToString()
        print(bytes)
        print(f'len fo bytes: {len(bytes)}')

        packet = Packet(login)



        self.writer.write(packet.bytes)
        await self.writer.drain()

    async def recv_co(self):
        while True:
            # recv
            data = await self.reader.read(5000)

            # exit if got ''
            if not data:
                exit()

            print(f'got data {data}')


            # await self.handle_server_msg(data)

    async def handle_server_msg(self, data):

        packet_name, packet = get_packet_name_and_packet_from_data(data)

        # run this func
        if packet_name in Client.CMDS_IN_SER_MSG_MGR:
            func = getattr(SerMsgMgr, packet_name)

            await func(self, packet)

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
    c = Client(client_id='1')
    c.main()


if __name__ == '__main__':
    main()