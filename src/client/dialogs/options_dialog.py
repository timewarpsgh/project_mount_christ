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
            rect=pygame.Rect((0, 500), (750, 50)),
            manager=self.mgr,
        )

        # buttons to add
        buttons_texts = ['Buildings', 'Options', 'Fight', 'Cmds', 'Items', 'Mates', 'Ships']

        for id, button_text in enumerate(buttons_texts):
            MyButton(
                relative_rect=pygame.Rect((0 + id * 100, 0), (100, 50)),
                text=button_text,
                manager=self.mgr,
                container=self.ui_window,
                on_click=partial(getattr(self, f'show_{button_text.lower()}_menu')),
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

    def __show_bar_menu(self):
        option_2_callback = {
            'Recruit Crew': '',
            'Dismiss Crew': '',
            'Treat': '',
            'Meet': '',
            'Fire Mate': '',
            'Waitress': '',
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )

    def __show_dry_dock_menu(self):
        option_2_callback = {
            'New Ship': '',
            'Used Ship': '',
            'Repair': '',
            'Sell': '',
            'Remodel': '',
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )

    def __show_harbor_menu(self):
        option_2_callback = {
            'Sail': '',
            'Load Supply': '',
            'Unload Supply': '',
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )

    def __show_inn_menu(self):
        option_2_callback = {
            'Check In': '',
            'Gossip': '',
            'Port Info': '',
            'Walk Around': '',
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )

    def __show_palace_menu(self):
        option_2_callback = {
            'Meet Ruler': '',
            'Defect': '',
            'Gold Aid': '',
            'Ship Aid': '',
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )

    def __show_job_house_menu(self):
        option_2_callback = {
            'Job Assignment': '',
            'Country Info': '',
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )

    def __show_bank_menu(self):
        option_2_callback = {
            'Check Balance': '',
            'Deposit': '',
            'Withdraw': '',
            'Borrow': '',
            'Repay': '',
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )

    def __show_item_shop_menu(self):
        option_2_callback = {
            'Buy': '',
            'Sell': '',
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )

    def __show_church_menu(self):
        option_2_callback = {
            'Pray': '',
            'Donate': '',
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )

    def __show_fortune_house_menu(self):
        option_2_callback = {
            'Life': '',
            'Career': '',
            'Love': '',
            'Mates': '',
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )

    def __exit_game(self):

        self.client.send(Disconnect())

    def show_buildings_menu(self):
        option_2_callback = {
            'Market': partial(self.__show_market_menu),
            'Bar': partial(self.__show_bar_menu),
            'Dry Dock': partial(self.__show_dry_dock_menu),
            'Harbor': partial(self.__show_harbor_menu),
            'Inn': partial(self.__show_inn_menu),
            'Palace': partial(self.__show_palace_menu),
            'Job House': partial(self.__show_job_house_menu),
            'Misc': 'test',
            'Bank': partial(self.__show_bank_menu),
            'Item Shop': partial(self.__show_item_shop_menu),
            'Church': partial(self.__show_church_menu),
            'Fortune House': partial(self.__show_fortune_house_menu),
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )

    def show_options_menu(self):
        option_2_callback = {
            'Language(L)': '',
            'Sounds': '',
            'Hot Keys': '',
            'Exit': partial(self.__exit_game),
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )

    def show_fight_menu(self):

        option_2_callback = {
            'View Enemy Ships': '',
            'All Ships Target': '',
            'All Ships Strategy': '',
            'One Ship Target': '',
            'One Ship Strategy': '',
            'Escape Battle': '',
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )

    def show_cmds_menu(self):
        option_2_callback = {
            'Enter Building (F)': '',
            'Enter Port (M)': '',
            'Go Ashore (G)': '',
            'Battle (B)': '',
            'Measure Cooridinate': '',
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )

    def show_items_menu(self):
        option_2_callback = {
            'Equipments': '',
            'Items': '',
            'Discoveries': '',
            'Diary': '',
            'World Map': '',
            'Port Map': ''
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )

    def show_mates_menu(self):
        option_2_callback = {
            'Admiral Info': '',
            'Mate Info': '',
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )

    def show_ships_menu(self):
        option_2_callback = {
            'Fleet Info': '',
            'Ship Info': '',
            'Swap Ships': '',
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )