import numpy as np


def step_function(*args):
    x = np.array(args)
    y = x > 0
    return y.astype(np.int)


print(np.array((1, 2, 3)))
