import pygame
import pygame_gui

import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\client\dialogs')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\client')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared')

import constants as c
from translator import sTr, tr

def only_show_top_window(mgr):

    stacked_windows = mgr.get_window_stack().get_stack()

    length = len(stacked_windows)
    for i, window in enumerate(stacked_windows):
        if i in [0, 1, length - 1]:
            window.show()
        else:
            window.hide()


class MyMsgWindow:

    def __init__(self, msg, mgr):
        MyPanelWindow(rect=pygame.Rect((0, 300), (250, 160)),
                      ui_manager=mgr,
                      text=msg)


class MyMenuWindow:

    def __init__(self, title, option_2_callback, mgr):

        len_of_options = len(option_2_callback)
        if len_of_options <= 2:
            len_of_options = 3

        if len_of_options >= 14:
            len_of_options = 14

        height = len_of_options * 20 + 70

        ui_window = pygame_gui.elements.UIWindow(
            rect=pygame.Rect((c.WINDOW_WIDTH - 265, 120), (280, height)),
            manager=mgr,
            window_display_title=title,
        )

        panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((0, 0), (250, height)),
            manager=mgr,
            container=ui_window,
        )


        worlds_menu = pygame_gui.elements.UISelectionList(
            item_list=list(option_2_callback.keys()),
            relative_rect=pygame.Rect((0, 0), (245, height+30)),
            manager=mgr,
            container=panel,
        )

        worlds_menu.option_2_callback = option_2_callback

        only_show_top_window(mgr)

class MyButton:

    def __init__(self, relative_rect, text, manager, container, on_click):
        self.button = pygame_gui.elements.UIButton(
            relative_rect=relative_rect,
            text=text,
            manager=manager,
            container=container,
        )

        self.button.on_click = on_click

class MyPanelWindow():
    """displays info"""
    def __init__(self, rect, ui_manager, text, image=None):

        ui_window = pygame_gui.elements.UIWindow(
            rect=rect,
            manager=ui_manager,
            window_display_title='',
        )

        panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((0, 0), (rect.width, rect.height)),
            manager=ui_manager,
            container=ui_window,
        )

        # image
        if image:
            pygame_gui.elements.UIImage(
                pygame.Rect((0, 0), (image.get_rect().size)),
                image,
                ui_manager,
                container=panel,
                anchors={'top': 'top', 'bottom': 'bottom',
                       'left': 'left', 'right': 'right'})

        # text box
        if text:
            if image:
                y = image.get_rect().height
            else:
                y = 0

            pygame_gui.elements.UITextBox(
                html_text=text,
                relative_rect=pygame.Rect(-5, y, rect.width - 30, rect.height), #pygame.Rect(0, image.get_rect().height, 320, 10)
                manager=ui_manager,
                wrap_to_height=True,
                container=panel
            )


class MyFleetPanelWindow():
    def __init__(self, rect, ui_manager, ships):

        ui_window = pygame_gui.elements.UIWindow(
            rect=rect,
            manager=ui_manager,
            window_display_title='',
        )

        panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((0, 0), (rect.width, rect.height)),
            manager=ui_manager,
            container=ui_window,
        )


        # text boxes
        start_x = -50
        start_y = 0
        delta_x = 52
        delta_y = 20

        # fileds
        fields = ['name', 'dura', 'crew', 'guns',
                  'food', 'water', 'lumber', 'shot',
                  'cargo', 'speed', 'captain']
        for field in fields:
            start_x += delta_x

            pygame_gui.elements.UITextBox(
                html_text=str(tr(field)),
                relative_rect=pygame.Rect(start_x, start_y, 200, 20),
                manager=ui_manager,
                wrap_to_height=True,
                container=panel
            )

        # ships
        for ship in ships:
            start_y += delta_y
            start_x = -50
            captain = ship.get_captain()
            if captain:
                captain_name = captain.name
            else:
                captain_name = ''

            attributes = [
                ship.name, ship.now_durability, ship.now_crew, ship.now_guns,
                ship.food, ship.water, ship.material, ship.cannon,
                ship.cargo_cnt, ship.get_base_speed_in_knots(),
                tr(captain_name)
            ]

            for attribute in attributes:
                start_x += delta_x

                pygame_gui.elements.UITextBox(
                    html_text=str(attribute),
                    relative_rect=pygame.Rect(start_x, start_y, 200, 20),
                    manager=ui_manager,
                    wrap_to_height=True,
                    container=panel
                )


class MyMatePanelWindow():
    """displays info"""
    def __init__(self, rect, ui_manager, image, mate, text):

        ui_window = pygame_gui.elements.UIWindow(
            rect=rect,
            manager=ui_manager,
            window_display_title='',
        )

        panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((0, 0), (rect.width, rect.height)),
            manager=ui_manager,
            container=ui_window,
        )



        pygame_gui.elements.UIImage(
            pygame.Rect((0, 0), (image.get_rect().size)),
            image,
            ui_manager,
            container=panel,
            anchors={'top': 'top', 'bottom': 'bottom',
                   'left': 'left', 'right': 'right'})

        # text box

        if image:
            y = image.get_rect().height
        else:
            y = 0

        pygame_gui.elements.UITextBox(
            html_text=text,
            relative_rect=pygame.Rect(-5, y, rect.width - 30, rect.height), #pygame.Rect(0, image.get_rect().height, 320, 10)
            manager=ui_manager,
            wrap_to_height=True,
            container=panel
        )

        # text boxes
        lines = [
            ['', 'nav', 'acc', 'bat'],
            ['lv', mate.lv_in_nav, mate.lv_in_acc, mate.lv_in_bat],
            ['value', mate.navigation, mate.accounting, mate.battle],
            ['talent', mate.talent_in_navigation, mate.talent_in_accounting, mate.talent_in_battle],
            ['xp', mate.xp_in_nav, mate.xp_in_acc, mate.xp_in_bat],
            ['lv_up_xp', c.LV_2_MAX_XP[mate.lv_in_nav], c.LV_2_MAX_XP[mate.lv_in_acc], c.LV_2_MAX_XP[mate.lv_in_bat]]
        ]

        start_x = -60
        start_y = 150

        for line in lines:
            start_y += 20
            start_x = -60
            for attribute in line:
                start_x += 70
                pygame_gui.elements.UITextBox(
                    html_text=tr(str(attribute)),
                    relative_rect=pygame.Rect(start_x, start_y, 200, 20),
                    manager=ui_manager,
                    wrap_to_height=True,
                    container=panel
                )
