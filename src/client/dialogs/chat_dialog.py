import pygame_gui
import pygame
from functools import partial



class ChatDialog:

    def __init__(self, mgr, client):
        self.mgr = mgr
        self.client = client
        self.ui_window = pygame_gui.windows.UIConsoleWindow(
            rect=pygame.rect.Rect((60, 280), (400, 200)),
            manager=mgr)
