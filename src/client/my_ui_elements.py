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