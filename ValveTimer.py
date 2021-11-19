"""
   Small timer program which flashes an output DIO-0 to open a valve which lets 
   diluent through the shear valve. 
   Author:  Martin Andersson
   Revision:  2020-11-17

   Requires:                       
       Python 3
"""

from ctypes import *
import math
import sys
import time

# setBit() returns an integer with the bit at 'offset' set to 1.
def setBit(int_type, offset):
    mask = 1 << offset
    return(int_type | mask)
  
# clrBit() returns an integer with the bit at 'offset' cleared.
def clrBit(int_type, offset):
    mask = ~(1 << offset)
    return(int_type & mask)


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

# enable output/mask on DIO0
dwf.FDwfDigitalIOOutputEnableSet(hdwf, c_int(0x0001))     
# enable positive supply
dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(0), c_int(0), c_double(True)) 
# set voltage to 0 V
dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(0), c_int(1), c_double(0.0)) 
# master enable
dwf.FDwfAnalogIOEnableSet(hdwf, c_int(True))    

while (True):
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x01)) 
    # set voltage to 4.5 V
    dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(0), c_int(1), c_double(4.5)) 
    
    
    time.sleep(2)
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x00)) 
    # set voltage to 0 V
    dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(0), c_int(1), c_double(0)) 
    time.sleep(16)