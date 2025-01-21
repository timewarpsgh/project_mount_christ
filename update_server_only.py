from update_client_only import sync_files_if_exist_in_both

def main():
    dir_a = r'D:\data\code\python\project_mount_christ'
    dir_b = r'D:\data\code\python\server_only'
    sync_files_if_exist_in_both(dir_a, dir_b)


if __name__ == '__main__':
    main()
