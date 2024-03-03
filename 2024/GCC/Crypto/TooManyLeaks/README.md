# Problem

Alice and Bob use the Diffie-Hellman key exchange protocol to generate a shared secret `s` using public keys $A = g^a \mod p$ and $B = g^b \mod p$.

After that, they generate another shared secret `s2` with Charlie using public keys $AC = g^{a+c} \mod p$ and $B = g^b \mod p$.

The flag is encrypted with AES_CBC, using `s` as the secret key.

The challenge leaks the 256 high bits of `s` and `s2` (out of 512).

```python
#!/usr/bin/env python3
from Crypto.Util.number import getStrongPrime
import hashlib
from secret import flag
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

def encrypt_flag(secret_key):
    sha1 = hashlib.sha1()
    sha1.update(str(secret_key).encode('ascii'))
    key = sha1.digest()[:16]
    iv = os.urandom(16)

    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(flag,16))
    print("{ ciphertext : " + ciphertext.hex() + ", iv : " + iv.hex() + "}")

    return ciphertext, iv

# Generate parameters
p = getStrongPrime(512)
print(f"{p=}")
g = 2

# Alice calculates the public key A
a = getStrongPrime(512)
A = pow(g,a,p)
print(f"{A=}")

# Bob calculates the public key B
b = getStrongPrime(512)
B = pow(g,b,p)
print(f"{B=}")

# Calculate the secret key
s = pow(B,a,p)

# What ?!
mask = ((1 << 256) - 1 << 256) + (1 << 255)
r1 = s & mask
print(f"{r1=}")

# Charlie arrives and sync with Alice and Bob
c = getStrongPrime(512)
print(f"{c=}")
AC = pow(g,a+c,p)
s2 = pow(AC,b,p)
print(f"{AC=}")
r2 = s2 & mask
print(f"{r2=}")

encrypt_flag(s)
```

Author: TheoR

# Resources

- https://en.wikipedia.org/wiki/Diffie%E2%80%93Hellman_key_exchange
- https://hal.science/hal-03045663/document

# Solution

The challenge is a textbook example of Diffie-Hellman key recovery from partial knowledge. This exact case where the high bits of `s` and `s2` are known is explained in section 6.2 of the paper [Recovering cryptographic keys from partial information, by example](https://hal.science/hal-03045663/document]) from Gabrielle de Micheli and Nadia Heninger. Note that in the paper, $a_1$ and $a_2$ should be $r_1$ and $r_2$.

The technique uses LLL on a crafted lattice to solve the Hidden Number Problem. We can implement the example in SageMath.

```python
p=12659765344651740648724763467724826993725936263366951091039118416195292099370631377712042960634433459603684366298668316118798753725083109726606307230709481
A=3301451331273103822833339817189898484477574460332521541023442766617163003861277567173209945681794302860954824946103841799431004692332025577336344394695314
B=4585794959794770660643739179463936175470737153250504109915159478661133411133496952267060123069524419032124459912888910847574766484421490926652243218962165
c=13305825506775525477695274133373660177357107668926266252207560823721404224069651345842091298405541700114875323083835571095924844005731356668708175418706451
r1=2568748433813321161874639775621008976218176085243148442053880160521563872123950485879781803171876295709491228751046125319137014580919198982132588104122368
r2=3829741721947473719324421527352078984331611168371079834096760630101921404398331513243772077101441758022492336098369985623504441570880895898971858238701568

t = pow(B, c, p)
t_1 = pow(t, -1, p)
K = 2 ^ 255

# Construct the lattice
M = []
M.append([p, 0, 0])
M.append([t_1, 1, 0])
M.append([r1-t_1*r2, 0, K])
M = Matrix(M)

# Run LLL to recover k1 = s - r1 and k2 = s2 - r2
M_reduced = M.LLL()
for row in M_reduced:
    if row[2] == K:
        print("Recovered k1 and k2")
        k1 = -row[0]
        k2 = -row[1]
s = r1 + k1

# Decrypt AES-CBC
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

ciphertext = int.to_bytes(int(0x89c372210be2a7b313366206f7426f941157009493d00fcb18b467250139413b6ea1ada6302e1916b6c02a6f935f4ed4), 48)
iv = int.to_bytes(int(0xc7d192fb72b529acf7b57d488c182466), 16)
sha1 = hashlib.sha1()
sha1.update(str(s).encode('ascii'))
key = sha1.digest()[:16]
cipher = AES.new(key, AES.MODE_CBC, iv)
plaintext = unpad(cipher.decrypt(ciphertext), 16)
print(plaintext.decode())
```

Running the script yields the flag `GCC{D1ff13_H3llm4n_L34k_15_FUn!!}`

#crypto #LLL #DiffieHellman
