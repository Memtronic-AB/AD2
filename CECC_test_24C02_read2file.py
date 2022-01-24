"""
   Reads the contents 256-byte from a memory 24C02 and writes it to "readfile.txt"
   Author: Martin Andersson
   Revision:  2021-05-10

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
import sys
import time
import AD2

AD=AD2.AD2()
AD.OpenAD2(3)
AD.PowerCtrl(3.3,True,0,False)   # power to pullups from internal PSU
time.sleep(1)
# initiate I2C on SCL = DIO-1, SDA = DIO-0 at speed 100kHz 
AD.InitI2C (1e5, 0, 1)

# ------------- Communicate using I2C --------------
adr = (c_ubyte*1)()
rgRX = (c_ubyte*1)()
iNak = c_int()
I2C_ADR = 0x55      # 7-bit address - CECC

#read all data starting at address pointer (adr:0x00)
writefile = open ("readfile.txt", 'w+',newline='')
for i in range(0,256):
    adr = (c_ubyte*1)(i)
    AD.dwf.FDwfDigitalI2cWrite(AD.hdwf, c_int(I2C_ADR<<1), adr, c_int(1), byref(iNak)) # write 1 bytes address
    AD.dwf.FDwfDigitalI2cRead(AD.hdwf, c_int(I2C_ADR<<1), rgRX, c_int(1), byref(iNak)) # read 1 bytes of data
    print (str(i) + ' : ' +str(rgRX[0]))
    #datawrite = csv.writer(writefile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    data = str(i) +';' + str(rgRX[0])+';' +chr(rgRX[0])+'\n'
    writefile.write(data)
writefile.close()    

print ("Exiting program")
#This function turns off power and closes devices opened by the calling process
AD.CloseAD2()