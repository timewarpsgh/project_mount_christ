import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

# import from dir
import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')

from login_pb2 import *

from models import SESSION, Account, World as WorldModel, Role as RoleModel

EXECUTOR = ThreadPoolExecutor()


async def run_in_threads(method, packet):
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(EXECUTOR, method, packet)
    return res


class PacketHandler:
    """server"""

    def __init__(self, session):
        self.session = session
        self.account_id = None

    async def handle_packet(self, packet):
        packet_name = type(packet).__name__
        await getattr(self, f'handle_{packet_name}')(packet)
        print()

    def __get_new_account_res(self, new_account):
        account = SESSION.query(Account).\
            filter_by(account=new_account.account).\
            first()

        if account:
            return NewAccountRes.NewAccountResType.ACCOUNT_EXISTS
        else:
            new_obj = Account(
                account=new_account.account,
                password=new_account.password,
            )
            SESSION.add(new_obj)
            SESSION.commit()
            return NewAccountRes.NewAccountResType.OK

    async def handle_NewAccount(self, new_account):
        # add new account to db
        res_type = await run_in_threads(self.__get_new_account_res, new_account)

        new_account_res = NewAccountRes()
        new_account_res.new_account_res_type = res_type
        self.session.send(new_account_res)

    def __get_login_res(self, login):
        account = SESSION.query(Account).filter_by(
            account=login.account,
            password=login.password).first()

        if account:
            self.account_id = account.id
            return LoginRes.LoginResType.OK
        else:
            return LoginRes.LoginResType.WRONG_PASSWORD_OR_ACCOUNT

    async def handle_Login(self, login):
        res_type = await run_in_threads(self.__get_login_res, login)

        login_res = LoginRes()
        login_res.login_res_type = res_type
        self.session.send(login_res)

    def __get_worlds(self, any):
        worlds_models = SESSION.query(WorldModel).all()
        worlds = []
        for world_model in worlds_models:
            world = World()
            world.id = world_model.id
            world.name = world_model.name

            worlds.append(world)
        return worlds

    async def handle_GetWorlds(self, get_worlds):
        worlds = await run_in_threads(self.__get_worlds, '')

        get_worlds_res = GetWorldsRes()
        get_worlds_res.worlds.extend(worlds)
        self.session.send(get_worlds_res)

    def __get_roles(self, get_roles_in_world):
        world_id = get_roles_in_world.world_id
        account_id = self.account_id

        roles_models = SESSION.query(RoleModel).\
            filter_by(world_id=world_id).\
            filter_by(account_id=account_id).\
            all()

        roles = []
        for role_model in roles_models:
            role = Role()
            role.id = role_model.id
            role.name = role_model.name
            roles.append(role)

        return roles

    async def handle_GetRolesInWorld(self, get_roles_in_world):
        roles = await run_in_threads(self.__get_roles, get_roles_in_world)

        get_roles_in_world_res = GetRolesInWorldRes()
        get_roles_in_world_res.roles.extend(roles)
        self.session.send(get_roles_in_world_res)

    def __create_new_role(self, new_role):
        role_model = SESSION.query(RoleModel).\
            filter_by(name=new_role.name, world_id=new_role.world_id).\
            first()

        if role_model:
            return NewRoleRes.NewRoleResType.NAME_EXISTS
        else:
            new_obj = RoleModel(
                name=new_role.name,
                world_id=new_role.world_id,
                account_id=self.account_id
            )

            SESSION.add(new_obj)
            SESSION.commit()

            return NewRoleRes.NewRoleResType.OK

    async def handle_NewRole(self, new_role):
        res_type = await run_in_threads(self.__create_new_role, new_role)

        new_role_res = NewRoleRes()
        new_role_res.new_role_res_type = res_type
        self.session.send(new_role_res)

    def __enter_world(self, enter_world):
        role = SESSION.query(RoleModel).\
            filter_by(id=enter_world.role_id, account_id=self.account_id).\
            first()

        if role:
            role_entered = RoleEntered()
            role_entered.id = role.id
            role_entered.name = role.name
            role_entered.map_id = role.map_id
            role_entered.x = role.x
            role_entered.y = role.y


            enter_world_res = EnterWorldRes()
            enter_world_res.is_ok = True
            enter_world_res.role_entered.CopyFrom(role_entered)

            return enter_world_res
        else:
            enter_world_res = EnterWorldRes()
            enter_world_res.is_ok = False

            return enter_world_res

    async def handle_EnterWorld(self, enter_world):
        enter_world_res = await run_in_threads(self.__enter_world, enter_world)
        self.session.send(enter_world_res)