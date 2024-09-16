import pygame_gui
import pygame
from functools import partial

import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\client\dialogs')

from login_pb2 import *
from my_ui_elements import MyButton


class PacketParamsDialog:

    def __init__(self, mgr, client, params_names, packet):
        self.mgr = mgr
        self.client = client

        self.params_names = params_names
        self.packet = packet

        # add ui window
        self.ui_window = pygame_gui.elements.UIWindow(
            rect=pygame.Rect((0, 0), (300, 300)),
            manager=self.mgr,
        )

        # for each param
        index = 0
        for i, param_name in enumerate(params_names):
            # add entry box
            entry_box = pygame_gui.elements.UITextEntryBox(
                relative_rect=pygame.Rect((0, 50 * (i + 1)), (100, 50)),
                placeholder_text=param_name,
                manager=self.mgr,
                container=self.ui_window,
            )
            entry_box.focus()
            entry_box.unfocus()

            setattr(self, param_name, entry_box)


            index += 1

        # add buttion to manager
        self.ok_button = MyButton(
            relative_rect=pygame.Rect((0, 50 * (index + 1)), (100, 50)),
            text='OK',
            manager=self.mgr,
            container=self.ui_window,
            on_click=partial(self.__send_packet),
        )

    def __send_packet(self):
        for param in self.params_names:
            entry_box = getattr(self, param)
            text = entry_box.get_text()
            if text.isdigit():
                entered_value = int(text)
            else:
                entered_value = text
            print(f'{param}: {entered_value}')
            setattr(self.packet, param, entered_value)


        self.client.send(self.packet)


