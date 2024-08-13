import json
import numpy as np

# rows = 12 * 2 * 45 # 1080
# cols = 12 * 2 * 30 * 3 # 2160
#
# print(f'{rows=}') # 6 * 3 = 18 grids           16*2 = 32      4
# print(f'{cols=}') # 12 * 3 = 36 grids          32*2 = 64      72


# a = 123124124
# # turn a into bitstring
# bin_str = bin(a)
# print(bin_str)

# init a matrix with 32 rows and 64 cols, each element is either 0 or 1, to represent a map
rows = 32
cols = 64

matrix = np.zeros((rows, cols), dtype=int)

# set cols 28 to 36 to 1
matrix[5:10, 26:36] = 1
print(matrix)

# turn to 2d list
matrix_list = matrix.tolist()
print(matrix_list)

print(json.dumps(matrix_list))
