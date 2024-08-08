import pygame
import pygame_gui


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
        ui_window = pygame_gui.elements.UIWindow(
            rect=pygame.Rect((0, 0), (300, 300)),
            manager=mgr,
            window_display_title=title,
        )

        worlds_menu = pygame_gui.elements.UISelectionList(
            item_list=list(option_2_callback.keys()),
            relative_rect=pygame.Rect((0, 0), (265, 300)),
            manager=mgr,
            container=ui_window,
        )

        worlds_menu.option_2_callback = option_2_callback


class MyButton:

    def __init__(self, relative_rect, text, manager, container, on_click):
        button = pygame_gui.elements.UIButton(
            relative_rect=relative_rect,
            text=text,
            manager=manager,
            container=container,
        )

        button.on_click = on_click

class MyPanelWindow(pygame_gui.elements.UIWindow):
    """displays info"""
    def __init__(self, rect, ui_manager, text, image='none'):

        # super
        super().__init__(rect, ui_manager,
                         window_display_title='',
                         object_id='#scaling_window',
                         resizable=True)


        # image
        if image:
            pygame_gui.elements.UIImage(
                pygame.Rect((0, 0), (image.get_rect().size)),
                image,
                ui_manager,
                container=self,
                anchors={'top': 'top', 'bottom': 'bottom',
                       'left': 'left', 'right': 'right'})

        # text box
        if text:
            pygame_gui.elements.UITextBox(
                html_text=text,
                relative_rect=pygame.Rect(0, image.get_rect().height, 320, 10), #pygame.Rect(0, image.get_rect().height, 320, 10)
                manager=ui_manager,
                wrap_to_height=True,
                container=self)

