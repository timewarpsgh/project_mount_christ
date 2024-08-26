# WORLD_MAP_COLUMNS
cols = 12 * 2 * 30 * 3
print(cols)

# WORLD_MAP_ROWS
rows = 12 * 2 * 45
print(rows)

#
GRID_TILES_COUNT: int = 13


a = cols / 13
print(a)

print(int(a))
b = rows / 13
print(b)


cells = [[0] * 2 for i in range(3) ]
print(cells)