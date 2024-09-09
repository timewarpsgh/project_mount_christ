ships_cnt = 8
rows = 2
# cal cols
cols = ships_cnt // rows

# get each ship's position in a 2d grid

row = -1
col = -1

for i in range(ships_cnt):
    if row == 1:
        row = 0
        col += 1
    else:
        row += 1

    if col == -1:
        col = 0

    print(row, col)

