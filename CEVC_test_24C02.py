"""
   Test to write to and read from a memory 24C02 on the CEVC board
   Author:  Digilent, Inc. and Martin Andersson
   Revision:  2021-08-20

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
import time
import AD2
from random import randrange

AD=AD2.AD2()
AD.OpenAD2(3)
AD.PowerCtrl(0,False,0,False)   # power from external PSU

# initiate I2C on SCL = DIO-0, SDA = DIO-1 at speed 100kHz 
AD.InitI2C (1e5, 0, 1)

# ------------ Read data from memory ----------------
adr = (c_ubyte*1)()
rgRX = (c_ubyte*1)(256)

I2C_ADR = 0x50      # 7-bit address CEVC

#read all data (256 byte) from memory starting at adr:0
for i in range(0,256):
    adr = (c_ubyte*1)(i)
    AD.dwf.FDwfDigitalI2cWrite(AD.hdwf, c_int(I2C_ADR<<1), adr, c_int(1), byref(AD.iNak)) # write 1 bytes address
    AD.dwf.FDwfDigitalI2cRead(AD.hdwf, c_int(I2C_ADR<<1), rgRX, c_int(1), byref(AD.iNak)) # read 1 bytes of data
    print (str(i) + ' : ' +str(rgRX[0]))

# random number
slump = randrange(256)
print ("Random number:", slump,"=",hex(slump))

# write random byte to all memory
TX = (c_byte*2)()
TX[1] = c_byte(slump)
for element in range(0,256):
    TX[0] = c_byte(element)
    time.sleep (0.01)
    AD.dwf.FDwfDigitalI2cWrite(AD.hdwf, c_int(I2C_ADR<<1), TX, c_int(2), byref(AD.iNak)) # write 2 bytes

#read all data (256 byte) from memory starting at adr:0
for i in range(0,256):
    adr = (c_ubyte*1)(i)
    AD.dwf.FDwfDigitalI2cWrite(AD.hdwf, c_int(I2C_ADR<<1), adr, c_int(1), byref(AD.iNak)) # write 1 bytes address
    AD.dwf.FDwfDigitalI2cRead(AD.hdwf, c_int(I2C_ADR<<1), rgRX, c_int(1), byref(AD.iNak)) # read 1 bytes of data
    print (str(i) + ' : ' +str(rgRX[0]))

#This function closes devices opened by the calling process
AD.CloseAD2()


