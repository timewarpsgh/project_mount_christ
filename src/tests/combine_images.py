from PIL import Image
import os

def combine_images(input_dir, output_path, sprite_width=49, sprite_height=49, rows=8, cols=16):
    # Create a new blank image with the size to hold all small images
    big_image = Image.new('RGB', (cols * sprite_width, rows * sprite_height))

    # Iterate over each file in the input directory
    for i in range(rows * cols):
        for ext in ['jpeg', 'png']:
            filename = f"{i}.{ext}"
            img_path = os.path.join(input_dir, filename)
            if os.path.exists(img_path):
                # Open the image
                img = Image.open(img_path)

                # Calculate the position to paste the image
                row = i // cols
                col = i % cols
                left = col * sprite_width
                upper = row * sprite_height

                # Paste the image into the big image
                big_image.paste(img, (left, upper))
                break

    # Save the big image to the output path
    big_image.save(output_path)

# Example usage
combine_images(r'C:\Users\陈林\Downloads\new_items', r'C:\Users\陈林\Downloads\big_image.png')