"""
   Reads the contents 256-byte from a memory 24C02 and writes it to "readfile.txt"
   Author: Martin Andersson
   Revision:  2021-05-10

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
import math
import sys
import time
import csv

def InitI2C (speed, SCL, SDA):
    '''Sets up I2C communication with:\n 
    speed = transmission speed in Hz\n
    SCL = pin number for the I2C clock line\n
    SDA = pin number for the I2C data line\n
    '''
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
dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(0), c_int(0), c_double(False)) 
# set voltage to 3.3 V
dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(0), c_int(1), c_double(3.3)) 
# master enable
dwf.FDwfAnalogIOEnableSet(hdwf, c_int(False))

# initiate I2C on SCL = DIO-0, SDA = DIO-1 at speed 100kHz 
InitI2C (1e5, 0, 1)

# ------------- Communicate using I2C --------------
adr = (c_ubyte*1)()
rgRX = (c_ubyte*1)()
iNak = c_int()
I2C_ADR = 0x53      # 7-bit address - CEFI
#I2C_ADR = 0x50      # 7-bit address - CEVC
#read all data starting at address pointer (adr:0x00)
writefile = open ("readfile.txt", 'w+',newline='')
for i in range(0,256):
    adr = (c_ubyte*1)(i)
    dwf.FDwfDigitalI2cWrite(hdwf, c_int(I2C_ADR<<1), adr, c_int(1), byref(iNak)) # write 1 bytes address
    dwf.FDwfDigitalI2cRead(hdwf, c_int(I2C_ADR<<1), rgRX, c_int(1), byref(iNak)) # read 1 bytes of data
    print (str(i) + ' : ' +str(rgRX[0]))
    #datawrite = csv.writer(writefile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    data = str(i) +';' + str(rgRX[0])+';' +chr(rgRX[0])+'\n'
    writefile.write(data)
writefile.close()    

# master disable power
dwf.FDwfAnalogIOEnableSet(hdwf, c_int(False))

#This function closes devices opened by the calling process
print ("Exiting program")
dwf.FDwfDeviceCloseAll()