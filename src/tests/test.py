from PIL import Image

def extract_sprites(sprite_sheet_path, output_folder, sprite_width=49, sprite_height=49):
    # Open the sprite sheet
    sprite_sheet = Image.open(sprite_sheet_path)
    sheet_width, sheet_height = sprite_sheet.size

    # Calculate the number of sprites in the sheet
    sprites_per_row = sheet_width // sprite_width
    sprites_per_column = sheet_height // sprite_height

    # Extract each sprite
    sprite_index = 0
    for row in range(sprites_per_column):
        for col in range(sprites_per_row):
            # Calculate the position of the sprite
            left = col * sprite_width
            upper = row * sprite_height
            right = left + sprite_width
            lower = upper + sprite_height

            # Crop the sprite
            sprite = sprite_sheet.crop((left, upper, right, lower))

            # Save the sprite as a PNG file
            sprite.save(f"{output_folder}/{sprite_index}.png", "PNG")
            sprite_index += 1

# Example usage
extract_sprites(r"C:\Users\陈林\Downloads\discoveries_and_items.png", r"C:\Users\陈林\Downloads\old_items")