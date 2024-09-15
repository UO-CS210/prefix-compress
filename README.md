# prefix-compress

Small student project: Compress sorted word list using 
shared prefixes.

[Project instructions](doc/HOWTO-compress.md)

This might be small enough to be completed in a lab session, but 
more likely would work as a "mini-project" near the beginning of the 
first term of the Intro to CS course (ACM CS 1, CS 210 at U. Oregon, 
CS 161 at other Oregon colleges and universities). 

Main challenges for students: 
- One loop to determine how long the shared prefix is between two 
  strings.  For example, for 'example' and 'examine', the shared 
  prefix is 'exam', length 4.  
- String slicing and concatenation.

The functions written by students have doctests.  The
[HOWTO](doc/HOWTO-compress.md) document has quite a bit of 
conceptual background on compression, and on disciplined incremental 
development with testing. 

