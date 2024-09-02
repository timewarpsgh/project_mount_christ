def main():
    dirs = 8

    for dir in range(dirs):
        dir_angel = 90 - dir * 45

        angle_range_low = [dir_angel - 45 - 90, dir_angel - 45]
        angle_range_high = [dir_angel + 45, dir_angel + 45 + 90]

        print(f'dir {dir} dir_angel:  {dir_angel}    {angle_range_low}  {angle_range_high}')




if __name__ == '__main__':
    main()