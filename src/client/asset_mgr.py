import pygame
import os

def load_images_in_dir(dict, path_to_dir, accept=('.png', '.jpg', '.bmp', '.gif')):
    """loads all imgs in dir into dict"""
    for pic in os.listdir(path_to_dir):
        name, ext = os.path.splitext(pic)
        if ext.lower() in accept:
            img = pygame.image.load(os.path.join(path_to_dir, pic))
            img = img.convert_alpha()
            dict[name] = img

def load_sounds_in_dir(sounds_container, directory, accept=('.ogg')):
    """loads all imgs in dir into image_contrainer"""
    for sound in os.listdir(directory):
        name, ext = os.path.splitext(sound)
        if ext.lower() in accept:
            sounds_container[name] = pygame.mixer.Sound(os.path.join(directory, sound))


class AssetMgr:
    def __init__(self):
        self.images = {}
        self.sounds = {}

    def load_images(self):
        self.images['ships'] = {}

        path_to_ships_imgs = r"D:\data\code\python\project_mount_christ\data\imgs\ships"
        load_images_in_dir(self.images['ships'], path_to_ships_imgs)

        self.images['figures'] = {}
        path_to_figures_imgs = r"D:\data\code\python\project_mount_christ\data\imgs\figures"
        load_images_in_dir(self.images['figures'], path_to_figures_imgs)

        self.images['discoveries_and_items'] = {}
        path_to_discoveries_and_items_imgs = r"D:\data\code\python\project_mount_christ\data\imgs\discoveries_and_items"
        load_images_in_dir(self.images['discoveries_and_items'], path_to_discoveries_and_items_imgs)

    def load_sounds(self):
        load_sounds_in_dir(self.sounds, f"D:\data\code\python\project_mount_christ\data\sounds\effect")



sAssetMgr = AssetMgr()