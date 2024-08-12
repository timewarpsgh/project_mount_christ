import pygame_gui
import pygame
from functools import partial
from pygame_gui._constants import UI_TEXT_ENTRY_FINISHED

import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')


from login_pb2 import *


class ChatDialog(pygame_gui.windows.UIConsoleWindow):

    def __init__(self, mgr, client):
        self.mgr = mgr
        self.client = client
        super().__init__(
            rect=pygame.rect.Rect((60, 280), (400, 200)),
            manager=mgr)


    def process_event(self, event: pygame.event.Event) -> bool:
        if event.type == UI_TEXT_ENTRY_FINISHED and event.ui_element == self.command_entry:
            text = self.command_entry.get_text()
            print(text)

            packet = Chat(
                chat_type=ChatType.SAY,
                text=text
            )

            self.client.send(packet)



        super().process_event(event)


    def add_chat(self, chat_type, origin_name, text):
        if chat_type == ChatType.SAY:
            chat_type_str = 'says'

        self.add_output_line_to_log(
            f'{origin_name} {chat_type_str} {text}',
            is_bold=True,
            remove_line_break=False,
            escape_html=True
        )
