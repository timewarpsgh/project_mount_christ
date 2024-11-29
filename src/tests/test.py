import os
from PIL import Image


def combine_images_in_folder(folder_path):
    # Define the size of each small image
    small_image_size = (75, 91)

    # Define the number of rows and columns
    rows, cols = 8, 16

    # Create a new blank image with the appropriate size
    big_image = Image.new('RGB', (cols * small_image_size[0], rows * small_image_size[1]))

    # Iterate over the small images
    for i in range(rows * cols):
        filename = f'{i}.jpeg'
        file_path = os.path.join(folder_path, filename)

        if os.path.exists(file_path):
            # Open the small image
            with Image.open(file_path) as img:
                # Calculate the position to paste the small image
                x = (i % cols) * small_image_size[0]
                y = (i // cols) * small_image_size[1]

                # Paste the small image into the big image
                big_image.paste(img, (x, y))

    # Save the big image
    big_image.save(os.path.join(folder_path, 'big_image.png'))


# Example usage
combine_images_in_folder(r'D:\data\code\python\project_mount_christ\data\imgs\figures\new_figures_75x91')