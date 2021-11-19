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
I2C_ADR = 0x4c      # 7-bit address

TX = (c_byte*3)()       
TX[0] = c_byte(0x12)    # control byte: write directly to ch A
while True:
    element = input ("Enter value in hex (e.g 1f). Quit with x.")
    if (element == "x"):
        break
    dec_element = int(element,16)
    TX[1] = c_byte(dec_element)
    print (hex(dec_element), dec_element)
    AD.dwf.FDwfDigitalI2cWrite(AD.hdwf, c_int(I2C_ADR<<1), TX, c_int(3), byref(AD.iNak)) # write 3 bytes

AD.CloseAD2()