"""
   Reads the contents 256-byte from a memory 24C02 and writes it to "readfile.txt"
   Author: Martin Andersson
   Revision:  2021-06-18

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
import AD2

AD = AD2.AD2()
AD.OpenAD2(3)
AD.PowerCtrl(0,False,0,False)

# initiate I2C on SCL = DIO-0, SDA = DIO-1 at speed 100kHz 
AD.InitI2C (1e5, 0, 1)

# ------------- Communicate using I2C --------------
adr = (c_ubyte*1)()
rgRX = (c_ubyte*1)()
I2C_ADR = 0x50      # 7-bit address

#read all data from EEPROM to a computer file, starting at address pointer (adr:0x00)
writefile = open ("CELIreadfile.txt", 'w+',newline='')
for i in range(0,256):
    adr = (c_ubyte*1)(i)
    AD.dwf.FDwfDigitalI2cWrite(AD.hdwf, c_int(I2C_ADR<<1), adr, c_int(1), byref(AD.iNak)) # write 1 bytes address
    AD.dwf.FDwfDigitalI2cRead(AD.hdwf, c_int(I2C_ADR<<1), rgRX, c_int(1), byref(AD.iNak)) # read 1 bytes of data
    print (str(i) + ' : ' +str(rgRX[0]))
    data = str(i) +';' + str(rgRX[0])+';' +chr(rgRX[0])+'\n'
    writefile.write(data)
writefile.close()    

# master disable power
AD.dwf.FDwfAnalogIOEnableSet(AD.hdwf, c_int(False))

#This function closes devices opened by the calling process
print ("Exiting program")
AD.dwf.FDwfDeviceCloseAll()