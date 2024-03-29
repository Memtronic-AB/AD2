# Valve position test program
# Version 1.0 2020-12-xx Moving only one valve
# Version 2.0 2021-01-13 Moving 8 valves on one valve board and saving to 8 files.
# Version 3.0 2021-01-18 Moving 8 valves on one valve board and saving to 8 files. Here we also calculate slope for a number of setups.
#                        the format of the saved file is also improved.                        

from ctypes import *
import csv
import math
import sys
import time
import numpy as np
import re

def slopeCalc (x,y):
    ''' Calculates the slope from two lists of values (x and y) using linear curve fit.
    Requires that the length of x and y are the same.'''
    sumx = 0
    sumy = 0
    sumxy = 0
    sumx2 = 0
    length = len(x)
    for i in range(0,length):   
        sumx +=x[i]
        sumy += y[i]
        sumxy += x[i] * y[i]
        sumx2 += x[i] * x[i]
    
    return (length * sumxy - sumx * sumy) *100 / (length * sumx2 - sumx * sumx)

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

# initiate I2C on SCL = DIO-0, SDA = DIO-1 at speed 100kHz 
InitI2C (1e5, 0, 1)

# ------------- Communicate using I2C --------------
rgRX = (c_ubyte*10)()
iNak = c_int()
I2C_ADR = 0x28      # 7-bit address of CELI
x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] # x-values (even sampling intervals) for slope calculation
VALVES, DIR, TESTS = 8,2,10

# start position sense
rgTX = (c_ubyte*1)(0xf8)
dwf.FDwfDigitalI2cWrite(hdwf, c_int(I2C_ADR<<1), rgTX, c_int(1), byref(iNak)) # write 1 bytes address

# sense all 10 samples
rgTX = (c_ubyte*2)(0xf6, 0x0a)
dwf.FDwfDigitalI2cWrite(hdwf, c_int(I2C_ADR<<1), rgTX, c_int(2), byref(iNak)) # write 2 bytes address

valveMatrix =np.array([['1','2','3','4','5','6','7','8'],[0xe0,0xe1,0xe2,0xe3,0xe4,0xe5,0xe6,0xe7],[0xb0,0xb1,0xb2,0xb3,0xb4,0xb5,0xb6,0xb7]])
resMatrix = [[["" for x in range(VALVES)] for y in range(DIR)] for z in range (TESTS)]

# perform all loops 
for test in range (0,TESTS):
    for direction in range (0,DIR):
        for valve in range (0,VALVES):
            if (direction % 2 == 0): 
                i2c = int(valveMatrix[2][valve])
                rgTX = (c_ubyte*2)(i2c) # Open valve 
                print ('Opening valve...')
            else:
                print ('Closing valve...')
                i2c = int(valveMatrix[1][valve])
                rgTX = (c_ubyte*2)(i2c) # Close valve
            cmd = hex(rgTX[0])
            dwf.FDwfDigitalI2cWrite(hdwf, c_int(I2C_ADR<<1), rgTX, c_int(1), byref(iNak)) # write 1 bytes address
            time.sleep(1)
            rgTX = (c_ubyte*2)(0xf7) # Get slope values
            dwf.FDwfDigitalI2cWriteRead(hdwf, c_int(I2C_ADR<<1), rgTX, c_int(1), rgRX, c_int(10), byref(iNak)) # read 10 bytes of data
            y =[]
            for i in range (0,10):      #adds the curve values to list
                y.append(rgRX[i])
            y.append(cmd)
            for i in range (2,7):       #adds the slope values to list 0-1:0-6?
                y.append(slopeCalc(x[0:i], y[0:i]))
            for i in range(3,7):        #adds the slope values to list 1-2:1-6?
                y.append(slopeCalc(x[1:i], y[1:i]))    
            resMatrix[test][direction][valve] = y
            resstring = 'Test: ' + str(test) + ', Direction: ' + str(direction) + ', Valve: ' + str(valve) + ', Result: ' + str(y)
            print (resstring)
            
        # end valve loop    
    # end direction loop        
# end for test loop 



# write the collected data to the files. One file for open and one for close operations
for valve in range (0,VALVES):
    fileNameOpen= valveMatrix[0][valve]+'logopen.csv'
    fileNameClose= valveMatrix[0][valve]+'logclose.csv'
    logfileopen = open (fileNameOpen, 'a+',newline='')
    logfileclose = open (fileNameClose, 'a+',newline='')
    for test in range (0,TESTS):
            log_writer_open = csv.writer(logfileopen, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            log_writer_close = csv.writer(logfileclose, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            log_writer_open.writerow(resMatrix[test][0][valve])
            log_writer_close.writerow(resMatrix[test][1][valve])

    logfileopen.close()
    logfileclose.close()



# master disable power
dwf.FDwfAnalogIOEnableSet(hdwf, c_int(False))

#This function closes devices opened by the calling process
print ("Exiting program")
dwf.FDwfDeviceCloseAll()