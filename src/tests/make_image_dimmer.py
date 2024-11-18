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


def dim_port_image(port_id):
    image_path = f'D:\data\code\python\project_mount_christ\data\imgs\my_ports\\{port_id}\\day.png'
    output_path = f'D:\data\code\python\project_mount_christ\data\imgs\my_ports\\{port_id}\\day_dimmed.png'
    make_image_dimmer(image_path, output_path, dim_factor=0.4)


def main():
    port_id = 32
    dim_port_image(port_id)


if __name__ == '__main__':
    main()