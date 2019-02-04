# Bad Compression
**Category**: Crypto
**Author**: Xorcerer
**Points**: 150
**Challenge**: 
This won't be too bad, I guess...  [File]

**Solution:**
The file contains a python script which seems to execute some kind of on an input string.
We are also given the compressed flag:
> 100001000100110000000100

and the SHA-256 of the complete flag:
> e67753ef818688790288702b0592a46c390b695a732e1b9fec47a14e2f6f25ae

The algorithm uses a **drop** function that removes a character from a string:

    def drop(b,m):
        return(b[:m]+b[(m+1):])
And a **shift** function that shifts the end of a string to the start:

    def shift(b, i):
        return(b[i:] + b[:i])
We can easily revert the **shift** function as well as the algorithm loop (by noticing that l is always equal to i - 1) but the **drop** function loses information.

    def unshift(b,i):
        return b[len(b)-i:]+b[:len(b)-i]
    def undrop(b,i):
	    return b[:i]+'?'+b[i:]
        
    b='100001000100110000000100'
    i = len(b) + 1
    l = i - 1
    while(i>1):
        i-=1
        l=l+1
        b=undrop(unshift(b,i),l%i)
    print b

We can deduce that any string matching ﻿"????00?0?0?1000????????1001?1?00??00?0?00?1001??" could be the input flag. The length of that string is divisible by 8 so it's probably 6 ascii characters, which means we are looking for evlz{xxxxxx}ctf.

Fortunately we have the SHA-256 of the flag so now we can just bruteforce the 2^21=2,097,152 possibilities and match the hash.
> evlz{20o8@d}ctf
