"""
   Test to write to a DAC MCP4706A0 and read the ADC values from an ADC121C027
   Author:  Digilent, Inc. and Martin Andersson
   Revision:  2021-05-17

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
import math
import sys
import time
import csv

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
#dwf.FDwfAnalogIOEnableSet(hdwf, c_int(False))
dwf.FDwfAnalogIOEnableSet(hdwf, c_int(True))
time.sleep(2)
# initiate I2C on SCL = DIO-0, SDA = DIO-01 at speed 100kHz 
InitI2C (1e5, 0, 1)

# ------------- Communicate using I2C --------------
rgRX = (c_ubyte*2)()
iNak = c_int()
I2C_ADR_DAC = 0x61      # 7-bit address for DAC
I2C_ADR_ADC = 0x51      # 7-bit address for ADC
TX = (c_ubyte*2)()
TX[0] = c_ubyte(0x00)

# set DAC register and read ADC -> write data to file
print ("Testing, please wait!")
writefile = open ("tubedetector.txt", 'w+',newline='')
for TX[1] in range (0,190):
    dwf.FDwfDigitalI2cWrite(hdwf, c_int(I2C_ADR_DAC<<1), TX, c_int(2), byref(iNak)) # write 2 bytes to DAC output register
    time.sleep(0.5)
    dwf.FDwfDigitalI2cRead(hdwf, c_int(I2C_ADR_ADC<<1), rgRX, c_int(2), byref(iNak)) # read 2 bytes of data from ADC
    adc_val = (((rgRX[0] & 0x0f) << 8) | rgRX[1])
    writefile.write(str(TX[1])+ ";"+ str(adc_val)+"\n")
writefile.close()
# turn off current generator
TX[1] = 0
dwf.FDwfDigitalI2cWrite(hdwf, c_int(I2C_ADR_DAC<<1), TX, c_int(2), byref(iNak)) # write 2 bytes to DAC output register

# # Read data from ADC conversion register
# while True:
#     ans=input("Press Enter to make ADC reading. x finishes.")
#     if (ans=="x"):
#         break
#     dwf.FDwfDigitalI2cRead(hdwf, c_int(I2C_ADR_ADC<<1), rgRX, c_int(2), byref(iNak)) # read 2 bytes of data from ADC
#     adc_val = (((rgRX[0] & 0x0f) << 8) | rgRX[1])
#     print (str(adc_val),"(",hex(rgRX[0]), hex(rgRX[1]),")")

# # Write data to DAC output register
# while True:
#     element = input ("Enter value in hex (e.g 1f). Quit with x.")
#     if (element == "x"):
#         break
#     dec_element = int(element,16)
#     TX[1] = c_byte(dec_element)
#     print (hex(dec_element), dec_element)
#     dwf.FDwfDigitalI2cWrite(hdwf, c_int(I2C_ADR_DAC<<1), TX, c_int(2), byref(iNak)) # write 2 bytes

# master disable power
dwf.FDwfAnalogIOEnableSet(hdwf, c_int(False))

#This function closes devices opened by the calling process
print ("Exiting program")
dwf.FDwfDeviceCloseAll()