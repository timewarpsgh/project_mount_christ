import math



class Ship:
    def __init__(self, x, y, dir):
        self.x = x
        self.y = y
        self.dir = dir

    def __is_angel_in_range(self, angle, angel_range):
        if angle >= angel_range[0] and angle <= angel_range[1]:
            return True
        else:
            return False

    def is_target_in_angle(self, ship):
        # get angle between the ships
        angle = math.atan2(ship.y - self.y, ship.x - self.x)
        angle = math.degrees(angle)
        angle_0 = angle
        angle_1 = angle - 360
        angle_2 = angle + 360
        print(angle_0, angle_1, angle_2)


        # get angel range based on self.dir
        dir_angel = 90 - self.dir * 45
        angle_range_low = [dir_angel - 45 - 90, dir_angel - 45]  # 90 degrees
        angle_range_high = [dir_angel + 45, dir_angel + 45 + 90]  # 90 degrees

        print(f'dir_angel: {dir_angel}')
        print(f'angle_range_low: {angle_range_low}')
        print(f'angle_range_high: {angle_range_high}')


        if self.__is_angel_in_range(angle_0, angle_range_low) or \
                self.__is_angel_in_range(angle_0, angle_range_high):
            return True

        if self.__is_angel_in_range(angle_1, angle_range_low) or \
                self.__is_angel_in_range(angle_1, angle_range_high):
            return True

        if self.__is_angel_in_range(angle_2, angle_range_low) or \
                self.__is_angel_in_range(angle_2, angle_range_high):
            return True

        return False

def main():
    ship1 = Ship(0, 0, 3)
    ship2 = Ship(5, -2, 0)

    res = ship1.is_target_in_angle(ship2)
    print(res)


if __name__ == '__main__':
    main()
