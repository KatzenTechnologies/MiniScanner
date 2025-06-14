import math

global pi, tau, eta, e
pi = math.pi
tau = 2 * pi
eta = 0.5 * pi
e = math.e

def sqrt(value, base = 2):
    return value ** (1 / base)

def sgn(value):
    if value > 0:
        return 1
    elif value < 0:
        return -1
    else:
        return 0

# declare aliases of sgn
sg = sgn
signum = sgn

def factorial(value):
    a = 1
    for i in range(1, value+1):
        a *= i
    return a
