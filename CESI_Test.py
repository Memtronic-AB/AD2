# CESI test program
# Communicates with the absolute encoder and reports the rotational position of the axle

from ctypes import *
import csv
import math
import sys
import time
import numpy as np

def InitI2C (speed, SCL, SDA):
    # ------------ Setup I2C communication --------------
    print("Configuring I2C...")
    iNak = c_int()

    dwf.FDwfDigitalI2cRateSet(hdwf, c_double(speed)) # 100kHz
    dwf.FDwfDigitalI2cSclSet(hdwf, c_int(SCL)) # SCL = DIO-1
    dwf.FDwfDigitalI2cSdaSet(hdwf, c_int(SDA)) # SDA = DIO-0
    dwf.FDwfDigitalI2cClear(hdwf, byref(iNak))
    if iNak.value == 0:
        print("I2C bus error. Check the pull-ups.")
        quit()
    


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
dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(0), c_int(0), c_double(True)) 
# set voltage to 3.3 V
dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(0), c_int(1), c_double(3.3)) 
# master enable
dwf.FDwfAnalogIOEnableSet(hdwf, c_int(True))

time.sleep(0.5)

# initiate I2C on SCL = DIO-1, SDA = DIO-0 at speed 400kHz 
InitI2C (4e5, 1, 0)

# ------------- Communicate using I2C --------------
rgRX = (c_ubyte*2)()
iNak = c_int()
I2C_ADR = 0x36      # 7-bit address of CESI
     
rgTX = (c_ubyte*1)(0x0c) # read raw angle
with open ("angle.csv", 'a+',newline='') as logfile:
        log_writer = csv.writer(logfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for i in range (1,5000):
            dwf.FDwfDigitalI2cWriteRead(hdwf, c_int(I2C_ADR<<1), rgTX, c_int(1), rgRX, c_int(2), byref(iNak)) # read 2 bytes of data
            high = rgRX[0]
            low = rgRX[1]
            angle =  high << 8 | low
            text = "High: " + hex(high) + ", Low: " + hex(low) + ", Angle: " + str(angle)
            print (text)
            #time.sleep (1)
            log_writer.writerow([hex(high), hex(low), str(angle)])
logfile.close()
# master disable power
dwf.FDwfAnalogIOEnableSet(hdwf, c_int(False))

#This function closes devices opened by the calling process
print ("Exiting program")
dwf.FDwfDeviceCloseAll()