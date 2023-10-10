import pygame_gui
import pygame


from dialogs.login_dialog import LoginDialog
from dialogs.create_account_dialog import CreateAccountDialog


class Gui:
    def __init__(self, client):
        self.client = client

        self.mgr = pygame_gui.UIManager((800, 600), '../../data/fonts/font_theme.json')

        self.login_diglog = LoginDialog(self.mgr, client)

    def process_event(self, event):
        self.mgr.process_events(event)

        # when button clicked
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            try:
                event.ui_element.on_click()
            except:
                pass

        # when menu item chosen
        if event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            # call corresponding func
            event.ui_element.option_2_callback[event.text]()

    def update(self, time_delta):
        self.mgr.update(time_delta)

    def draw(self, window_surface):
        self.mgr.draw_ui(window_surface)