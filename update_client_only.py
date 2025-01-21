import os
import shutil


def sync_files_if_exist_in_both(dir_a, dir_b):
    """
    Recursively sync files from dir_a to dir_b only if the file exists in both dir_a and dir_b at the same location.

    :param dir_a: The source directory.
    :param dir_b: The target directory.
    """
    for root, dirs, files in os.walk(dir_a):
        # Calculate the relative path from the base of dir_a
        relative_path = os.path.relpath(root, dir_a)
        # Construct the corresponding directory in dir_b
        target_dir = os.path.join(dir_b, relative_path)

        # Check if the corresponding directory exists in dir_b
        if not os.path.exists(target_dir):
            continue  # Skip syncing if the target directory doesn't exist

        # Sync files only if they exist in both dir_a and dir_b
        for file_name in files:
            src_file = os.path.join(root, file_name)
            dst_file = os.path.join(target_dir, file_name)

            if os.path.exists(dst_file):
                # Copy the file from dir_a to dir_b
                shutil.copy2(src_file, dst_file)
                print(f"Syncing {src_file} to {dst_file}")
            else:
                print(f"File {dst_file} does not exist in dir_b, skipping.")

def main():
    dir_a = r'D:\data\code\python\project_mount_christ'
    dir_b = r'D:\data\code\python\client_only'
    sync_files_if_exist_in_both(dir_a, dir_b)


if __name__ == '__main__':
    main()
