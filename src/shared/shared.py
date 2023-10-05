from queue import Queue
import asyncio

# import from dir
import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')

from login_pb2 import *
from opcodes import OPCODE_2_VALUE, VALUE_2_OPCODE


class FullPacket:

    def __init__(self, probuf_obj):
        opcode_value = self.__protbuf_obj_2_opcode_value(probuf_obj)
        two_bytes_for_opcode = opcode_value.to_bytes(2)
        bytes_for_obj = probuf_obj.SerializeToString()
        two_bytes_for_obj_len = len(bytes_for_obj).to_bytes(2)
        self.__bytes = two_bytes_for_opcode + two_bytes_for_obj_len + bytes_for_obj

    def get_bytes(self):
        return self.__bytes

    def __protbuf_obj_2_opcode_value(self, protbuff_obj):
        """for sending"""
        type_of_protbuff_obj_str = type(protbuff_obj).__name__
        opcode_value = OPCODE_2_VALUE[type_of_protbuff_obj_str]
        return opcode_value


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
        print(f'### send packet {type(protbuf_obj).__name__}')

    async def send_co(self):
        while True:
            await asyncio.sleep(0.1)

            while not self.to_send_packets.empty():
                protbuf_obj = self.to_send_packets.get()
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
            await self.process_got_packets()

    def on_disconnect(self):
        """virtual(to be implemented by sub_class)"""
        pass

    def __opcode_2_protbuf_obj(self, opcode_bytes):
        opcode_type_value = int.from_bytes(opcode_bytes)
        return eval(VALUE_2_OPCODE[opcode_type_value])()

    def receive_packets(self, bytes):
        self.__bytes_buffer += bytes

        while len(self.__bytes_buffer) >= 4:
            opcode_bytes = self.__bytes_buffer[:2]
            obj_len_bytes = self.__bytes_buffer[2:4]
            obj_bytes_cnt = int.from_bytes(obj_len_bytes)

            if len(self.__bytes_buffer) >= 4 + obj_bytes_cnt:
                obj_bytes = self.__bytes_buffer[4:4 + obj_bytes_cnt]

                protbuf_obj = self.__opcode_2_protbuf_obj(opcode_bytes)
                protbuf_obj.ParseFromString(obj_bytes)
                self.got_packets.put(protbuf_obj)
                print(f'### got packet {type(protbuf_obj).__name__}')

                # slice self.__bytes_buffer
                self.__bytes_buffer = self.__bytes_buffer[4 + obj_bytes_cnt:]
            else:
                break

    async def process_got_packets(self):
        while not self.got_packets.empty():
            packet = self.got_packets.get()
            await self.packet_handler.handle_packet(packet)










