import pygame
import pygame_gui

pygame.init()

pygame.display.set_caption('Quick Start')

window_surface = pygame.display.set_mode((800, 600))

background = pygame.Surface((800, 600))
background.fill(pygame.Color('#550000'))

# init manager
manager = pygame_gui.UIManager((800, 600), '../../data/fonts/font_theme.json')

# add ui window to
ui_window = pygame_gui.elements.UIWindow(
    rect=pygame.Rect((0, 0), (300, 300)),
    manager=manager,
)

# add buttion to manager
hello_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((0, 0), (100, 50)),
    text='登录',
    manager=manager,
    container=ui_window,
)

# add entry box
entry_box_account = pygame_gui.elements.UITextEntryBox(
    relative_rect=pygame.Rect((0, 50), (100, 50)),
    initial_text='账号',
    manager=manager,
    container=ui_window,
)

# add entry box
entry_box_password = pygame_gui.elements.UITextEntryBox(
    relative_rect=pygame.Rect((0, 100), (100, 50)),
    initial_text='密码',
    manager=manager,
    container=ui_window,
)


clock = pygame.time.Clock()
is_running = True

while is_running:

    # get time_delta
    time_delta = clock.tick(60) / 1000.0

    # update
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == hello_button:
                print(f'entry_box_account: {entry_box_account.get_text()}')
                print(f'entry_box_account: {entry_box_password.get_text()}')

        manager.process_events(event)

    manager.update(time_delta)

    # draw
    window_surface.blit(background, (0, 0))
    manager.draw_ui(window_surface)

    # flip
    pygame.display.update()