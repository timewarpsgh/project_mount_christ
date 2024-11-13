import cv2
import numpy as np


def make_image_dimmer(image_path, output_path, dim_factor=0.5):
    # Read the image
    image = cv2.imread(image_path)

    # Ensure the dim factor is between 0 and 1
    dim_factor = np.clip(dim_factor, 0, 1)

    # Apply the dim factor to the image
    dimmed_image = (image * dim_factor).astype(np.uint8)

    # Save the dimmed image
    cv2.imwrite(output_path, dimmed_image)


# Example usage
image_path = r'D:\data\code\python\project_mount_christ\data\imgs\my_ports\map_test.png'
output_path = r'D:\data\code\python\project_mount_christ\data\imgs\my_ports\map_test_dimmed.png'
make_image_dimmer(image_path, output_path, dim_factor=0.4)