import pygame_gui
import pygame
from functools import partial

import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared')

from login_pb2 import *
from my_ui_elements import MyButton, MyMsgWindow
import constants as c


class CreateRoleDialog:

    def __init__(self, mgr, client, world_id):
        self.mgr = mgr
        self.client = client
        self.world_id = world_id

        self.points = 3
        self.talent_in_nav = 0
        self.talent_in_acc = 0
        self.talent_in_bat = 0


        # add ui window
        width = c.LOGIN_WINDOW_WIDTH
        height = c.LOGIN_WINDOW_HEIGHT * 1.5
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

        self.nation_menu = pygame_gui.elements.UIDropDownMenu(
            options_list=[nation.name for nation in c.Nation],
            starting_option=c.Nation.ENGLAND.name,
            relative_rect=pygame.Rect((0, 100), (130, 50)),
            manager=self.mgr,
            container=panel)

        # points
        self.points_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, 160), (150, 20)),
            text=f'Points: {self.points}',
            manager=self.mgr,
            container=panel,
        )

        MyButton(
            relative_rect=pygame.Rect((150, 160), (70, 20)),
            text='Reset',
            manager=self.mgr,
            container=panel,
            on_click=partial(self.__reset_points),
        )

        # Talent in navigation
        label_width = 150

        self.nav_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, 180), (label_width, 20)),
            text=f'Talent in nav: {self.talent_in_nav}',
            manager=self.mgr,
            container=panel,
        )

        MyButton(
            relative_rect=pygame.Rect((label_width + 20, 180), (40, 20)),
            text='+',
            manager=self.mgr,
            container=panel,
            on_click=partial(self.__add_nav),
        )

        # Talent in accounting
        self.acc_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, 200), (label_width, 20)),
            text=f'Talent in acc: {self.talent_in_acc}',
            manager=self.mgr,
            container=panel,
        )

        MyButton(
            relative_rect=pygame.Rect((label_width + 20, 200), (40, 20)),
            text='+',
            manager=self.mgr,
            container=panel,
            on_click=partial(self.__add_acc),
        )

        # Talent in battle
        self.bat_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, 220), (label_width, 20)),
            text=f'Talent in bat: {self.talent_in_bat}',
            manager=self.mgr,
            container=panel,
        )

        MyButton(
            relative_rect=pygame.Rect((label_width + 20, 220), (40, 20)),
            text='+',
            manager=self.mgr,
            container=panel,
            on_click=partial(self.__add_bat),
        )

    def __add_nav(self):
        if self.points <= 0:
            return

        self.talent_in_nav += 1
        self.nav_label.set_text(f'Talent in nav: {self.talent_in_nav}')

        self.points -= 1
        self.points_label.set_text(f'Points: {self.points}')

    def __add_acc(self):
        if self.points <= 0:
            return

        self.talent_in_acc += 1
        self.acc_label.set_text(f'Talent in acc: {self.talent_in_acc}')

        self.points -= 1
        self.points_label.set_text(f'Points: {self.points}')

    def __add_bat(self):
        if self.points <= 0:
            return

        self.talent_in_bat += 1
        self.bat_label.set_text(f'Talent in bat: {self.talent_in_bat}')

        self.points -= 1
        self.points_label.set_text(f'Points: {self.points}')

    def __reset_points(self):
        self.points = 3
        self.points_label.set_text(f'Points: {self.points}')

        self.talent_in_nav = 0
        self.nav_label.set_text(f'Talent in nav: {self.talent_in_nav}')

        self.talent_in_acc = 0
        self.acc_label.set_text(f'Talent in acc: {self.talent_in_acc}')

        self.talent_in_bat = 0
        self.bat_label.set_text(f'Talent in bat: {self.talent_in_bat}')

    def __create_role(self):
        if self.points > 0:
            # message box
            MyMsgWindow('Please spend all points', self.mgr)

            return


        print(f'send __create_role packet for {self.world_id=}')
        new_role = NewRole()

        new_role.world_id = self.world_id

        new_role.name = self.entry_box_role_name.get_text()
        new_role.nation = c.Nation[self.nation_menu.selected_option].value
        new_role.talent_in_nav = self.talent_in_nav
        new_role.talent_in_acc = self.talent_in_acc
        new_role.talent_in_bat = self.talent_in_bat
        new_role.img_id = '1_2'

        self.client.send(new_role)


