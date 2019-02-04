# Sanity Check 2
**Category**: Sanity
**Author**: Hexterisk
**Points**: 50
**Challenge**: 
No one deserving should go ever go empty handed.
[Image]

**Solution:** 
Second sanity check, image is a QR code.

Scanning it reveals a Zippyshare link to download a **flag.zip** archive protected by a password, containing a **flag.txt** file.

Before using JohnTheRipper, let's try [a zip password recovery website](https://passwordrecovery.io/zip-file-password-removal/)... Password is found in seconds: **!!!0mc3t**.

The text file contains an hexadecimal string in plain text:
> 652076206c207a207b207320302075206e2064205f20302066205f206d2075203520692063207d206320742066

Converted to ASCII it becomes:
> e v l z { s 0 u n d _ 0 f _ m u 5 i c } c t f
