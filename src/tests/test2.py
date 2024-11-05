import os

def detect_missing_images(input_dir, total_images=128):
    missing_images = []
    for i in range(total_images):
        filename = f"{i}.jpeg"
        img_path = os.path.join(input_dir, filename)
        if not os.path.exists(img_path):
            missing_images.append(filename)
    return missing_images

# Example usage
missing_images = detect_missing_images(r'C:\Users\陈林\Downloads\test_output')
print("Missing images:", missing_images)
