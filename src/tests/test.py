import random
import copy

TILES_AROUND_PORTS = [[2, 0], [2, 1], [2, -1], [-2, 0],
                      [-2, 1], [-2, -1],[0, 2], [1, 2],
                      [-1, 2], [0, -2], [1, -2], [-1, -2]]
new = copy.copy(TILES_AROUND_PORTS)
random.shuffle(new)

print(new)