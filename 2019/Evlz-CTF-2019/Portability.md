# Portability

**Category**: Misc

**Points**: 25

**Challenge**: 

My beautiful API is finally ready! Uses Flask, Virtual Environments, and loads the config from Environment Variables! [Download]

**Solution:** 

The zip files contains a Web API using Python and Flask.

When reading the **application.py** file, we notice that the flag is loaded from an environment variable.
> FLAG = os.getenv("FLAG", "evlz{}ctf")

Obviously our environment doesn't contain the flag but we can look around for the "setenv" or "export" string.

`grep -r ./ -e setenv -e export`

One interesting commented line comes out:
> \# export $(echo RkxBRwo= | base64 -d)=ZXZsenthbHdheXNfaWdub3JlX3RoZV91bm5lY2Nlc3Nhcnl9Y3RmCg==

The first base64 string is FLAG and the second the actual flag:
> evlz{always_ignore_the_unneccessary}ctf
