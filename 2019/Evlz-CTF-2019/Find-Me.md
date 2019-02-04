# Find Me
**Category**: Reverse
**Author**: Achilles
**Points**: 396
**Challenge**: 
Take the [binary] give me the flag

**Solution:**
The binary file is a 64-bit ELF shared object which crashes when trying to execute it.

But we don't need to execute it as the **strings** command shows the following strings:
>dWdnYyUzQSUyRiUyRnJpeW0lN0JoZXlfZnJyemZfZWJnZ3JhX2p2Z3VfNjQlN0RwZ3MucGJ6
%%%02X
GG!, now put that flag on ye head and fly away!!
Nope, wrong flag ye got there m8, try again!

The first line is a base64 encoded string:
> uggc%3A%2F%2Friym%7Bhey_frrzf_ebggra_jvgu_64%7Dpgs.pbz

Which is URL encoded string:
> uggc://riym{hey_frrzf_ebggra_jvgu_64}pgs.pbz

With a ROT cipher:
> http://evlz{url_seems_rotten_with}ctf.com
