import math


def clog2(x):
    if x == 0:
        return 0
    return int(math.ceil(math.log2(x)))
