import pygame_gui
import pygame
from functools import partial

import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\client\dialogs')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\client')

from login_pb2 import *
from my_ui_elements import MyButton
from create_account_dialog import CreateAccountDialog
from my_ui_elements import MyMenuWindow

class OptionsDialog:

    def __init__(self, mgr, client):
        self.mgr = mgr
        self.client = client

        # add ui window
        self.ui_window = pygame_gui.elements.UIWindow(
            rect=pygame.Rect((0, 500), (300, 50)),
            manager=self.mgr,
        )

        # add buttion to manager
        self.login_button = MyButton(
            relative_rect=pygame.Rect((0, 0), (100, 50)),
            text='Buildings',
            manager=self.mgr,
            container=self.ui_window,
            on_click=partial(self.__show_buildings_menu),
        )


    def __send_get_available_cargos(self):
        self.client.send(GetAvailableCargos())

    def __show_market_menu(self):
        option_2_callback = {
            'Buy': partial(self.__send_get_available_cargos),
            'Sell': '',
            'Price Index': '',
            'Investment State': '',
            'Invest': '',
            'Defeat Administrator': '',
            'Manage': '',
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )

    def __show_buildings_menu(self):
        option_2_callback = {
            'Market': partial(self.__show_market_menu),
            'Bar': '',
            'Dry Dock': '',
            'Harbor': '',
            'Inn': '',
            'Palace': '',
            'Job House': '',
            'Misc': '',
            'Bank': '',
            'Item Shop': '',
            'Church': '',
            'Fortune House': '',
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )

