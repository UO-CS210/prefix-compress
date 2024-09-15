# Prefix compression howto

_Compression_ means producing a more compact representation of 
something.  Compression may be specialized to a 
certain kind of data 
(e.g., image compression) or it may be more general purpose.  
Decompression is the inverse operation, but decompressing after a 
_lossy_ compression (e.g., JPEG, MPEG) may produce only an 
approximation of the original data before compression.  
Decompressing the representation produced by a _lossless_ 
compression produces an exact copy of the original. 

All compression techniques identify and exploit _redundancy_ in data.
Redundancy can be thought of as information in part of the data that 
can be used to predict other parts of the data.  The opposite of 
redundancy is _entropy_, the amount of information needed to 
oredict some part of a data set.  Entropy is measured in _bits_, 
which are related to (but distinct from) the binary digits 
used to represent information in computer memory.  

In this project you will write functions for a lossless, special 
purpose compression method for sorted word lists.  The 
redundancy this compression algorithm will exploit is that many 
words in a sorted word list (the kind we might use for a 
spell-checker or Boggle solver) start with the same first few 
letters as the word before.  

## Prefix compression

Consider this short sequence of words from `data/dict.txt`: 

```text
abate
abatement
abattoir
abbe
abbess
abbey
abbot
abbreviate
abbreviated
```
We can represent each word as a pair:  An integer indicating how 
many initial letters it shares with the word before, and a string 
providing the remaining letters.  If the short sequence above were 
the whole word list, it might be encoded as 

```text
0,abate
5,ment
4,toir
2,be
4,ss
4,y
3,ot
3,reviate
10,d
```

While we could represent shared prefixes textually as shown above, 
such as "4," or "10,", we can do much better by recognizing that 
shared prefixes are usually short.  A shared prefix longer than 24 
should be very rare.  If we encode prefixes limited to 24, we could 
use letters A..Z to represent 0..24, we can use one string to 
represent both the shared prefix and the remaining letters. So we 
might represent the list above as  

```text
Aabate
Fment
Etoir
Cbe
Ess
Ey
Dot
Dreviate
Kd
```

