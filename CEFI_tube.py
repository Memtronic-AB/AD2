"""
   Test to write to and read from a DAC5574
   Author:  Digilent, Inc. and Martin Andersson
   Revision:  2021-06-11

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
import math
import sys
import time
import csv
import AD2

AD = AD2.AD2()                  # 
AD.OpenAD2(3)                   # initiates the AD2 with configuration 3
AD.PowerCtrl(0,False,0,False)   # power off
AD.InitI2C (1e5, 0, 1)          # initiate I2C on SCL = DIO-1, SDA = DIO-0 at speed 100kHz 

# ------------- Communicate using I2C --------------
I2C_ADR = 0x2a      # 7-bit address
RX = (c_byte*4)()
TX = (c_byte*3)()       
for i in range (0,255):
    # set DAC to value
    TX[0] = 0x85    # write P6
    TX[1] = 0xCC
    AD.dwf.FDwfDigitalI2cWrite(AD.hdwf, c_int(I2C_ADR<<1), TX, c_int(2), byref(AD.iNak)) # write 3 bytes
    # read DAC back 
    TX[0] = 0x86
    AD.dwf.FDwfDigitalI2cWriteRead(AD.hdwf, c_int(I2C_ADR<<1), TX, c_int(1), RX, c_int(2), byref(AD.iNak)) # write 1 byte and read 2 bytes of data
    print ("0x86: " + str(RX[0]) + " - " + str(RX[1]))
    TX[0] = 0x87
    AD.dwf.FDwfDigitalI2cWriteRead(AD.hdwf, c_int(I2C_ADR<<1), TX, c_int(1), RX, c_int(2), byref(AD.iNak)) # write 1 byte and read 2 bytes of data
    print ("0x87: " + str(RX[0]) + " - " + str(RX[1]))

    # read ADC P6
    TX[0] = 0x82
    AD.dwf.FDwfDigitalI2cWriteRead(AD.hdwf, c_int(I2C_ADR<<1), TX, c_int(1), RX, c_int(2), byref(AD.iNak)) # write 1 byte and read 2 bytes of data
    print ("0x82: " + str(RX[0]) + " - " + str(RX[1]))

    # read ADC P9
    TX[0] = 0x83
    AD.dwf.FDwfDigitalI2cWriteRead(AD.hdwf, c_int(I2C_ADR<<1), TX, c_int(1), RX, c_int(2), byref(AD.iNak)) # write 1 byte and read 2 bytes of data
    print ("0x83: " + str(RX[0]) + " - " + str(RX[1]))

AD.CloseAD2()