import math
import functools

sign = functools.partial(math.copysign, 1.0)

# def sign(x):
#     return math.copysign(1.0, x)
