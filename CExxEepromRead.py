"""
   Writes the article numer, serial numer and everything to the eeprom of the CEFI board
   Author:  Martin Andersson
   Revision:  2023-08-18

   Requires:                       
       Python 3
"""

from ctypes import *
import AD2
import Boule

TX = (c_byte*2)()

AD=AD2.AD2()
AD.OpenAD2(3)
AD.InitI2C (1e5, 0, 1)
Bo = Boule.Boule()

board = input ("What type of board are you connected to (e.g. 'CEFI'):")
board=board.upper()
if (board == "CEFI"):
    I2C_ADR = 0x53      # 7-bit I2C address to eeprom
elif (board == "CEDI" or board == "CEOI" or board == "CELI"):
    I2C_ADR = 0x54      
elif (board == "CECC" or board == "CELC" or board == "CESC"):
    I2C_ADR = 0x55
elif (board == "CEOD" or board == "CEID"):
    I2C_ADR = 0x52
elif (board == "CEVC" or board == "CESI"):
    I2C_ADR = 0x50
elif (board == "CEGC"):
    I2C_ADR = 0x57    
else:
    print ("Error! Unknown board type.")
    raise

adr=0
SIZE = 20
adr = (c_ubyte*1)()
rgRX = (c_ubyte*1)()
RX = (c_ubyte*SIZE)()
iNak = c_int()

#read  data starting at address pointer (adr:0x00)

for i in range(0,SIZE):
    adr = (c_ubyte*1)(i)
    AD.dwf.FDwfDigitalI2cWrite(AD.hdwf, c_int(I2C_ADR<<1), adr, c_int(1), byref(iNak)) # write 1 bytes address
    AD.dwf.FDwfDigitalI2cRead(AD.hdwf, c_int(I2C_ADR<<1), rgRX, c_int(1), byref(iNak)) # read 1 bytes of data
    RX[i] = rgRX[0]
    
article = ""
for i in RX[2:9]:
    article += chr(i)
rev = ""
for i in RX[9:11]:
    rev += chr(i)
year = ""    
for i in RX[11:13]:
    year += chr(i)
week = ""
for i in RX[13:15]:
    week += chr(i)
serial = ""
for i in RX[15:19]:
    serial += chr(i)
crc_calc = 0x5A
for i in RX[0:19]:
    crc_calc ^= int(i)

print ("Board:   "+ Boule.ARTICLENAME.get(int(RX[1]), "--"))
print ('Article: '+ article)
print ('Rev:     ' + rev)
print ('Year:    ' + year)
print ('Week:    ' + week)
print ('Serial:  ' + serial)
if (RX[19] == crc_calc):
    print ('CRC:     OK (' +ascii(hex(crc_calc)) + ')')
else:
    print ('CRC:     Not correct. Calculated: ' +ascii(hex(crc_calc)) + ', EEPROM: ' + ascii(hex(RX[19])))

#This function closes devices opened by the calling process
AD.CloseAD2()

