import pygame

pygame.init()
window = pygame.display.set_mode((400, 300))
clock = pygame.time.Clock()

background = pygame.Surface((window.get_width()+200, window.get_height()))
ts, w, h, c1, c2 = 100, *background.get_size(), (64, 64, 64), (127, 64, 64)
tiles = [((x*ts, y*ts, ts, ts), c1 if (x+y) % 2 == 0 else c2) for x in range((w+ts-1)//ts) for y in range((h+ts-1)//ts)]
for rect, color in tiles:
    pygame.draw.rect(background, color, rect)

var_x, var_bounce, speed_x = 0, 0, 4

def scroll():
    global var_x, var_bounce
    if var_bounce == 0:
        if var_x > -200:
            var_x = var_x - speed_x
        else:
            var_bounce = 1
    elif var_bounce == 1:
        if var_x < 0:
            var_x = var_x + speed_x
        else:
            var_bounce = 0

run = False
while not run:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = True

    scroll()

    window.blit(background, (var_x, 0))
    pygame.display.flip()

pygame.quit()
exit()
