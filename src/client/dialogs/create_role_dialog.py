import pygame_gui
import pygame
from functools import partial

import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared')

from login_pb2 import *
from my_ui_elements import MyButton
import constants as c


class CreateRoleDialog:

    def __init__(self, mgr, client, world_id):
        self.mgr = mgr
        self.client = client
        self.world_id = world_id

        # add ui window
        width = c.LOGIN_WINDOW_WIDTH
        height = c.LOGIN_WINDOW_HEIGHT
        self.ui_window = pygame_gui.elements.UIWindow(
            rect=pygame.Rect((0, 0), (width, height)),
            manager=self.mgr,
        )

        # add panel
        panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((0, 0), (width, height)),
            manager=self.mgr,
            container=self.ui_window,
        )

        # add buttion to manager
        self.login_button = MyButton(
            relative_rect=pygame.Rect((0, 0), (100, c.LOGIN_BUTTON_HEIGHT)),
            text='创建角色',
            manager=self.mgr,
            container=panel,
            on_click=partial(self.__create_role),
        )

        # add entry box
        self.entry_box_role_name = pygame_gui.elements.UITextEntryBox(
            relative_rect=pygame.Rect((0, 50), (100, 50)),
            initial_text='角色名',
            manager=self.mgr,
            container=panel,
        )

    def __create_role(self):
        print(f'send __create_role packet for {self.world_id=}')
        new_role = NewRole()

        new_role.world_id = self.world_id

        new_role.name = self.entry_box_role_name.get_text()
        new_role.nation = 2
        new_role.talent_in_nav = 1
        new_role.talent_in_acc = 1
        new_role.talent_in_bat = 1
        new_role.img_id = '1_2'

        self.client.send(new_role)


