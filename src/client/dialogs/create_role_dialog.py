import random

import pygame_gui
import pygame
from functools import partial

import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\client')

from login_pb2 import *
from my_ui_elements import MyButton, MyMsgWindow, MyPanelWindow
import constants as c
from asset_mgr import sAssetMgr
from translator import sTr, tr


def figure_x_y_2_image(x=8, y=8):
    figure_width = c.FIGURE_WIDTH
    figure_height = c.FIGURE_HEIGHT

    figures_image = sAssetMgr.images['figures']['figures']


    figure_surface = pygame.Surface((figure_width, figure_height))
    x_coord = -figure_width * (x - 1)
    y_coord = -figure_height * (y - 1)
    rect = pygame.Rect(x_coord, y_coord, figure_width, figure_height)
    figure_surface.blit(figures_image, rect)

    return figure_surface


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
        height = c.LOGIN_WINDOW_HEIGHT * 1.6
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

        # name
        self.entry_box_role_name = pygame_gui.elements.UITextEntryBox(
            relative_rect=pygame.Rect((0, 50), (100, 50)),
            initial_text='角色名',
            manager=self.mgr,
            container=panel,
        )

        # nation
        self.nation_menu = pygame_gui.elements.UIDropDownMenu(
            options_list=[tr(nation.name) for nation in c.Nation],
            starting_option=tr(c.Nation.ENGLAND.name),
            relative_rect=pygame.Rect((0, 100), (130, 50)),
            manager=self.mgr,
            container=panel
        )

        # talents
        self.__add_talent_buttons(panel)

        # img
        self.img_x = 2
        self.img_y = 2
        image = figure_x_y_2_image(self.img_x, self.img_y)
        self.figure_img = pygame_gui.elements.UIImage(
            pygame.Rect((0, 250), (image.get_rect().size)),
            image,
            self.mgr,
            container=panel
        )

        # randomize button
        self.login_button = MyButton(
            relative_rect=pygame.Rect((80, 260), (100, 50)),
            text=tr('Randomize'),
            manager=self.mgr,
            container=panel,
            on_click=partial(self.__randomize_img),
        )

    def __randomize_img(self):
        self.img_x = random.randint(1, 16)
        self.img_y = random.randint(1, 8)

        self.figure_img.set_image(figure_x_y_2_image(self.img_x, self.img_y))

    def __add_talent_buttons(self, panel):

        text_box_width = 160

        # points
        self.points_label = pygame_gui.elements.UITextBox(
            html_text=f'{tr("Points")}: {self.points}',
            relative_rect=pygame.Rect((0, 160), (text_box_width, 20)),
            manager=self.mgr,
            wrap_to_height=True,
            container=panel
        )

        MyButton(
            relative_rect=pygame.Rect((150, 160), (70, 20)),
            text=tr('Reset'),
            manager=self.mgr,
            container=panel,
            on_click=partial(self.__reset_points),
        )

        # Talent in navigation
        label_width = 150
        self.nav_label = pygame_gui.elements.UITextBox(
            html_text=f'{tr("Talent in nav")}: {self.talent_in_nav}',
            relative_rect=pygame.Rect((0, 180), (text_box_width, 20)),
            manager=self.mgr,
            wrap_to_height=True,
            container=panel
        )

        MyButton(
            relative_rect=pygame.Rect((label_width + 20, 180), (40, 20)),
            text='+',
            manager=self.mgr,
            container=panel,
            on_click=partial(self.__add_nav),
        )

        # Talent in accounting
        self.acc_label = pygame_gui.elements.UITextBox(
            html_text=f'{tr("Talent in acc")}: {self.talent_in_acc}',
            relative_rect=pygame.Rect((0, 200), (text_box_width, 20)),
            manager=self.mgr,
            wrap_to_height=True,
            container=panel
        )

        MyButton(
            relative_rect=pygame.Rect((label_width + 20, 200), (40, 20)),
            text='+',
            manager=self.mgr,
            container=panel,
            on_click=partial(self.__add_acc),
        )

        # Talent in battle
        self.bat_label = pygame_gui.elements.UITextBox(
            html_text=f'{tr("Talent in bat")}: {self.talent_in_bat}',
            relative_rect=pygame.Rect((0, 220), (text_box_width, 20)),
            manager=self.mgr,
            wrap_to_height=True,
            container=panel
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
        self.nav_label.set_text(f'{tr("Talent in nav")}: {self.talent_in_nav}')

        self.points -= 1
        self.points_label.set_text(f'{tr("Points")}: {self.points}')

    def __add_acc(self):
        if self.points <= 0:
            return

        self.talent_in_acc += 1
        self.acc_label.set_text(f'{tr("Talent in acc")}: {self.talent_in_acc}')

        self.points -= 1
        self.points_label.set_text(f'{tr("Points")}: {self.points}')

    def __add_bat(self):
        if self.points <= 0:
            return

        self.talent_in_bat += 1
        self.bat_label.set_text(f'{tr("Talent in bat")}: {self.talent_in_bat}')

        self.points -= 1
        self.points_label.set_text(f'{tr("Points")}: {self.points}')

    def __reset_points(self):
        self.points = 3
        self.points_label.set_text(f'{tr("Points")}: {self.points}')

        self.talent_in_nav = 0
        self.nav_label.set_text(f'{tr("Talent in nav")}: {self.talent_in_nav}')

        self.talent_in_acc = 0
        self.acc_label.set_text(f'{tr("Talent in acc")}: {self.talent_in_acc}')

        self.talent_in_bat = 0
        self.bat_label.set_text(f'{tr("Talent in bat")}: {self.talent_in_bat}')

    def __get_nation_id(self):
        nation_names = [tr(nation.name) for nation in c.Nation]
        for id, name in enumerate(nation_names):
            if name == self.nation_menu.selected_option:
                nation_id = id + 1
                return nation_id

    def __create_role(self):
        if self.points > 0:
            # message box
            MyMsgWindow(tr('Please spend all points'), self.mgr)

            return


        print(f'send __create_role packet for {self.world_id=}')
        new_role = NewRole()
        new_role.world_id = self.world_id
        new_role.name = self.entry_box_role_name.get_text()
        new_role.nation = self.__get_nation_id()
        new_role.talent_in_nav = self.talent_in_nav
        new_role.talent_in_acc = self.talent_in_acc
        new_role.talent_in_bat = self.talent_in_bat
        new_role.img_id = f'{self.img_x}_{self.img_y}'
        self.client.send(new_role)


