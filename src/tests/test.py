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

matrix_zeros = np.ones((rows, cols), dtype=int)
print(matrix_zeros)

# turn to 2d array
matrix_2d = matrix_zeros.tolist()
json_str = json.dumps(matrix_2d)

two_d_list = json.loads(json_str)
matrix = np.array(two_d_list)

print(matrix)

# get the 1st col and turn into 32 bits
col_1 = matrix[:, 0]
print(col_1)

print(len(col_1))

bit_str = ''.join(str(x) for x in col_1)
print(bit_str)

# turn bit_str with 32 bits into a int32 number
int_num = int(bit_str, 2)
print(int_num)


list_of_list = [[0] * cols for i in range(rows)]
print(list_of_list)



# turn an integer to 32 bits
def int_to_32_bits(num):
    bin_str = bin(num)
    bin_str = bin_str[2:]
    bin_str = '0' * (32 - len(bin_str)) + bin_str
    return bin_str


bin_str = int_to_32_bits(0)
print(bin_str)

# turn to a list of ints
list_of_ints = [int(x) for x in bin_str]
print(list_of_ints)

# turn to a numpy column
col = np.array(list_of_ints)
print(col)

# add a col to the right of an existing numpy matrix
matrix_with_col = np.hstack((matrix, col.reshape(rows, 1)))

# print matrix dimensions
print(matrix_with_col.shape)


