import pygame_gui
import pygame


from dialogs.login_dialog import LoginDialog
from dialogs.create_account_dialog import CreateAccountDialog


class Gui:
    def __init__(self, client):
        self.client = client

        self.mgr = pygame_gui.UIManager((800, 600), '../../data/fonts/font_theme.json')

        self.login_diglog = LoginDialog(self.mgr, client)
        self.create_account_dialog = CreateAccountDialog(self.mgr, client)

    def process_event(self, event):
        self.mgr.process_events(event)

        self.login_diglog.process_event(event)
        self.create_account_dialog.process_event(event)

    def update(self, time_delta):
        self.mgr.update(time_delta)

    def draw(self, window_surface):
        self.mgr.draw_ui(window_surface)