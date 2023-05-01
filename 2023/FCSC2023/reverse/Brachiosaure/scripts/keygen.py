import qrcode
import hashlib
from PIL import Image
from sympy import Matrix
import random
import subprocess
import sys

# Use high correction % just in case to not break the codes
ERROR_CORRECT = qrcode.constants.ERROR_CORRECT_L
# Use a small box size to work with small matrices
BOX_SIZE = 2
# Use a border so that the QR codes are easier to find
BORDER = 2

# Username input
if len(sys.argv) == 2:
    username = sys.argv[1].encode()
else:
    username = "RXvB1WwdAXe7i65KE1km2GxP9Uy".encode()

# Generate a first QR code containing sha512(username)
data = hashlib.sha512(username).digest()
qr = qrcode.QRCode(version=1, error_correction=ERROR_CORRECT, box_size=BOX_SIZE, border=BORDER)
qr.add_data(data)
qr1 = qr.make_image().convert("L")
SIZE = qr1.size[0]
assert(qr1.size[1] == SIZE)

# Set the sha512 as an 8x8 matrix and square it to obtain the expected second QR code data
M = Matrix([[data[8*y+x] for x in range(8)] for y in range(8)])
M2 = M * M % 256
data = bytes([M2[x,y] for x in range(8) for y in range(8)])

# Generate a second QR code with the new data
qr = qrcode.QRCode(version=1, error_correction=ERROR_CORRECT, box_size=BOX_SIZE, border=BORDER)
qr.add_data(data)
qr2 = qr.make_image().convert("L")
assert(qr2.size == (SIZE, SIZE))

# Convert the qr code images to pixel matrices
# Add some random noise so that there is no equal lines and columns
# This way the matrice have a chance to be invertible
A = [[qr1.getpixel((x,y)) ^ random.randint(0, 7) for x in range(SIZE)] for y in range(SIZE)]
B = [[qr2.getpixel((x,y)) ^ random.randint(0, 7) for x in range(SIZE)] for y in range(SIZE)]

# Use sage to adjust A and B and find inverses for both
output = subprocess.check_output(["sage", "adjust_and_inverse.sage", str(A), str(B)]).split(b"\n")
A, B, A_inv, B_inv = [eval(res) for res in output[:4]]

# Create the first image
img1 = Image.new("L", (SIZE * 2, SIZE * 2))
# with the first QR code in the top left
for y in range(SIZE):
    for x in range(SIZE):
        img1.putpixel((x, y), A[y][x])
# and the second QR code inverse in the bottom right
for y in range(SIZE):
    for x in range(SIZE):
        img1.putpixel((x + SIZE, y + SIZE), B_inv[y][x])
img1.save("img1.png")

# Create the second image
img2 = Image.new("L", (SIZE * 2, SIZE * 2))
# with the first QR code inverse in the top left
for y in range(SIZE):
    for x in range(SIZE):
        img2.putpixel((x, y), A_inv[y][x])
# and the second QR code in the bottom right
for y in range(SIZE):
    for x in range(SIZE):
        img2.putpixel((x + SIZE, y + SIZE), B[y][x])
img2.save("img2.png")
