"""
   Communicates with an LM75B temp sensor. Address pins set to all zero
   Author:  Martin Andersson
   Revision:  2021-11-22

   Requires:                       
       Python 3
"""

from ctypes import *
import time
import AD2

# Constants
ADR = 0x49          # address pins set to "001"

AD = AD2.AD2()
AD.OpenAD2(3)
AD.PowerCtrl(3.3, True, 0, False)
time.sleep(0.5)
AD.InitI2C (1e5, 0,1)                  # Setup I2C communication on SCL = DIO-1, SDA = DIO-0 at speed 100kHz --------------

# ------------- Communicate using I2C --------------
rgTX = (c_ubyte*1)(0)
rgRX = (c_ubyte*2)()

#                                8bit address  
AD.dwf.FDwfDigitalI2cWrite(AD.hdwf, c_int(ADR<<1), rgTX, c_int(1), byref(AD.iNak)) # write 1 bytes
time.sleep(0.1)


try:
    while True:
        AD.dwf.FDwfDigitalI2cRead(AD.hdwf, c_int(ADR<<1), rgRX, c_int(2), byref(AD.iNak)) # read 2 bytes
        if AD.iNak.value != 0:
            print("NAK "+str(AD.iNak.value))
        #print(list(rgRX))
        temp = (((rgRX[0] << 8) | rgRX[1]) >> 5)/8
        print (temp)
        time.sleep(1)
except KeyboardInterrupt:
    pass

#This function closes devices opened by the calling process
AD.dwf.FDwfDeviceCloseAll()