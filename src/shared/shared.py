from queue import Queue
import asyncio

# import from dir
import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')

from login_pb2 import Login, NewAccount, LoginRes, NewAccountRes
from opcodes import OpCodeType


class FullPacket:

    def __init__(self, probuf_obj):
        opcode_value = protbuf_obj_2_opcode_value(probuf_obj)
        two_bytes_for_opcode = opcode_value.to_bytes(2)
        bytes_for_obj = probuf_obj.SerializeToString()
        two_bytes_for_obj_len = len(bytes_for_obj).to_bytes(2)
        self.__bytes = two_bytes_for_opcode + two_bytes_for_obj_len + bytes_for_obj

    def get_bytes(self):
        return self.__bytes


class Connection:

    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer

        self.got_packets = Queue() # each packet is a protbuf
        self.to_send_packets = Queue() # each packet is a protbuf
        self.__bytes_buffer = b''
        self.packet_handler = None

    def send(self, protbuf_obj):
        self.to_send_packets.put(protbuf_obj)

    async def send_co(self):
        while True:
            await asyncio.sleep(0.1)

            while not self.to_send_packets.empty():
                protbuf_obj = self.to_send_packets.get()
                print(f'### sent packet {type(protbuf_obj)}\n')
                full_packet = FullPacket(protbuf_obj)
                self.writer.write(full_packet.get_bytes())

            await self.writer.drain()

    async def recv_co(self):
        while True:
            # recv msg
            bytes = await self.reader.read(5000)

            # if disconn
            if bytes == b'':
                self.on_disconnect()
                break

            self.receive_packets(bytes)
            self.process_got_packets()

    def on_disconnect(self):
        """virtual(to be implemented by sub_class)"""
        pass

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

                # slice self.__bytes_buffer
                self.__bytes_buffer = self.__bytes_buffer[4 + obj_bytes_cnt:]
            else:
                break

    def process_got_packets(self):
        while not self.got_packets.empty():
            packet = self.got_packets.get()
            self.packet_handler.handle_packet(packet)


## d and d_reversed
d = {
    'Login': 1,
    'LoginRes': 2,
    'NewAccount': 3,
    'NewAccountRes': 4,
}

d_reversed = {v: k for k, v in d.items()}


def opcode_2_protbuf_obj(opcode_bytes):
    opcode_type_value = int.from_bytes(opcode_bytes)
    return eval(d_reversed[opcode_type_value])()


def protbuf_obj_2_opcode_value(protbuff_obj):
    """for sending"""
    type_of_protbuff_obj_str = type(protbuff_obj).__name__
    opcode_value = d[type_of_protbuff_obj_str]
    return opcode_value
