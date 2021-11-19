"""
   Test to write to and read from a memory 24C02
   Author:  Digilent, Inc. and Martin Andersson
   Revision:  2020-09-01

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
import math
import sys
import time
import csv

def InitI2C (speed, SCL, SDA):
    ('''def InitI2C (speed, SCL, SDA)
    ''')
    # ------------ Setup I2C communication --------------
    print("Configuring I2C...")
    iNak = c_int()

    dwf.FDwfDigitalI2cRateSet(hdwf, c_double(speed)) # 100kHz
    dwf.FDwfDigitalI2cSclSet(hdwf, c_int(SCL)) # SCL
    dwf.FDwfDigitalI2cSdaSet(hdwf, c_int(SDA)) # SDA
    dwf.FDwfDigitalI2cClear(hdwf, byref(iNak))
    if iNak.value == 0:
        print("I2C bus error. Check the pull-ups.")
        quit()
    #time.sleep(1)


if sys.platform.startswith("win"):
    dwf = cdll.LoadLibrary("dwf.dll")
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

hdwf = c_int()

print("Opening first device")
#dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))
# device configuration of index 3 (4th) for Analog Discovery has 16kS digital-in/out buffer
dwf.FDwfDeviceConfigOpen(c_int(-1), c_int(3), byref(hdwf)) 

if hdwf.value == 0:
    print("failed to open device")
    szerr = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szerr)
    print(str(szerr.value))
    quit()

# enable positive supply
dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(0), c_int(0), c_double(True)) 
# set voltage to 3.3 V
dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(0), c_int(1), c_double(3.3)) 
# master enable
dwf.FDwfAnalogIOEnableSet(hdwf, c_int(True))

# initiate I2C on SCL = DIO-1, SDA = DIO-0 at speed 100kHz 
InitI2C (1e5, 1, 0)

# ------------- Communicate using I2C --------------
rgTX = (c_ubyte*1)(0x00) # Address data pointer
adr = (c_ubyte*1)()
rgRX = (c_ubyte*1)()
iNak = c_int()
I2C_ADR = 0x54      # 7-bit address

strang = 'Nog finns det mål och mening i vår färd Men det är vägen, som är mödan värd'
langd= len(strang)
#read data at address pointer (adr:0)
dwf.FDwfDigitalI2cWrite(hdwf, c_int(I2C_ADR<<1), rgTX, c_int(1), byref(iNak)) # write 1 bytes address
dwf.FDwfDigitalI2cRead(hdwf, c_int(I2C_ADR<<1), rgRX, c_int(1), byref(iNak)) # read 1 bytes of data
print (rgTX[0])
print (rgRX[0])

# # write data to adr:0
# TX = (c_byte*2)(0x00, 0xaa)
# dwf.FDwfDigitalI2cWrite(hdwf, c_int(I2C_ADR<<1), TX, c_int(2), byref(iNak)) # write 2 bytes

# #read data at address pointer (adr:00)
# adr = (c_ubyte*1)(0x00)
# dwf.FDwfDigitalI2cWrite(hdwf, c_int(I2C_ADR<<1), adr, c_int(1), byref(iNak)) # write 1 bytes address
# dwf.FDwfDigitalI2cRead(hdwf, c_int(I2C_ADR<<1), rgRX, c_int(1), byref(iNak)) # read 1 bytes of data
# print (rgRX[0])

# write data to all memory
TX = (c_byte*2)()
TX[1] = c_byte(0xaa)
for element in range(0,256):
    TX[0] = c_byte(element)
    
    dwf.FDwfDigitalI2cWrite(hdwf, c_int(I2C_ADR<<1), TX, c_int(2), byref(iNak)) # write 2 bytes


#write data to adr:0
# TX = (c_byte*2)()
# for element in range(0,len(strang)):
#     TX[0] = c_byte(element)
#     TX[1] = c_byte(ord(strang[element]))

#     dwf.FDwfDigitalI2cWrite(hdwf, c_int(I2C_ADR<<1), TX, c_int(2), byref(iNak)) # write 2 bytes

# #read data at address pointer (adr:0xE1)
# adr = (c_ubyte*1)(0x00)
# dwf.FDwfDigitalI2cWrite(hdwf, c_int(I2C_ADR<<1), adr, c_int(1), byref(iNak)) # write 1 bytes address
# dwf.FDwfDigitalI2cRead(hdwf, c_int(I2C_ADR<<1), rgRX, c_int(1), byref(iNak)) # read 1 bytes of data
# print (rgRX[0])


# master disable power
dwf.FDwfAnalogIOEnableSet(hdwf, c_int(False))

#This function closes devices opened by the calling process
print ("Exiting program")
dwf.FDwfDeviceCloseAll()