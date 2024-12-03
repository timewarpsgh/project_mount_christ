import pygame_gui
import pygame
from functools import partial

import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\client\dialogs')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared')

from login_pb2 import *
from my_ui_elements import MyButton
from create_account_dialog import CreateAccountDialog
import constants as c

AUTO_CLICK_LOGIN = True

class LoginDialog:

    def __init__(self, mgr, client):
        self.mgr = mgr
        self.client = client

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
            text='登录',
            manager=self.mgr,
            container=panel,
            on_click=partial(self.login),
        )

        # add entry box
        self.entry_box_account = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((0, 50), (100, 50)),
            initial_text=self.client.account_and_password,
            manager=self.mgr,
            container=panel,
        )

        # add entry box
        self.entry_box_password = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((0, 100), (100, 50)),
            initial_text=self.client.account_and_password,
            manager=self.mgr,
            container=panel,
        )
        self.entry_box_password.set_text_hidden()
        self.entry_box_password.hidden_text_char = '*'

        # add buttion to manager
        self.no_account_button = MyButton(
            relative_rect=pygame.Rect((0, 150), (100, c.LOGIN_BUTTON_HEIGHT)),
            text='注册',
            manager=self.mgr,
            container=panel,
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