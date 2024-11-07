from PIL import Image
import os

def resize_images(input_dir, output_dir, width=49, height=49):
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Iterate over each file in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            # Open the image
            img = Image.open(os.path.join(input_dir, filename))

            # Resize the image
            img = img.resize((width, height))

            # Save the resized image to the output directory
            img.save(os.path.join(output_dir, filename))

# Example usage
resize_images(r'C:\Users\陈林\Downloads\mid', r'C:\Users\陈林\Downloads\new_items')