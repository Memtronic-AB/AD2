"""
   Writes the article numer, serial numer and everything to the eeprom of the CEFI board
   Author:  Martin Andersson
   Revision:  2023-08-16

   Requires:                       
       Python 3
"""

from ctypes import *
import time
import AD2
import Boule

TX = (c_byte*2)()

AD=AD2.AD2()
AD.OpenAD2(3)
AD.InitI2C (1e5, 0, 1)
Bo = Boule.Boule()

barcode = input ("Please enter barcode string:")
if (len(barcode) != 17):
    print ("Wrong length of string read from barcode.")
    raise

board = Boule.ARTICLETYPE.get(barcode[0:7], "--")
if (board == "CEFI"):
    # set IO expander to all outputs
    I2C_ADR = 0x23      # 7-bit I2C address to IO expander PCA9534:0
    TX[0] = c_byte(0x03)
    TX[1] = c_byte(0x00)
    AD.dwf.FDwfDigitalI2cWrite(AD.hdwf, c_int(I2C_ADR<<1), TX, c_int(2), byref(AD.iNak)) # write 2 bytes

    # set WP (write protect signal) to low to enable programming
    TX[0] = c_byte(0x01)
    TX[1] = c_byte(0xfe)
    AD.dwf.FDwfDigitalI2cWrite(AD.hdwf, c_int(I2C_ADR<<1), TX, c_int(2), byref(AD.iNak)) # write 2 bytes
    I2C_ADR = 0x53      # 7-bit I2C address to eeprom
elif (board == "CEDI"):
    I2C_ADR = 0x54      # 7-bit I2C address to eeprom
    
elif (board == "CELI"):
     # set IO expander to all outputs
    I2C_ADR = 0x41      # 7-bit I2C address to io expander PCA9536:0
    TX[0] = c_byte(0x03)
    TX[1] = c_byte(0x00)
    AD.dwf.FDwfDigitalI2cWrite(AD.hdwf, c_int(I2C_ADR<<1), TX, c_int(2), byref(AD.iNak)) # write 2 bytes

    # set WP (write protect signal) to low to enable programming
    TX[0] = c_byte(0x01)
    TX[1] = c_byte(0xfe)
    AD.dwf.FDwfDigitalI2cWrite(AD.hdwf, c_int(I2C_ADR<<1), TX, c_int(2), byref(AD.iNak)) # write 2 bytes
    I2C_ADR = 0x54      # 7-bit I2C address to eeprom
elif (board == "CELC"):
     # set IO expander output bit 0 low to enable programming
    I2C_ADR = 0x62      # 7-bit I2C address to io expander PCA9533:0
    TX[0] = c_byte(0x05)
    TX[1] = c_byte(0x01)
    AD.dwf.FDwfDigitalI2cWrite(AD.hdwf, c_int(I2C_ADR<<1), TX, c_int(2), byref(AD.iNak)) # write 2 bytes
    I2C_ADR = 0x55      # 7-bit I2C address to eeprom
elif (board == "CECC" or board == "CESC"):
     # set IO expander to all outputs
    I2C_ADR = 0x24      # 7-bit I2C address to io expander PCA9570:0. Set WP (write protect signal) to low to enable programming
    TX[0] = c_byte(0xFE)
    AD.dwf.FDwfDigitalI2cWrite(AD.hdwf, c_int(I2C_ADR<<1), TX, c_int(1), byref(AD.iNak)) # write 2 bytes
    I2C_ADR = 0x55      # 7-bit I2C address to eeprom
elif (board == "CEOI"):
    I2C_ADR = 0x54      # 7-bit I2C address to eeprom
elif (board == "CEGC"):
    I2C_ADR = 0x57
#elif (board == "CEOD"):
#elif (board == "CEID"):
else:
    print ("Unknown article number.")
    raise


s=Bo.barcode2eepromstring(barcode)
adr=0
for i in range (0,len(s)-1,2):
    TX[0] = c_byte(adr)
    adr=adr+1
    TX[1]= c_byte(int(s[i]+s[i+1],16))
    time.sleep (0.01)
    AD.dwf.FDwfDigitalI2cWrite(AD.hdwf, c_int(I2C_ADR<<1), TX, c_int(2), byref(AD.iNak)) # write 2 bytes
    print (TX[1])

#This function closes devices opened by the calling process
AD.CloseAD2()

