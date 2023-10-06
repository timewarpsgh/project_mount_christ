import pygame_gui
import pygame


class LoginDialog:

    def __init__(self, mgr, client):
        self.mgr = mgr
        self.client = client

        # add ui window
        self.ui_window = pygame_gui.elements.UIWindow(
            rect=pygame.Rect((0, 0), (300, 300)),
            manager=self.mgr,
        )

        # add buttion to manager
        self.login_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, 0), (100, 50)),
            text='登录',
            manager=self.mgr,
            container=self.ui_window,
        )

        # add entry box
        self.entry_box_account = pygame_gui.elements.UITextEntryBox(
            relative_rect=pygame.Rect((0, 50), (100, 50)),
            initial_text='账号',
            manager=self.mgr,
            container=self.ui_window,
        )

        # add entry box
        self.entry_box_password = pygame_gui.elements.UITextEntryBox(
            relative_rect=pygame.Rect((0, 100), (100, 50)),
            initial_text='密码',
            manager=self.mgr,
            container=self.ui_window,
        )

    def process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.login_button:
                print(f'account: {self.entry_box_account.get_text()}')
                print(f'password: {self.entry_box_password.get_text()}')
