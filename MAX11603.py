"""
   Test to write to and read from a ADC MAX11603
   Author:  Digilent, Inc.
   Revision:  2018-07-23

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
import math
import sys
import time
import matplotlib.pyplot as plt

def InitI2C (speed, SCL, SDA):
    ''' Initiates the I2C communication towards the Analog Discovery. Speed in Hz. SCL and SDA is the DIO pin number for the respective signal.'''
    # ------------ Setup I2C communication --------------
    print("Configuring I2C...")
    iNak = c_int()

    dwf.FDwfDigitalI2cRateSet(hdwf, c_double(speed)) # 100kHz
    dwf.FDwfDigitalI2cSclSet(hdwf, c_int(SCL)) # SCL = DIO-8
    dwf.FDwfDigitalI2cSdaSet(hdwf, c_int(SDA)) # SDA = DIO-9
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

# initiate I2C on SCL = DIO-8, SDA = DIO-9 at speed 100kHz 
InitI2C (1e5, 8, 9)

# ------------- Communicate using I2C --------------
DATAPOINTS = 100
rgTX = (c_ubyte*2)(0xAA,0x69) # Write Configuration and setup
rgRX = (c_ubyte*DATAPOINTS)()
iNak = c_int()
#                                8bit address  
dwf.FDwfDigitalI2cWrite(hdwf, c_int(0x6D<<1), rgTX, c_int(2), byref(iNak)) # write 2 bytes
time.sleep(0.1)

dwf.FDwfDigitalI2cRead(hdwf, c_int(0x6D<<1), rgRX, c_int(DATAPOINTS), byref(iNak)) # read 100 bytes

print ("Exiting program")

# for i in range (0,99):
#     print (rgRX[i])
plt.plot(rgRX)    
plt.show()
dwf.FDwfDeviceCloseAll()