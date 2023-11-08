"""
   Test to write to and read from a memory 24C02
   Author:  Digilent, Inc. and Martin Andersson
   Revision:  2023-10-30

   Requires:                       
       Python 3
"""

from ctypes import *
import time
import AD2

def printHelp ():
    print ("----------------------------------------------")
    print ("help menu: ")
    print ("r. Read memory and print on screen.")
    print ("f. Read memory and print to file.")
    print ("w. Write memory with same data to whole memory area.")
    print ("b. Set WC pin to write protect.")
    print ("c. Set WC pin to write enable.")
    print ("q. Quit program.")

def writeMem ():
    data = input ("What data do you want to write (hex format '0x33'):")
    num = int(data, 16)
    if (num < 0 or num > 255):
        print ("Invalid number!")
        raise

    # write data to all memory
    TX = (c_byte*2)()
    TX[1] = c_byte(num)
    for element in range(0,256):
        TX[0] = c_byte(element)
        time.sleep (0.01)
        AD.dwf.FDwfDigitalI2cWrite(AD.hdwf, c_int(I2C_MEM<<1), TX, c_int(2), byref(AD.iNak)) # write 2 bytes


def setMemWC (board, state):
    TX = (c_byte*2)()
    board = board.upper()
    if (board == "CEFI"):
        # set IO expander to all outputs
        I2C_ADR = 0x23      # 7-bit I2C address to IO expander PCA9534:0
        TX[0] = c_byte(0x03)
        TX[1] = c_byte(0x00)
        AD.dwf.FDwfDigitalI2cWrite(AD.hdwf, c_int(I2C_ADR<<1), TX, c_int(2), byref(AD.iNak)) # write 2 bytes

        # set WP (write protect signal) to low to enable programming
        TX[0] = c_byte(0x01)
        if (state == 1):
            TX[1] = c_byte(0xff)
        else:
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
        if (state == 1):
            TX[1] = c_byte(0xff)
        else:
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
        if (state == 1):
            TX[0] = c_byte(0xFF)
        else:
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

def readMem (board, choise):
    adr = (c_ubyte*1)()
    rgRX = (c_ubyte*1)()
    row1 = "     x0   x1   x2   x3   x4   x5   x6   x7   x8   x9   xA   xB   xC   xD   xE   xF\n"
    row2 = "----------------------------------------------------------------------------------\n"
    row3 = "0x:  "
    row = 0x0
    # if print on screen
    if (choise.lower() == 'r'):
        print (row1 + row2 + row3, end="") 
    else:
        filename = board.upper() + "readfile.txt"
        writefile = open (filename, 'w+',newline='')
        writefile.write(row1 + row2 + row3)
   
    for i in range(0,256):
        adr = (c_ubyte*1)(i)
        AD.dwf.FDwfDigitalI2cWrite(AD.hdwf, c_int(I2C_MEM<<1), adr, c_int(1), byref(AD.iNak)) # write 1 bytes address
        AD.dwf.FDwfDigitalI2cRead(AD.hdwf, c_int(I2C_MEM<<1), rgRX, c_int(1), byref(AD.iNak)) # read 1 bytes of data
        # if print on screen
        if (choise.lower() == 'r'):
            print (hex(rgRX[0]) + " ", end="")
            if ((i+1) % 16 == 0 and i < 250):
                row =row + 1
                print ("\n" + hex(row)[2:3] + "x:  ", end="")
        # else to file
        else:
            data = hex(rgRX[0])
            writefile.write(data + " ")
            if ((i+1) % 16 == 0 and i < 250):
                row =+ 1
                writefile.write("\n" + hex(row)[2:3] + "x:  ")
    print ("")
    if (choise.lower() == 'f'):            
        writefile.close()    


AD=AD2.AD2()
AD.OpenAD2(3)
AD.PowerCtrl(3.3,True,0,False)   # power to pullups from internal PSU
time.sleep(1)

# initiate I2C on SCL = DIO-1, SDA = DIO-0 at speed 100kHz 
AD.InitI2C (1e5, 0, 1)

# ------------- Set up for each board --------------
board = input("Which board are you testing (e.g. CELI):")
if (board.lower() == "celi"):
    I2C_MEM = 0x54      
elif (board.lower() == "cefi"):
    I2C_MEM = 0x53      
elif (board.lower() == "cecc"):
    I2C_MEM = 0x55
elif (board.lower() == "cesc"):
    I2C_MEM = 0x56
elif (board.lower() == "cesi"):
    I2C_MEM = 0x50
elif (board.lower() == "ceoi"):
    I2C_MEM = 0x54
elif (board.lower() == "cedi"):
    I2C_MEM = 0x54
elif (board.lower() == "ceod"):
    I2C_MEM = 0x52
elif (board.lower() == "ceid"):
    I2C_MEM = 0x52
elif (board.lower() == "cevc"):
    I2C_MEM = 0x50

print ("Memory test program. Type 'h' for help.")
while True:
    choise=input(">")

    # ------------ Read data from memory ----------------
    if (choise.lower() == "r" or choise.lower() == 'f'):
        readMem(board, choise)    
    #--------------- Write data to memory ---------------------
    elif (choise.lower() == "w"):
        writeMem()
    elif (choise.lower() == "b"):
        setMemWC (board, 1)
    elif (choise.lower() == "c"):
        setMemWC (board, 0)
    elif (choise.lower() == "h"):
        printHelp()
    elif (choise.lower() == "q"):
        break
    else:
        print ("Unknown command")

#This function closes devices opened by the calling process
AD.CloseAD2()

