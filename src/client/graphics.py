import pygame

FONT_SIZE = 16
YELLOW = (255, 255, 0)
RED = (255, 0, 0)


class SP(pygame.sprite.Sprite):

    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.image = image
        self.rect = image.get_rect().move(x, y)

    def change_img(self, img):
        self.image = img

    def move_to(self, x, y):
        self.rect = self.image.get_rect().move(x, y)


class Graphics:

    def __init__(self, client=None, model=None):
        self.font = pygame.font.Font(r"D:\data\code\python\project_mount_christ\data\fonts\siyuanheiti.ttf", FONT_SIZE)

        # client
        self.client = client

        # model
        self.model = model

        # imgs
        self.imgs = self.__load_images()

        # sprites
        self.sprites = pygame.sprite.Group()

        self.sp_background = SP(self.imgs['background'], 0, 0)
        self.sp_role = SP(self.imgs['role'], 300, 150)
        self.sp_role_name = SP(self.font.render('name', True, YELLOW), 300, 150)
        self.sp_hud = SP(self.imgs['hud'], 0, 0)

        self.sprites.add(self.sp_background)
        self.sprites.add(self.sp_role)
        self.sprites.add(self.sp_role_name)
        self.sprites.add(self.sp_hud)

    def __load_images(self):
        imgs = {}

        imgs['background'] = self.__load_image(r'D:\data\code\python\project_mount_christ\data\imgs\port.png')
        imgs['role'] = self.__load_image(r'D:\data\code\python\project_mount_christ\data\imgs\role.png')
        imgs['hud'] = self.__load_image(r'D:\data\code\python\project_mount_christ\data\imgs\hud.png')

        return imgs

    def __load_image(self, path_to_img, set_transparent=True):
        image = pygame.image.load(path_to_img).convert()

        if set_transparent:
            colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
            return image
        else:
            return image

    def process_event(self, event):
        print(event)


    def update(self, time_delta):
        pass


    def draw(self, window_surface):
        if not self.client.packet_handler.is_in_game:
            return

        # draw objs
        self.sprites.draw(window_surface)
