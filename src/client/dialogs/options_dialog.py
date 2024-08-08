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
from my_ui_elements import MyMenuWindow, MyPanelWindow
from asset_mgr import sAssetMgr


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


    def __make_menu(self, dict):
        MyMenuWindow(
            title='',
            option_2_callback=dict,
            mgr=self.mgr
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

    def __show_one_ship_states(self, ship):
        print(f'show states for {ship.id}')
        dict = {
            'name/type/captain': f'{ship.name}/{ship.ship_template_id}/{ship.captain}',
            '1': '',
            'tacking/power/speed': f'{ship.tacking}/{ship.power}',
            'durability': f'{ship.now_durability}/{ship.max_durability}',
            '2': '',
            'capacity': f'{ship.capacity}',
            'guns/max_guns': f'{ship.now_guns}/{ship.max_guns}',
            'min_crew/crew/max_crew': f'{ship.min_crew}/{ship.now_crew}/{ship.max_crew}',
            '3': '',
            'useful_capacity': f'{ship.capacity}',
        }

        # make text from dict
        text = self.__dict_2_txt(dict)

        # get ship image
        ship_image = sAssetMgr.images['ships']['carrack']

        MyPanelWindow(
            rect=pygame.Rect((59, 12), (350, 400)),
            ui_manager=self.mgr,
            text=text,
            image=ship_image,
        )

    def __dict_2_txt(self, dict):
        text = ''
        for k, v in dict.items():
            if k.isdigit():
                text += f'<br>'
            else:
                text += f'{k}: {v}<br>'
        return text

    def __show_ship_info_menu(self):
        ship_mgr = self.client.game.graphics.model.role.ship_mgr

        option_2_callback = {
        }

        for id, ship in ship_mgr.id_2_ship.items():
            option_2_callback[ship.name] = partial(self.__show_one_ship_states, ship_mgr.get_ship(id))


        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )

    def __show_one_mate_states(self, mate):

        dict = {
            'name/nation': f"{mate.name}/{mate.nation}",
            'duty': mate.assigned_duty,
            '1': '',
            'lv/points': f"{mate.lv}/{mate.points}",
            '2': '',
            'navigation/accounting/battle': f"{mate.navigation}/{mate.accounting}/{mate.battle}",

            '3': '',
            'talent in navigation/accounting/battle':
                f"{mate.talent_in_navigation}/{mate.talent_in_accounting}/{mate.talent_in_battle}",
        }

        # make text from dict
        text = self.__dict_2_txt(dict)

        # get ship image
        ship_image = sAssetMgr.images['ships']['carrack']

        MyPanelWindow(
            rect=pygame.Rect((59, 12), (350, 400)),
            ui_manager=self.mgr,
            text=text,
            image=ship_image,
        )




    def __show_mate_info_menu(self):
        mate_mgr = self.client.game.graphics.model.role.mate_mgr

        option_2_callback = {
        }

        for id, mate in mate_mgr.id_2_mate.items():
            option_2_callback[mate.name] = partial(self.__show_one_mate_states, mate_mgr.get_mate(id))

        self.__make_menu(option_2_callback)

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
            'Mate Info': partial(self.__show_mate_info_menu),
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )


    def show_ships_menu(self):
        option_2_callback = {
            'Fleet Info': '',
            'Ship Info': partial(self.__show_ship_info_menu),
            'Swap Ships': '',
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )