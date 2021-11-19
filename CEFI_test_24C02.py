"""
   Test to write to and read from a memory 24C02
   Author:  Digilent, Inc. and Martin Andersson
   Revision:  2021-06-18

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
import time
import AD2

AD=AD2.AD2()
AD.OpenAD2(3)
AD.PowerCtrl(0,False,0,False)   # power from external PSU

# initiate I2C on SCL = DIO-1, SDA = DIO-0 at speed 100kHz 
AD.InitI2C (1e5, 0, 1)

# ------------- Communicate using I2C --------------
strang = 'Nog finns det mål och mening i vår färd Men det är vägen, som är mödan värd'

# # ----------- set up IC7 - PCA9536 IO expander -----------
# I2C_ADR = 0x41      # 7-bit address
# rgTX = (c_ubyte*2)(0x03, 0x00)  # Configuration byte (03) set to output (00)
# AD.dwf.FDwfDigitalI2cWrite(AD.hdwf, c_int(I2C_ADR<<1), rgTX, c_int(2), byref(AD.iNak)) # write configuration to output
# rgTX = (c_ubyte*2)(0x01, 0x00)  # Output byte (01) set to low state (00)
# AD.dwf.FDwfDigitalI2cWrite(AD.hdwf, c_int(I2C_ADR<<1), rgTX, c_int(2), byref(AD.iNak)) # write output state IO0 = low = write controlled

# ------------ Read data from memory ----------------
adr = (c_ubyte*1)()
rgRX = (c_ubyte*1)()

I2C_ADR = 0x50      # 7-bit address
# langd= len(strang)
# #read data at address pointer (adr:0)
# AD.dwf.FDwfDigitalI2cWrite(AD.hdwf, c_int(I2C_ADR<<1), rgTX, c_int(1), byref(AD.iNak)) # write 1 bytes address
# AD.dwf.FDwfDigitalI2cRead(AD.hdwf, c_int(I2C_ADR<<1), rgRX, c_int(1), byref(AD.iNak)) # read 1 bytes of data
# print (rgTX[0])
# print (rgRX[0])

# write data to all memory
TX = (c_byte*2)()
TX[1] = c_byte(0x55)
for element in range(0,256):
    TX[0] = c_byte(element)
    time.sleep (0.01)
    AD.dwf.FDwfDigitalI2cWrite(AD.hdwf, c_int(I2C_ADR<<1), TX, c_int(2), byref(AD.iNak)) # write 2 bytes

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

#This function closes devices opened by the calling process
AD.CloseAD2()

