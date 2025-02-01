import pygame_gui
import pygame
from functools import partial

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared', 'packets'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from login_pb2 import *
from my_ui_elements import MyButton
from translator import sTr, tr

class PacketParamsDialog:

    def __init__(self, mgr, client, params_names, packet):
        self.mgr = mgr
        self.client = client

        self.params_names = params_names
        self.packet = packet

        # add ui window

        height = len(params_names) * 40 + 40 * 2
        width = 180

        ui_window = pygame_gui.elements.UIWindow(
            rect=pygame.Rect((100, 200), (width, height)),
            manager=self.mgr,
        )

        # add panel
        panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((0, 0), (width, height)),
            manager=self.mgr,
            container=ui_window,
        )

        # for each param
        index = 0
        for i, param_name in enumerate(params_names):
            # add entry box
            entry_box = pygame_gui.elements.UITextEntryBox(
                relative_rect=pygame.Rect((0, 40 * i), (140, 40)),
                placeholder_text=tr(param_name),
                manager=self.mgr,
                container=panel,
            )
            entry_box.focus()

            if len(params_names) >= 2:
                entry_box.unfocus()

            setattr(self, param_name, entry_box)


            index += 1

        # add buttion to manager
        self.ok_button = MyButton(
            relative_rect=pygame.Rect((0, 40 * index), (100, 40)),
            text='OK',
            manager=self.mgr,
            container=panel,
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


