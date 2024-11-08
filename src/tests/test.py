def item_img_id_2_xy(img_id):
    cols = 16
    rows = 8

    img_x = (img_id % cols) + 1
    img_y = (img_id // cols) + 1

    return img_x, img_y

# Example usage
img_id = 96
print(item_img_id_2_xy(img_id))  # Output: (1, 1)