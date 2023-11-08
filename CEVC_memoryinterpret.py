"""
   Interprets the memory content of the memory of the CEVC. Prints the info to terminal.
   Author:  Martin Andersson
   Revision:  2022-02-07

   Requires:                       
       Python 3, AD2-CEVC hw, AD2 hw
"""

from ctypes import *
import time
import AD2

AD=AD2.AD2()
AD.OpenAD2(3)
AD.PowerCtrl(3.3,True,0,False)   # power from external PSU
time.sleep(0.3)
# initiate I2C on SCL = DIO-1, SDA = DIO-0 at speed 100kHz 
AD.InitI2C (1e5, 1, 0)

# ------------ Read data from memory ----------------
adr = (c_ubyte*1)()
rgRX = (c_ubyte*1)(256)
datalist = []
I2C_ADR = 0x50      # 7-bit address CEVC

#read all data (256 byte) from memory starting at adr:0
for i in range(0,256):
    adr = (c_ubyte*1)(i)
    AD.dwf.FDwfDigitalI2cWrite(AD.hdwf, c_int(I2C_ADR<<1), adr, c_int(1), byref(AD.iNak)) # write 1 bytes address
    AD.dwf.FDwfDigitalI2cRead(AD.hdwf, c_int(I2C_ADR<<1), rgRX, c_int(1), byref(AD.iNak)) # read 1 bytes of data
    datalist.append(rgRX[0])


# interpret the data
print ("Field version\n  Major:   " + str((datalist[0] & 0xf0) >> 4))
print ("  Minor:   " + str(datalist[0] & 0x0f))
print ("Unit id:   " + str(datalist[1]) + "(" + AD.UnitIdString(datalist[1]) + ")")
print ("Article#:  " + AD.ASCIIString(datalist, 2, 7))
print ("Revision:  " + chr(datalist[10]))
print ("Prod Year: " + AD.ASCIIString(datalist, 11, 2))
print ("Prod Week: " + AD.ASCIIString(datalist, 13, 2))
print ("Serial#:   " + AD.ASCIIString(datalist, 15, 4))
xored = 0x00
for t in datalist[0:19+1]:
    xored = xored ^ t
if (xored == 0x5A):
    print ("Checksum is correct!")
else:
    print ("--- Checksum error! ---")    
#This function closes devices opened by the calling process
AD.CloseAD2()


