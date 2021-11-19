"""
   DWF Python Example
   Author:  Digilent, Inc.
   Revision:  2018-07-23

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
import math
import sys
import time

if sys.platform.startswith("win"):
    dwf = cdll.LoadLibrary("dwf.dll")
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

hdwf = c_int()
iNak = c_int()

def InitI2C (speed, SCL, SDA):
    ('''def InitI2C (speed, SCL, SDA)
    ''')
    # ------------ Setup I2C communication --------------
    print("Configuring I2C...")
    dwf.FDwfDigitalI2cRateSet(hdwf, c_double(speed)) # 100kHz
    dwf.FDwfDigitalI2cSclSet(hdwf, c_int(SCL)) # SCL
    dwf.FDwfDigitalI2cSdaSet(hdwf, c_int(SDA)) # SDA
    dwf.FDwfDigitalI2cClear(hdwf, byref(iNak))
    if iNak.value == 0:
        print("I2C bus error. Check the pull-ups.")
        quit()
    #time.sleep(1)

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

#------------- Switch on power to the board - 3.3VDC --------------------
print ("Powering up....")
# enable positive supply
dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(0), c_int(0), c_double(True)) 
# set voltage to 3.3 V
dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(0), c_int(1), c_double(3.3)) 
# master enable
dwf.FDwfAnalogIOEnableSet(hdwf, c_int(True))

time.sleep (1)    # wait 1 sec to power up

# ------------ Setup I2C communication on SCL = DIO-1, SDA = DIO-0 at speed 100kHz --------------
InitI2C (1e5, 1, 0)

# ------------- Communicate using I2C --------------
rgTX = (c_ubyte*1)(0)
rgRX = (c_ubyte*2)()

#                                8bit address  
dwf.FDwfDigitalI2cWrite(hdwf, c_int(0x4e<<1), rgTX, c_int(1), byref(iNak)) # write 1 bytes
time.sleep(0.1)

try:
    while True:

        dwf.FDwfDigitalI2cRead(hdwf, c_int(0x4e<<1), rgRX, c_int(2), byref(iNak)) # read 2 bytes
        if iNak.value != 0:
            print("NAK "+str(iNak.value))
        #print(list(rgRX))
        temp = (((rgRX[0] << 8) | rgRX[1]) >> 5)/8
        print (temp)
        time.sleep(1)
except KeyboardInterrupt:
    pass

#This function closes devices opened by the calling process
dwf.FDwfDeviceCloseAll()