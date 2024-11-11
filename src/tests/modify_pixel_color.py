import cv2
import numpy as np

def modify_pixel_color(image_path, target_color, new_color, output_path):
    image = cv2.imread(image_path)
    height, width, _ = image.shape

    # Convert target and new colors to numpy arrays
    target_color = np.array(target_color)
    new_color = np.array(new_color)

    for y in range(height):
        for x in range(width):
            if np.array_equal(image[y, x], target_color):
                image[y, x] = new_color

    cv2.imwrite(output_path, image)

# Example usage
image_path = r'D:\data\code\python\project_mount_christ\data\imgs\world_map\day.png'
target_color = [97, 178, 0]  # Red color
new_color = [29, 230, 181]     # Green color
output_path = r'D:\data\code\python\project_mount_christ\data\imgs\world_map\day_modified.png'

modify_pixel_color(image_path, target_color, new_color, output_path)