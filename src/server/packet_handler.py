import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

# import from dir
import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')

from login_pb2 import *

from models import create_session, Account

EXECUTOR = ThreadPoolExecutor()


async def run_in_threads(method, packet):
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(EXECUTOR, method, packet)
    return res


class PacketHandler:
    """server"""

    def __init__(self, session):
        self.session = session

    async def handle_packet(self, packet):
        packet_name = type(packet).__name__
        await getattr(self, f'handle_{packet_name}')(packet)
        print()

    def __add_new_account_to_db(self, new_account):
        session_to_db = create_session()

        account = session_to_db.query(Account).\
            filter_by(account=new_account.account).\
            first()

        if account:
            return NewAccountRes.NewAccountResType.ACCOUNT_EXISTS
        else:
            new_obj = Account(
                account=new_account.account,
                password=new_account.password,
            )
            session_to_db.add(new_obj)
            session_to_db.commit()
            return NewAccountRes.NewAccountResType.OK

    async def handle_NewAccount(self, new_account):
        print(time.time())
        print(time.time())

        # add new account to db
        res_type = await run_in_threads(self.__add_new_account_to_db, new_account)
        print(time.time())

        new_account_res = NewAccountRes()
        new_account_res.new_account_res_type = res_type
        self.session.send(new_account_res)

    async def handle_Login(self, login):
        login_res = LoginRes()
        login_res.login_res_type = LoginRes.LoginResType.OK
        self.session.send(login_res)

    async def handle_NewRole(self, new_role):
        new_role_res = NewRoleRes()
        new_role_res.new_role_res_type = NewRoleRes.NewRoleResType.OK
        self.session.send(new_role_res)