The built-in function `chr` converts an integer to a 
single-character string, based on the
[Unicode](https://en.wikipedia.org/wiki/Unicode)
text representation.  The built-in function 
`ord`gives an 
integer encoding of a letter.  The letters from 'A' to 'Z' are 
represented by a sequence of integers 65 to 90 in Unicode, so we 
can compute a character to represent an integer 0..25 by 
- adding `ord("A")` to the integer
- converting that sum `n` to a character as `chr(n)`

While it is likely we could use characters with unicode encodings 
greater than 90, words sharing prefixes of more than 25 characters 
are so rare that it would not significantly improve our compression. 
A 
[list of 466,000 English words](https://github.com/dwyl/english-words)
contains only a handful with 25 or more characters:  

```text
antidisestablishmentarian 25
antidisestablishmentarianism 28
cyclotrimethylenetrinitramine 29
demethylchlortetracycline 25
dichlorodiphenyltrichloroethane 31
electroencephalographical 25
electroencephalographically 27
hydroxydehydrocorticosterone 28
hydroxydesoxycorticosterone 27
```

We will still write the program to work correctly if it encounters 
two words with a common prefix longer than 25 characters, but we 
won't worry about the performance impact of encoding only the first 25. 

## Order of development

I have provided a main program, `pfc.py`, which will compress or 
decompress an input file depending on whether it is invoked like this

```commandline
python3 pfc.py compress data/sample.txt  data/compressed.txt
```
or like this 

```commandline
python3 pfc.py expand data/compressed.txt  data/restored.txt
```

Program `pfc.py` performs the compression and expansion by calling 
functions in `codec.py`, the source file you will produce.
"[Codec](https://en.wikipedia.org/wiki/Codec)" is short for 
"coder/decoder", jargon for a matching pair of transformations that 
convert from one representation to another ("encode") and from 
the second back to the first ("decode").  Codecs you may be familiar 
with include [MP3](https://en.wikipedia.org/wiki/MP3)
(between an audio signal and a compressed digital 
representation) and  [JPEG](https://en.wikipedia.org/wiki/JPEG) for 
images, both of which are lossy.  Your codec will provide _lossless_ 
pair of functions, `encode` and `decode`, meaning they will be 
inverses of each other.  That is, you will ensure that 
$decode(encode(s,x), x) = s$. The _x_ in this equation will be the 
immediately preceding word in the word list.  The redundancy we are 
exploiting to compress data is the similarity between _s_ and _x_.

## Building the codec

Start `codec.py` with a skeleton that imports the `doctest` module 
and runs all the doctests when the module is invoked as a main program: 

```python
"""codec is short for "coder-decoder", i.e., a pair of matched functions for 
encoding and decoding values.  In our case the values are strings, and we
encode a string relative to another string (e.g., the immediately preceding
string in a text file).
"""

import doctest

if __name__ == "__main__":
    doctest.main()
```


To build the encoder, we will need to 
- determine the length of the shared prefix of _s_, the string to be 
  encoded, and prior word in the word list.
- represent that shared prefix compactly as a single character
- combine the resulting character with the remainder of _s_

To build the decoder, we will need to 
- break the encoded string _s_ into the single character indication 
  of its shared prefix and the remainder, which we'll call the 
  _suffix_. 
- Interpret the shared prefix indicator as an integer _n_.
- Combine the first _n_ characters of the predictor string with the 
  suffix.

We want to construct this functionality by writing functions in an 
order that will allow us to test each function. This means that the 
`encode` and `decode` functions will be the last we write, after we 
have written and tested the functions that they will call. 

### Shared prefix length

We can start with a function for determining the length of the 
shared prefix between a string `s` and a predictor string `p`: 

```python
def shared_prefix_length(s: str, p: str) -> int:
    """Return length of shared prefix of s and p.

    >>> shared_prefix_length("abcdef", "abcxyz")
    3
    >>> shared_prefix_length("dog", "cat")
    0
    >>> shared_prefix_length("fork", "forked")
    4
    >>> shared_prefix_length("flame-out", "flame")
    5
    """
```

This function will require a loop through the characters in `s` and 
`p` together.  There are several ways to do this, but all of them 
involve keeping track of a count or index of matched characters.  Be 
careful of not "running off the end" of either string.   I used a 
`while` loop with a condition that checked that an index variable 
`i` was within bounds for both strings and the _i_ th character of 
`s` and `p` matched. 

### Encode and decode length

Next we can produce the pair of functions `encode_length` and 
`decode_length` that handle representation of an integer between 
zero and 25 inclusive as a single letter.

It is tempting to hard-code the representation choices (range 0 to 
25, representation 'A' to 'Z') directly as literals in the code, and 
if I'm being honest, that is what I did first.   But that sloppiness 
violates our coding guideline against "magic numbers".  A better 
approach is to isolate these representation choices in a few 
symbolic constants near the beginning of the module, just 
after any `import` statements.  Since they will be global to the 
module, we will write them in "all caps", and since they are 
strictly internal to this module, we will begin them with a single 
underscore.  Also, since they are fairly far from some of the 
functions that use them, we'll give them long descriptive names. 


```python
# Internal configuration constants for encode_length, decode_length
_MAX_PREFIX_ENCODE = 25   
_CODE_ZERO = 'A'
_CODE_MAX = 'Z'
```

Now we can write `encode_length`:

```python
def encode_length(n: int) -> str:
    """Return a one character representation of an integer 0 <= n <= 25.

    >>> encode_length(0)
    'A'
    >>> encode_length(25)
    'Z'
    >>> encode_length(5)
    'F'
    """
    assert 0 <= n <= _MAX_PREFIX_ENCODE, f"{n} exceeds MAX_PREFIX_ENCODE"
    return 'Z'   # FIXME
```

My implementation of `encode_length` is a single line of Python code 
that uses the built-in functions `chr` and `ord`.  You might 
reasonably ask why I bother to write a Python function for a single 
line of code.   There are a couple of reasons: 
- The name `encode_length` is clearer than the line of code that 
  implements it.  It will make our `encode` and `decode` functions 
  more readable, and in particular the relation between 
  `encode_length` and `decode_length` will be clearer. 
- The design decisions regarding how to represent the length are 
  isolated in one obvious place.  One of the key purposes of a 
  function or other modularization construct (e.g, _classes_ which 
  we will introduce in the second course in this series) is to 
  isolate design decisions so that, when we later make changes to 
  the software, we don't have to ask "where else do I need to make 
  this change?".


When `encode_length` is working correctly, we can write its inverse 
function `decode_length`: 

```python
def decode_length(s: str) -> int:
    """Inverse of encode_length, converts A..Z to 0..25.

    >>> decode_length("A")
    0
    >>> decode_length("Z")
    25
    >>> decode_length("F")
    5
    """
    assert _CODE_ZERO <= s <= _CODE_MAX, f"{s} is not a legal encoding of prefix length"
    return -1   # FIXME
```

### Encode and decode strings

We are finally ready to write the `encode` and `decode` functions 
that `pfc.py` calls to compress a word list.  We'll start with 
`encode`: 

```python
def encode(s: str, predictor: str) -> str:
    """Encode (compress) s relative to predictor.

    >>> encode("abatement", "abate")
    'Fment'
    >>> encode('abate', 'abatement')
    'F'
    >>> encode("abattoir", "abatement")
    'Etoir'
    >>> encode("dog", "cat")
    'Adog'
    """
```

Recall our plan [above](#building-the-codec) for encoding.  We now 
have the tools we need to build the `encode` function with just a 
few lines of code. 
- `shared_prefix_length(s, predictor)` gives us the length of the 
  shared prefix.  Although we will rarely encounter a shared prefix 
  that is too long to be encoded, we should play it safe by taking 
  the minimum of that value and `_MAX_PREFIX_ENCODE`. 
- `encode_length` gives us the single character encoding of the 
  shared prefix length. 
- Python gives us the basic string manipulation operations to 
  assemble the encoded string, 
  including concatenation (`+`) and [slicing](
  https://docs.python.org/3/library/stdtypes.html#typesseq-common)
  like `s[0]` for the first character and `s[n:]` for characters 
  starting from index `n`. 

The body of my `encode` function is just three lines of Python code, 
corresponding closely to the three steps of
[the plan](#building-the-codec).  Feel free to expand it to a few 
more lines, but if you find yourself writing any complex logic, even 
an `if` statement, then you are probably on the wrong track. 

After `encode`, we can write and test `decode`: 

```python
def decode(s: str, predictor: str) -> str:
    """Decode s, which must be prefix-encoded string.

    >>> decode("Fment", "abate")
    'abatement'
    >>> decode("F", "abatement")
    'abate'
    >>> decode("Etoir", "abatement")
    'abattoir'
    >>> decode("Adog", "cat")
    'dog'
    """
```

My implementation of the `decode` function is even shorter than 
`encode`, just two lines of Python code with some string operations 
and a call to `decode_length`. 

## Using the compression program

`pfc.py` provides a command-line interface for your compression and 
decompression functions.  For a simple "smoke test", try compressing 
a short word list and printing the result to the screen: 

```commandline
python3 pfc.py compress data/sample.txt
```
The output should look like this: 

```text
Aabate
Fment
Etoir
Cbe
Ess
Ey
Dot
Dreviate
Kd
```

To save the compressed output in a file, run it this way: 

```commandline
python3 pfc.py compress data/sample.txt data/compressed.txt
```

Now the output should be in `data/compressed.txt`.  Decompress it 
and send the output to the screen this way: 

```commandline
python3 pfc.py expand data/compressed.txt
```
The output should look like this, and should be identical to 
`data/sample.txt`: 

```text
abate
abatement
abattoir
abbe
abbess
abbey
abbot
abbreviate
abbreviated
```

To check it on a more substantial word list, try 

```commandline
python3 pfc.py compress data/dict.txt data/compressed.txt
```

`dict.txt` is a list of 41,238 words.  It occupies 380 kilobytes of 
storage.  `data/compressed.txt` produced as shown above occupies 206 
kilobytes of storage, or about 45% less.   Not bad for a simple 
codec that a beginning Python programmer can build and understand!  
More sophisticated codecs used in production software use similar 
principles, but with more complex ways of predicting the next chunk 
of data and representing only how the actual data differs from the 
prediction. 








