"""
   Communicates with the LM75B temperature sensing IC via I2C
   Author:  Martin Andersson
   Revision:  2021-06-01

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
import time
import AD2

AD=AD2.AD2()            # 
AD.OpenAD2(3)           # initiates the AD2 with configuration 3

#------------- Switch on power to the board - 3.3VDC --------------------
AD.PowerCtrl (3.3,True,0,False)
time.sleep(1)
# ------------ Setup I2C communication on SCL = DIO-0, SDA = DIO-1 at speed 100kHz --------------
AD.InitI2C (1e5, 0, 1)

# ------------ Communicate using I2C --------------
rgTX = (c_ubyte*1)(0)
rgRX = (c_ubyte*2)()
I2C_ADR = 0x4
AD.dwf.FDwfDigitalI2cWrite(AD.hdwf, c_int(I2C_ADR<<1), rgTX, c_int(1), byref(AD.iNak)) # write 1 bytes

try:
    while True:

        AD.dwf.FDwfDigitalI2cRead(AD.hdwf, c_int(I2C_ADR<<1), rgRX, c_int(2), byref(AD.iNak)) # read 2 bytes
        if AD.iNak.value != 0:
            print("NAK "+str(AD.iNak.value))
        temp = (((rgRX[0] << 8) | rgRX[1]) >> 5)/8
        print (temp)
        time.sleep(1)
except KeyboardInterrupt:
    pass

#This function closes devices opened by the calling process
AD.dwf.FDwfDeviceCloseAll()