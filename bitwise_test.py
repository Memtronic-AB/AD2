global a

def setBit(int_type, offset):
    mask = 1 << offset
    return(int_type | mask)
  
# clrBit() returns an integer with the bit at 'offset' cleared.
def clrBit(int_type, offset):
    mask = ~(1 << offset)
    return(int_type & mask)

def mid_level():
    a = a+2
    b=setBit(a,0)
    a=b



a=0x0718
b= mid_level(a)
c=9