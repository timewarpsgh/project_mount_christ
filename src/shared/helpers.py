from dataclasses import dataclass
import math

@dataclass
class Point:

    x: int=None
    y: int=None


def unit_vector(x1, y1):
    """
    计算向量 (x1, y1) 的单位向量。

    参数:
    x1, y1 -- 向量的坐标

    返回:
    单位向量的坐标 (ux, uy)。
    """
    magnitude = math.sqrt(x1 ** 2 + y1 ** 2)
    if magnitude == 0:
        return (0, 0)
    ux = x1 / magnitude
    uy = y1 / magnitude
    return (ux, uy)

def are_vectors_in_same_direction(point_1, point_2):
    x1 = point_1.x
    y1 = point_1.y

    x2 = point_2.x
    y2 = point_2.y


    # 计算两个向量的单位向量
    u1 = unit_vector(x1, y1)
    u2 = unit_vector(x2, y2)

    # 比较单位向量是否相同
    return u1 == u2