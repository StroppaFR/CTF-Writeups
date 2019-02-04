# Jail

**Category**: Misc

**Author**: Hexterisk

**Points**: 290

**Challenge**:
`ssh u1@xx.xxx.xxx.xxx -p 2220 pass u1`

**Solution:** 

When connecting, we are inside a shell script that executes our commands. We can get out with **bash**.

From there we can't see the standard output stream but we can see the standard error stream so we can simply redirect with **1>&2** and find the flag.

    bash-4.3$ /bin/ls 1>&2
    Desktop  Documents  Music  Pictures  Videos  bin  flag.txt  programs
    bash-4.3$ /bin/ls /bin 1>&2
    bash  ec.sh  echo  ls  sh
    bash-4.3$ /bin/ls /usr/bin 1>&2
    awk  chattr  chsh  ssh	vim  wc
    bash-4.3$ /usr/bin/vim flag.txt 1>&2

> Pass: evlz{0ut_0f_ech0}ctf

