import pygame_gui
import pygame
from functools import partial
import html
from pygame_gui._constants import UI_TEXT_ENTRY_FINISHED, UI_TEXT_ENTRY_CHANGED
from pygame_gui._constants import UI_CONSOLE_COMMAND_ENTERED

import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\client')

from login_pb2 import *
from my_ui_console_window import MyUIConsoleWindow

class ChatDialog(MyUIConsoleWindow):

    def __init__(self, mgr, client):
        self.mgr = mgr
        self.client = client
        super().__init__(
            rect=pygame.rect.Rect((150, 280), (400, 160)),
            manager=mgr,
            object_id='#console_window'
        )


    def process_event(self, event: pygame.event.Event) -> bool:

        # send packet
        if event.type == UI_TEXT_ENTRY_FINISHED and event.ui_element == self.command_entry:
            text = self.command_entry.get_text()
            if not text:
                return

            packet = Chat(
                chat_type=ChatType.SAY,
                text=text
            )

            self.client.send(packet)

            self.command_entry.unfocus()

        # call super
        super().process_event(event)


    def add_chat(self, chat_type, text, origin_name=None):
        if chat_type == ChatType.SAY:
            chat_type_str = 'says'

            self.add_output_line_to_log(
                f'{origin_name} {chat_type_str} {text}',
                is_bold=False,
                remove_line_break=False,
                escape_html=True
            )

        elif chat_type == ChatType.SYSTEM:
            self.add_output_line_to_log(
                f'SYSTEM {text}',
                is_bold=True,
                remove_line_break=False,
                escape_html=True
            )
