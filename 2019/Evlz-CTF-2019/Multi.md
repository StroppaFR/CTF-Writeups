# Multi

**Category**: Pwn

**Author**: iamalsaher

**Points**: 396

**Challenge**: 

nc xx.xxx.xxx.xxx 31337
[Binary]

**Solution:**

The file is a 64-bit ELF executable. I used gdb to debug the binary and IDA to have a better view of the assembly code.

This challenge is divided into 4 stages. The first 3 stages raise 3 boolean flags on completion and the 4th stage executes **/bin/sh** if the flags are correctly set.

If a stage fails, the program exits with a supportive message:

> Go learn some more

**Stage 1**

> Solve this challenge to advance
Enter two numbers: 

This stage is pretty straight-forward, the application requires 2 numbers so that B - A = 1337. The stage fails is one of the number is greater than 1336.

Fortunately, negative numbers exist.

> -1337 0

**Stage 2**

Stage 2 is a loop where you have a choice between the same two inputs at every step. Depending on your input, a variable called **Val** is increased or decreased. It starts at 10000.

> 1. Add a number between 0-250  
> 2. Subtract a number between 0-250  
>  2  
> Enter a number between 1-250 inclusive: 250  
> Val is now 9750

It seems that you can't bypass this choice. You also can't go above 10,000. Finally, if you try to decrease the value below 5,000,  it gets raised back up to more than 9,000.

After further investigation, the application uses 2 threads for this stage:

 1. The main thread handles the main loop and does the adding and substracting depending on user input. It sleeps for 1 second at the end of each loop execution and if the value is negative, you win the stage.
 2. Another thread runs the following loop in the **check()** function:

```
while(Val <= 10000) {
	if(Val < 5000) {
		sleep(4); // 4 seconds
		Val += 4900;
	}
}
```

The goal in this stage is to raise Val above 10,000 in order to stop the check() thread. We can take advantage of the 4 seconds sleep by decreasing the value to 4,999 and raise it back quickly to 5,749. When the second thread adds 4,900 Val becomes 10,649 so it stops checking and we are then free to decrease the value to below 0.

**Stage 3**:

At stage 3, you are greeted with this message:

> Now that you are here, you gotta tell me about yourself: 

When you type some input, the programs repeats what you typed and asks you for an address:

> Now that you are here, you gotta tell me about yourself: 
> someinput  
> So you say that you are a  
>	    someinput  
> Okay, let's see how good you are  
> Give me the address of the puts function  

To pass this stage, you need to input the address of libc puts function as a long value. Unfortunately the executable is **dynamically linked** so you can't extract this information with static analysis.

Now the first input of this stage is there for a reason, we can find that there is a **Format String Attack** possible on this input because the program repeats your input with **printf(your_input)** instead of **print("%s", your_input)**!

I had some trouble figuring this one out and I ended with the following solution:
1. Use the input "%p:%p:%p:%p:%p:%p:%p:%p:%p:%p:%p:%p:%p:%p:%p:%p:%p:%p:%p:%p:%p:%p:%p:%p:%p:%p:%p:%p:%p:%p:%p:%p:%p:%p:%p:%p:%p:%p:%p" to leak values directly from the stack.
2. The last leaked value is return address of __libc_start_main function. It's different every time you launch the binary because of dynamic linking.
3. Add the correct offset to the value (offset between this return address and the address of puts in libc).

I used gdb to figure out the offset needed once, which was 5ee29 on my machine. Sadly, the remote server was using a different libc version so the offset was different. I tried different offsets from a [libc database](https://github.com/niklasb/libc-database/) and found the correct version and offset: **libc6_2.23-0ubuntu10_amd64** and **4ee60**.

I'm sure people will come out with better methods of getting puts function and I'm certain you can simply bypass this stage completely or even go to the flag from here but it's my first experience with CTF.

**Stage 4**

The last stage feels easier, you have 4 choices and can repeat them:
> We are about to finish. I hope you had fun  
> 1. Create a memory region  
> 2. Delete the memory region  
> 3. Do some captcha  
> 4. Jump

First option allocates 8 bytes of memory, puts the address in some variable p and raises a flag to 1.

Second option simply frees the memory allocated at p.

Third option asks "Whats the sum of 0xdeadbeef and 0xcafebabe:", allocates 8 bytes for your input and stores your answer in the allocated memory block.

Fourth option only works if the flag from first option was raised and jumps to the value stored at the address pointed by p.

This is a **Use After Free** vulnerability. By calling 1, 2, 3 and 4, in that order, we are able to jump to any address we input in 3. Indeed, we are allocating the same memory block in 3 as the one that was originally pointed by p and freed in 2. In 4, the program reuses the pointer p that still points to the same memory location.

In 3, we input the address of the **finish()** function, that is otherwise not accessible: **4199982** (0x40162e, obtainable with objdump -d multi | grep finish).

```
$ ls
flag
multi
$ cat flag
evlz{I_h0pe_y0u_l3arnt_s0me7h1ng_wh1l3_s0lv1ng_th15}ctf
```

