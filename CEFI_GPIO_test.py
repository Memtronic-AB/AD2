"""
   Test hack som användes när CEFI testades
   Author:  Digilent, Inc.
   Revision:  2021-05-31

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

def AD2PowerCtrl (posvalue, pos_on, negvalue, neg_on):
    '''def AD2PowerCtrl (posvalue, pos_on, negvalue, neg_on)'''   
    # set positive voltage
    dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(0), c_int(1), c_double(posvalue)) 
    # enable positive supply
    dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(0), c_int(0), c_double(pos_on))
    
    # set negative voltage
    dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(1), c_int(1), c_double(negvalue))
    # enable negative supply
    dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(1), c_int(0), c_double(neg_on))

    if (pos_on == True or neg_on == True):
        print ("Powering up....")
        # master enable
        dwf.FDwfAnalogIOEnableSet(hdwf, c_int(True))
    else:
        # master enable
        dwf.FDwfAnalogIOEnableSet(hdwf, c_int(False))
    

def AD2InitI2C (speed, SCL, SDA):
    '''Sets up I2C communication with:\n 
    speed = transmission speed in Hz\n
    SCL = pin number for the I2C clock line\n
    SDA = pin number for the I2C data line\n'''
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

# ------------ make sure power is off
AD2PowerCtrl (3.3, False, -3.3, False)

# ------------ Setup I2C communication on SCL = DIO-0, SDA = DIO-1 at speed 100kHz --------------
AD2InitI2C (1e5, 0, 1)

# ------------- Communicate using I2C --------------
rgTX = (c_ubyte*2)(0)
rgRX = (c_ubyte*2)()
I2C_ADR = 0x2a
rgTX[0] = 0x50
dwf.FDwfDigitalI2cWriteRead(hdwf, c_int(I2C_ADR<<1), rgTX, c_int(1), rgRX, c_int(2), byref(iNak)) # write 1 byte and read 2 bytes of data
print("Connector P1:"+str(list(rgRX)))

rgTX[0] = 0x51
dwf.FDwfDigitalI2cWriteRead(hdwf, c_int(I2C_ADR<<1), rgTX, c_int(1), rgRX, c_int(2), byref(iNak)) # write 1 byte and read 2 bytes of data
print("Connector P2:"+str(list(rgRX)))

rgTX[0] = 0x10
dwf.FDwfDigitalI2cWriteRead(hdwf, c_int(I2C_ADR<<1), rgTX, c_int(1), rgRX, c_int(2), byref(iNak)) # write 1 byte and read 2 bytes of data
print("Connector P3:"+str(list(rgRX)))

rgTX[0] = 0x11
dwf.FDwfDigitalI2cWriteRead(hdwf, c_int(I2C_ADR<<1), rgTX, c_int(1), rgRX, c_int(2), byref(iNak)) # write 1 byte and read 2 bytes of data
print("Connector P4:"+str(list(rgRX)))


#This function closes devices opened by the calling process
dwf.FDwfDeviceCloseAll()