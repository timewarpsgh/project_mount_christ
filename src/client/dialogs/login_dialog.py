import pygame_gui
import pygame
from functools import partial

import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\client\dialogs')

from login_pb2 import *
from my_ui_elements import MyButton
from create_account_dialog import CreateAccountDialog


AUTO_CLICK_LOGIN = False

class LoginDialog:

    def __init__(self, mgr, client):
        self.mgr = mgr
        self.client = client

        # add ui window
        self.ui_window = pygame_gui.elements.UIWindow(
            rect=pygame.Rect((0, 0), (300, 300)),
            manager=self.mgr,
        )

        # add buttion to manager
        self.login_button = MyButton(
            relative_rect=pygame.Rect((0, 0), (100, 50)),
            text='登录',
            manager=self.mgr,
            container=self.ui_window,
            on_click=partial(self.login),
        )

        # add entry box
        self.entry_box_account = pygame_gui.elements.UITextEntryBox(
            relative_rect=pygame.Rect((0, 50), (100, 50)),
            initial_text=self.client.account_and_password,
            manager=self.mgr,
            container=self.ui_window,
        )

        # add entry box
        self.entry_box_password = pygame_gui.elements.UITextEntryBox(
            relative_rect=pygame.Rect((0, 100), (100, 50)),
            initial_text=self.client.account_and_password,
            manager=self.mgr,
            container=self.ui_window,
        )

        # add buttion to manager
        self.no_account_button = MyButton(
            relative_rect=pygame.Rect((0, 200), (100, 50)),
            text='没有账号？',
            manager=self.mgr,
            container=self.ui_window,
            on_click=partial(self.__make_create_account_dialog),
        )

        if AUTO_CLICK_LOGIN:
            self.login()

    def login(self):
        login = Login()
        login.account = self.entry_box_account.get_text()
        login.password = self.entry_box_password.get_text()
        self.client.send(login)


    def __make_create_account_dialog(self):
        CreateAccountDialog(self.mgr, self.client)