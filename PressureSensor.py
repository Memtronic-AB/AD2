"""
   Test to read from a Honeywell ABP2LANTxxxxx2A3xx pressure sensor
   Author:  Digilent, Inc. and Martin Andersson
   Revision:  2021-05-18

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
import sys
import time

def InitI2C (speed, SCL, SDA):
    ('''def InitI2C (speed, SCL, SDA)
    ''')
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
dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(0), c_int(0), c_double(True)) 
# set voltage to 3.3 V
dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(0), c_int(1), c_double(3.3)) 
# master enable
dwf.FDwfAnalogIOEnableSet(hdwf, c_int(False))
#dwf.FDwfAnalogIOEnableSet(hdwf, c_int(True))

# initiate I2C on SCL = DIO-1, SDA = DIO-0 at speed 100kHz 
InitI2C (1e5, 1, 0)

# ------------- Communicate using I2C --------------
rgRX = (c_ubyte*7)()       # receive data  
iNak = c_int()
I2C_ADR = 0x28      # 7-bit address for sensor

TX = (c_ubyte*3)(0xAA, 0x00, 0x00)

# ----------
outputmax = 15099494
outputmin = 1677722
pmax = 60   #psi
pmin = 0    #psi
time.sleep(5)

writefile = open ("pressurefile.txt", 'w+',newline='')

for i in range(200):
    dwf.FDwfDigitalI2cWrite(hdwf, c_int(I2C_ADR<<1), TX, c_int(3), byref(iNak)) # write 3 bytes command to start pressure conversion
    time.sleep(0.100)
    dwf.FDwfDigitalI2cRead(hdwf, c_int(I2C_ADR<<1), rgRX, c_int(7), byref(iNak)) # read 7 bytes of data from sensor
    print (hex(rgRX[0]),hex(rgRX[1]),hex(rgRX[2]),hex(rgRX[3]),hex(rgRX[4]),hex(rgRX[5]),hex(rgRX[6]))
    pres_count=(rgRX[1]<<16) | (rgRX[2]<<8) | rgRX[3]
    temp_count = (rgRX[4]<<16) | (rgRX[5]<<8) | rgRX[6]
    pressure = ((pres_count-outputmin)*(pmax-pmin))/(outputmax-outputmin)+pmin
    temp = (temp_count*200/16777215)-50 #°C
    print ("Pressure:" + str(pressure)+" Temp: "+str(temp))

    data = str(pressure) +';' + str(temp)+'\n'
    writefile.write(data)

writefile.close()  
# master disable power
dwf.FDwfAnalogIOEnableSet(hdwf, c_int(False))

#This function closes devices opened by the calling process
print ("Exiting program")
dwf.FDwfDeviceCloseAll()