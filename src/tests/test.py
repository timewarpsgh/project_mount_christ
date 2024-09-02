import math

def is_in_shooting_angle(ship1, ship2):
    # Calculate the angle between the ships
    angle = math.atan2(ship2['y'] - ship1['y'], ship2['x'] - ship1['x'])
    angle = math.degrees(angle)
    print(angle)
    if angle < 0:
        angle += 360
    print(f'the angle between the ships:{angle}')

    exit()


    # Convert the ship1's direction to an angle
    direction_angle = (ship1['direction'] * 45) % 360

    # Check if the target ship is within the shooting angle
    if (direction_angle - 45 <= angle <= direction_angle + 45) \
            or (direction_angle - 45 <= angle + 360 <= direction_angle + 45):
        return True
    else:
        return False

# Example usage:
ship1 = {'x': 0, 'y': 0, 'direction': 1}  # NE
ship2 = {'x': -1, 'y': -2, 'direction': 7}  # NW
print(is_in_shooting_angle(ship1, ship2))  # Output: True


