import pygame
pygame.init()

# Load the font
font_path = r'D:\data\code\python\project_mount_christ\data\fonts\siyuanheiti.ttf'
font_size = 36
try:
    font = pygame.font.Font(font_path, font_size)
except IOError as e:
    print(f"Error loading font: {e}")
    # Handle the error, e.g., use a default font or exit the program
