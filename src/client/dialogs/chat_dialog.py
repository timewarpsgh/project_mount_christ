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

            # whisper
            if text.startswith('/w'):
                split_items = text.split(' ')
                target_role_name = split_items[1]
                msg = ' '.join(split_items[2:])

                pack = Chat(
                    chat_type=ChatType.WHISPER,
                    text=msg,
                    whisper_target_name=target_role_name,
                )

            # nation
            elif text.startswith('/n'):
                split_items = text.split(' ')
                msg = ' '.join(split_items[1:])

                pack = Chat(
                    chat_type=ChatType.NATION,
                    text=msg,
                )

            # say
            else:
                pack = Chat(
                    chat_type=ChatType.SAY,
                    text=text
                )

            self.client.send(pack)

            self.command_entry.unfocus()

        # call super
        super().process_event(event)


    def add_chat(self, chat_type, text, origin_name=None, whisper_target_name=None):
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

        elif chat_type == ChatType.WHISPER:
            if origin_name == self.client.game.graphics.model.role.name:
                self.add_output_line_to_log(
                    f'You whispered to {whisper_target_name}: {text}',
                    is_bold=False,
                    remove_line_break=False,
                    escape_html=True
                )
            else:
                self.add_output_line_to_log(
                    f'{origin_name} whispers: {text}',
                    is_bold=False,
                    remove_line_break=False,
                    escape_html=True
                )
