import pygame_gui
import pygame
import os
from dialogs.login_dialog import LoginDialog
from dialogs.create_account_dialog import CreateAccountDialog

class Gui:
    def __init__(self, client):
        self.client = client

        font_theme_path =  os.getcwd() + '/' + r'../../data/fonts/font_theme.json'

        self.mgr = pygame_gui.UIManager(
            (800, 600),
            font_theme_path,
        )

        self.login_diglog = LoginDialog(self.mgr, client)
        self.options_dialog = None
        self.chat_dialog = None

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
            if not hasattr(event.ui_element, 'option_2_callback'):
                return

            # for testing force exit (click msc in buildings)
            if not event.ui_element.option_2_callback[event.text]:
                return

            # call corresponding func
            event.ui_element.option_2_callback[event.text]()

        # esc pressed
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if not self.options_dialog:
                    return
                self.options_dialog.pop_some_menus(cnt=1)


    def update(self, time_delta):
        self.mgr.update(time_delta)

    def draw(self, window_surface):
        self.mgr.draw_ui(window_surface)