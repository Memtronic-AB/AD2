"""
   Communicates with a TMC5130A drive circuit for stepper motors
   Author:  Martin Andersson
   Revision:  2020-11-25

   Requires:                       
       Python 3
"""

from ctypes import *
import math
import sys
import time
import numpy

TMC5130A_IHOLD_IRUN = 0x10
TMC5130A_CHOPCONF = 0x6c

PIN_CS = 0
PIN_SCK = 1
PIN_MOSI = 2
PIN_MISO = 3
PIN_ENABLE = 4

def ConfigureSPI(speed_hz,dio_clk,dio_mosi,dio_miso,dio_cs):

    print("Configuring SPI...")
    # set the SPI frequency (in Hz)
    dwf.FDwfDigitalSpiFrequencySet(hdwf, c_double(speed_hz))

    # select which pin is SPI clock
    dwf.FDwfDigitalSpiClockSet(hdwf, c_int(dio_clk)) #DIO-0 = SPI_CLK

    # select which pin is SPI data
    dwf.FDwfDigitalSpiDataSet(hdwf, c_int(0), c_int(dio_mosi)) # 0 DQ0_MOSI_SISO = DIO-1
    dwf.FDwfDigitalSpiDataSet(hdwf, c_int(1), c_int(dio_miso)) # 1 DQ1_MISO = DIO-3

    # data mode specifies polarities (I think....)
    dwf.FDwfDigitalSpiModeSet(hdwf, c_int(0))

    # Sets in which order the data is sent / received
    dwf.FDwfDigitalSpiOrderSet(hdwf, c_int(1)) # 1 MSB first

    # sets the CS pin - not used here 
    #                              DIO       value: 0 low, 1 high, -1 high impedance
    dwf.FDwfDigitalSpiSelect(hdwf, c_int(dio_cs), c_int(1)) # CS DIO-0 high
    # cDQ 0 SISO, 1 MOSI/MISO, 2 dual, 4 quad
    #                                cDQ       bits 0    data 0
    dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(dio_mosi), c_int(0), c_int(0)) # start driving the channels, clock and data


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

#--------------------- Configure SPI -----------------
            #speed_hz,dio_clk,dio_mosi,dio_miso,dio_cs
ConfigureSPI(1e6,PIN_SCK,PIN_MOSI,PIN_MISO,PIN_CS)


rx = (c_ubyte*5)()

def TMC5130A_WriteRead (adr, wdata, rdata):
    """ Writes wdata (32 bits) to register with address adr and returns the data read back via reference rdata."""
    tx = (c_ubyte*5)()
    tx[0] = (adr | 0x80)    # set highest bit = 1 (write)
    tx[1] = (wdata & 0xFF000000) >> 32
    tx[2] = (wdata & 0x00ff0000) >> 16
    tx[3] = (wdata & 0x00ff0000) >> 8
    tx[4] = (wdata & 0x00ff0000)
    dwf.FDwfDigitalSpiSelect(hdwf, c_int(PIN_CS), c_int(0)) # CS DIO-0 low
    dwf.FDwfDigitalSpiWriteRead(hdwf, c_int(1), c_int(8), tx, c_int(5), rdata, c_int(5)) # write 40 bit to MOSI and read from MISO
    dwf.FDwfDigitalSpiSelect(hdwf, c_int(PIN_CS), c_int(1)) # CS DIO-0 high

def TMC5130A_Read (adr, rdata):
    """ Reads rdata (5 bytes) via reference from register with address adr. The first byte is the SPI status."""
    tx = (c_ubyte*5)()
    tx[0] = adr
    tx[1] = tx[2] = tx[3] = tx[4] = 0x00
    dwf.FDwfDigitalSpiSelect(hdwf, c_int(PIN_CS), c_int(0)) # CS DIO-0 low
    dwf.FDwfDigitalSpiWriteRead(hdwf, c_int(1), c_int(8), tx, c_int(5), rdata, c_int(5)) # write 40 bit to MOSI and read from MISO
    dwf.FDwfDigitalSpiSelect(hdwf, c_int(PIN_CS), c_int(1)) # CS DIO-0 high
    print ("RX:"+' 0x%02x' % rdata[0] +' 0x%02x' % rdata[1] +' 0x%02x' % rdata[2] +' 0x%02x' % rdata[3] +' 0x%02x' % rdata[4])    
    dwf.FDwfDigitalSpiSelect(hdwf, c_int(PIN_CS), c_int(0)) # CS DIO-0 low
    dwf.FDwfDigitalSpiWriteRead(hdwf, c_int(1), c_int(8), tx, c_int(5), rdata, c_int(5)) # write 40 bit to MOSI and read from MISO
    dwf.FDwfDigitalSpiSelect(hdwf, c_int(PIN_CS), c_int(1)) # CS DIO-0 high


# write to CHOPCONF - register
TMC5130A_WriteRead (TMC5130A_CHOPCONF, 0x000080c4, byref(rx))
#print ("RX:"+' 0x%02x' % rx[0] +' 0x%02x' % rx[1] +' 0x%02x' % rx[2] +' 0x%02x' % rx[3] +' 0x%02x' % rx[4])

# write to IHOLD_IRUN - register 
TMC5130A_WriteRead (TMC5130A_IHOLD_IRUN, 0x00010501, byref(rx))
#print ("RX:"+' 0x%02x' % rx[0] +' 0x%02x' % rx[1] +' 0x%02x' % rx[2] +' 0x%02x' % rx[3] +' 0x%02x' % rx[4])



#read from CHOPCONF register 
TMC5130A_Read (TMC5130A_CHOPCONF, byref(rx))    
print ("RX:"+' 0x%02x' % rx[0] +' 0x%02x' % rx[1] +' 0x%02x' % rx[2] +' 0x%02x' % rx[3] +' 0x%02x' % rx[4])

dwf.FDwfDeviceCloseAll()