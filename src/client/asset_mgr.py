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


class AssetMgr:
    def __init__(self):
        self.images = {}
        self.sounds = {}

    def load_images(self):
        self.images['ships'] = {}

        path_to_ships_imgs = r"D:\data\code\python\project_mount_christ\data\imgs\ships"
        load_images_in_dir(self.images['ships'], path_to_ships_imgs)


sAssetMgr = AssetMgr()