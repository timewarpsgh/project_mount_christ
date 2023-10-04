# import from dir
import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')

from login_pb2 import Login, NewAccount, LoginRes, LoginResType
from opcodes import OpCodeType


class Packet:

    def __init__(self, probuf_obj, opcode_value):
        two_bytes_for_opcode = opcode_value.to_bytes(2)
        bytes_for_obj = probuf_obj.SerializeToString()
        two_bytes_for_obj_len = len(bytes_for_obj).to_bytes(2)
        self.__bytes = two_bytes_for_opcode + two_bytes_for_obj_len + bytes_for_obj

    def get_bytes(self):
        return self.__bytes


def opcode_2_protbuf_obj(opcode_bytes):
    opcode_type_value = int.from_bytes(opcode_bytes)

    if opcode_type_value == OpCodeType.C_LOGIN.value:
        return Login()
    elif opcode_type_value == OpCodeType.C_NEW_ACCOUNT.value:
        return NewAccount()

def protbuf_obj_2_opcode_value(protbuff_obj):
    """for sending"""
    if isinstance(protbuff_obj, Login):
        return OpCodeType.C_LOGIN.value
    elif isinstance(protbuff_obj, NewAccount):
        return OpCodeType.C_NEW_ACCOUNT.value
    elif isinstance(protbuff_obj, LoginRes):
        return OpCodeType.S_LOGIN_RES.value