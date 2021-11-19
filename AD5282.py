"""
   Test hack för att kommunicera länge med en AD5282 Seriell potentiometer 
   Slår på 1.8 V 
   Rampar resistansen och mäter spänningen över en spänningsdelare
   Author:  Digilent, Inc.
   Revision:  2021-05-24

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
import AD2
import time

AD = AD2.AD2()
AD.OpenAD2(3)
AD.PowerCtrl(1.8,True,0,False)

# ------------ Setup I2C communication on SCL = DIO-1, SDA = DIO-0 at speed 100kHz --------------
AD.InitI2C (1e5, 0, 1)

time.sleep (1)    # wait 1 sec to power up


# ------------- Communicate using I2C --------------
rgTX = (c_ubyte*2)(0)
rgRX = (c_ubyte*2)()

#                                8bit address  
#Top sensor left position (furthest from connector)
address1 = 0x2d
instruction_byte1 = 0x00

#Top sensor middle position
address2 = 0x2c
instruction_byte2 = 0x80

#Top sensor right position (closest to connector)
address3 = 0x2c
instruction_byte3 = 0x00

#Bottom sensor left position (furthest from connector)
address4 = 0x2e
instruction_byte4 = 0x80

#Bottom sensor middle position
address5 = 0x2e
instruction_byte5 = 0x00

#Bottom sensor right position (closest to connector)
address6 = 0x2d
instruction_byte6 = 0x80

I2C_ADR = 0x2d     # 7-bit address
rgTX[0] = 0x80
round = 0
temp = 0
voltage1 = c_double()
voltage2 = c_double()

wfile = open("resdata.txt","w+",newline='')

for res in range (256):
    rgTX[1] = res
    
    AD.dwf.FDwfDigitalI2cWrite(AD.hdwf, c_int(I2C_ADR<<1), rgTX, c_int(2), byref(AD.iNak)) # write 2 bytes
    time.sleep(0.05)
    AD.dwf.FDwfAnalogInStatus(AD.hdwf, False, None) 
    AD.dwf.FDwfAnalogInStatusSample(AD.hdwf, c_int(0), byref(voltage1))
    AD.dwf.FDwfAnalogInStatusSample(AD.hdwf, c_int(1), byref(voltage2))
    
    print (str(res)+" : " +str(voltage1.value))
    data = str(res)+";" +str(voltage1.value)+"\n"
    wfile.write(data)

wfile.close()
    
    
    
#This function closes devices opened by the calling process
AD.dwf.FDwfDeviceCloseAll()