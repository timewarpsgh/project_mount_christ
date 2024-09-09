import pygame
import pygame_gui

import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\client\dialogs')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\client')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared')

import constants as c

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
        msg_windows = pygame_gui.windows.ui_message_window.UIMessageWindow(
            rect=pygame.Rect((0, 300), (250, 160)),
            manager=mgr,
            window_title='',
            html_message=msg,
        )

        msg_windows.dismiss_button.set_text('OK')


class MyMenuWindow:

    def __init__(self, title, option_2_callback, mgr):

        len_of_options = len(option_2_callback)
        if len_of_options <= 2:
            len_of_options = 3

        height = len_of_options * 20 + 40

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
            relative_rect=pygame.Rect((0, 0), (245, height)),
            manager=mgr,
            container=panel,
        )

        worlds_menu.option_2_callback = option_2_callback

        # only_show_top_window(mgr)

class MyButton:

    def __init__(self, relative_rect, text, manager, container, on_click):
        button = pygame_gui.elements.UIButton(
            relative_rect=relative_rect,
            text=text,
            manager=manager,
            container=container,
        )

        button.on_click = on_click

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
                relative_rect=pygame.Rect(0, y, 320, 10), #pygame.Rect(0, image.get_rect().height, 320, 10)
                manager=ui_manager,
                wrap_to_height=True,
                container=panel)

