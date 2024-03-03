# Problem

This is an Elliptic Curve Cryptography challenge where we can choose the parameters of the curve. For an N-bits long flag, the script generates N random elements on the curve and add together all the points $P_i$ where `bin(flag)[i] == 1`.

We know all the points and the total sum, we want to recover the flag (= the list of points that were summed together).

```python
from Crypto.Util.number import isPrime, bytes_to_long
import json
from flag import flag

print("I'm pretty nice, I let you choose my curve parameters")

p = int(input("p = "))
a = int(input("a = "))
b = int(input("bl = "))

assert int(p).bit_length() > 128, "Send a bigger number"
assert isPrime(p), "Send a prime"

E = EllipticCurve(GF(p),[a,b])
G = E.gens()[0]
o = G.order()
l = factor(o)

assert int(l[-1][0]).bit_length() >= 0x56
flag_int = bytes_to_long(flag.lstrip(b"GCC{").rstrip(b"}"))

bin_flag = [int(val) for val in bin(flag_int)[2:]]

points = [E.random_element() for _ in range(len(bin_flag))]

s = G*0

for i,val in enumerate(bin_flag):
	if val == 1:
		s += points[i]

print(json.dumps({"values":[[int(a) for a in point.xy()] for point in points]}),flush=True)
print(s.xy(),flush=True)
```

Author: [Shadowwws](https://twitter.com/Shadowwws7)

# Resources

- http://www.monnerat.info/publications/anomalous.pdf
- https://github.com/J08nY/ecgen
- https://github.com/jvdsn/crypto-attacks/blob/master/attacks/ecc/smart_attack.py

# Solution

Choosing the right curve(s) is key to solve this problem. There are a few checks to prevent us from cheating:

- Sage's `EllipticCurve` constructor will prevent us from generating a singular curve using $a=0$ and $b=0$ (`ArithmeticError: y^2 = x^3 defines a singular curve`),
- `p` should be prime and large enough to prevent us from solving the Discrete Logarithm Problem (DLP),
- The curve generator order should have a large enough factor (it cannot be smooth), to make the DLP harder .

The script doesn't prevent us from using **anomalous** curves (where the order of the generator is equal to $p$). This type of curve is weak to the so-called "Smart Attack" which can be used to solve the DLP on the curve.

Information to generate such curves can be found in [this paper](http://www.monnerat.info/publications/anomalous.pdf) but we can simply use the [ecgen tool](https://github.com/J08nY/ecgen). We can generate anomalous curves with the `--anomalous` flag. A Smart Attack implementation is available [here](https://github.com/jvdsn/crypto-attacks/blob/master/attacks/ecc/smart_attack.py). 

Our goal is to recover the points $P_i$ that sum to the known $S$ among all the $P_i$ to recover the flag bits.

$$
\sum_{flag[i] = 1}P_i = S
$$

Solving the DLP on all points with Smart Attack makes the problem easier, we find the $p_i$ such that $p_iG = P_i$ and $s$ such that $sG = S$. The equation becomes

$$
\sum_{flag[i] = 1}(p_iG) = sG
$$

In this case, the DLP has a unique solution for any integer, which means we can now leave the Elliptic Curve world and work in $GF(p)$.

$$
\sum_{flag[i] = 1}p_i = \sum_{1}^{N}a_ip_i = s \mod p \text{ where all the } a_i \text{ are either 0 or 1}
$$

Finding the right $p_i$ that sum to $s$ is known as the subset sum problem (in a finite field here) and can probably be solved using LLL, but to make the problem easier, we can instead call the script N times on the same curve to obtain a linear system of N equations with N unknowns (the $a_{i,j}$).

$$
\begin{cases}
\sum_{1}^{N}a_{i}p_{i,0} = s_0 \mod p \\
... \\
\sum_{1}^{N}a_{i}p_{i,N} = s_N \mod p \\
\end{cases}
$$

The system has a unique solution which yields the bits of the flag. We can solve it using SageMaths.

```python
from Crypto.Util.number import isPrime, long_to_bytes
from pwn import *
import json

def _lift(E, P, gf):
    x, y = map(ZZ, P.xy())
    for point_ in E.lift_x(x, all=True):
        _, y_ = map(gf, point_.xy())
        if y == y_:
            return point_

def SmartAttack(G, P):
    E = G.curve()
    gf = E.base_ring()
    p = gf.order()
    assert E.trace_of_frobenius() == 1, f"Curve should have trace of Frobenius = 1."

    E = EllipticCurve(Qp(p), [int(a) + p * ZZ.random_element(1, p) for a in E.a_invariants()])
    G = p * _lift(E, G, gf)
    P = p * _lift(E, P, gf)
    Gx, Gy = G.xy()
    Px, Py = P.xy()
    return int(gf((Px / Py) / (Gx / Gy)))

# Use a 130 bits anomalous curve
p = 0x03c967a105f928e610235b0e25d8773e55
a = 0x022a376538c7d354a01b863099b30c1cc5
b = 0x01e019b8d66c61f208b660c6795bb400f0
assert int(p).bit_length() > 128, "Send a bigger number"
assert isPrime(p), "Send a prime"
E = EllipticCurve(GF(p),[a,b])
G = E.gens()[0]
o = G.order()
l = factor(o)
assert int(l[-1][0]).bit_length() >= 0x56

n = 127 # Number of points = (flag length in bits) - 1
# Get 127 sums and 127 x 127 points
M = []
S = []
for k in range(n):
    print(k)
    #r = remote("challenges1.gcc-ctf.com", int(4000))
    r = process(["sage", "chall.sage"])
    r.recvuntil(b"p = ")
    r.sendline(f"{p}".encode())
    r.recvuntil(b"a = ")
    r.sendline(f"{a}".encode())
    r.recvuntil(b"bl = ")
    r.sendline(f"{b}".encode())
    # Solve the DLP for all random points
    values = [SmartAttack(G, E(_)) for _ in json.loads(r.recvline())["values"]]
    # Solve the DLP for the sum of points
    s = SmartAttack(G, E(eval(r.recvline())))
    M.append(values)
    S.append(s)
    r.close()

# Solve the linear system
M = Matrix(GF(p), M)
S = Matrix(GF(p), S).transpose()
flag = int("".join(str(bit[0]) for bit in M.solve_right(S)), 2)
print(b'GCC{' + long_to_bytes(flag) + b'}')
```

#crypto #DiscreteLog #ECC

