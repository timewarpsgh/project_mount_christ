import pygame_gui
import pygame
from functools import partial


import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')


from login_pb2 import *
from my_ui_elements import MyButton


class CreateAccountDialog:

    def __init__(self, mgr, client):
        self.mgr = mgr
        self.client = client

        # add ui window
        self.ui_window = pygame_gui.elements.UIWindow(
            rect=pygame.Rect((0, 0), (300, 300)),
            manager=self.mgr,
        )

        # add buttion to manager
        self.create_account_button = MyButton(
            relative_rect=pygame.Rect((0, 0), (100, 50)),
            text='创建账号',
            manager=self.mgr,
            container=self.ui_window,
            on_click=partial(self.__create_account),
        )

        # add entry box
        self.entry_box_account = pygame_gui.elements.UITextEntryBox(
            relative_rect=pygame.Rect((0, 50), (100, 50)),
            initial_text='账号1',
            manager=self.mgr,
            container=self.ui_window,
        )

        # add entry box
        self.entry_box_password = pygame_gui.elements.UITextEntryBox(
            relative_rect=pygame.Rect((0, 100), (100, 50)),
            initial_text='密码1',
            manager=self.mgr,
            container=self.ui_window,
        )

    def __create_account(self):
        new_account = NewAccount()
        new_account.account = self.entry_box_account.get_text()
        new_account.password = self.entry_box_password.get_text()
        self.client.send(new_account)



