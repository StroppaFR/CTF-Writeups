import sys
import random

assert(len(sys.argv) == 3)

# Read 2 matrices from command line
m1 = eval(sys.argv[1])
m2 = eval(sys.argv[2])
size = len(m1)

# Randomize M1 until it has an odd determinant so that it is inversible
while True:
    M1 = Matrix(IntegerModRing(256), m1)
    if M1.determinant() % 2 == 1:
        break
    m1[random.randint(0, size-1)][random.randint(0, size-1)] ^^= 1

# Randomize M2 until it has an odd determinant so that it is inversible
while True:
    M2 = Matrix(IntegerModRing(256), m2)
    if M2.determinant() % 2 == 1:
        break
    m2[random.randint(0, size-1)][random.randint(0, size-1)] ^^= 1

# Print the two adjusted matrices and their respective inverse
print(list([list(c) for c in M1]))
print(list([list(c) for c in M2]))
print(list([list(c) for c in M1.inverse()]))
print(list([list(c) for c in M2.inverse()]))
