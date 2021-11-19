"""
   Communicates with a DRV8823 drive circuit for motors or valves
   Author:  Martin Andersson
   Revision:  2020-06-23

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
import math
import sys
import time

#global ab_val1
#global cd_val1
global ab_val2 
global cd_val2 


# setBit() returns an integer with the bit at 'offset' set to 1.
def setBit(int_type, offset):
    mask = 1 << offset
    return(int_type | mask)
  
# clrBit() returns an integer with the bit at 'offset' cleared.
def clrBit(int_type, offset):
    mask = ~(1 << offset)
    return(int_type & mask)

def ConfigureSPI(speed_hz,dio_clk,dio_mosi,dio_miso):

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
    dwf.FDwfDigitalSpiOrderSet(hdwf, c_int(0)) # 0 LSB first

    # sets the CS pin - not used here 
    #                              DIO       value: 0 low, 1 high, -1 high impedance
    dwf.FDwfDigitalSpiSelect(hdwf, c_int(2), c_int(1)) # CS DIO-0 high
    # cDQ 0 SISO, 1 MOSI/MISO, 2 dual, 4 quad
    #                                cDQ       bits 0    data 0
    dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(0), c_int(0)) # start driving the channels, clock and data

def drv8823_reset ():
    # reset the chip -  SSTB1 = 0, SSTB0 = 0, nRESET = 0, nSLEEP = 1
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x10)) 
    time.sleep(0.1)
    # back to in-active state -  SSTB1 = 0, SSTB0 = 0, nRESET = 1, nSLEEP = 1
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x30)) 

# sets the state of a bridge (0-7) on a CEVC to state (0/1) and dir(ection) to 0/1
def drv8823_bridge_ctrl (bridge, state, dir, val_array):
    if (bridge == 0):
        if (state == 0):    val_array[0] = clrBit(val_array[0],0)
        else:               val_array[0] = setBit(val_array[0],0)
        if (dir == 0):      val_array[0] = clrBit(val_array[0],1)
        else:               val_array[0] = setBit(val_array[0],1)
        # send data to first chip
        dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(16), c_uint(val_array[0])) # write 16 bit to MOSI (DIO1)
        sstb_on = 0x70
    elif (bridge == 1):
        if (state == 0):    val_array[0] = clrBit(val_array[0],6)
        else:               val_array[0] = setBit(val_array[0],6)
        if (dir == 0):      val_array[0] = clrBit(val_array[0],7)
        else:               val_array[0] = setBit(val_array[0],7)
        # send data to first chip
        dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(16), c_uint(val_array[0])) # write 16 bit to MOSI (DIO1)
        sstb_on = 0x70
    elif (bridge == 2):
        if (state == 0):    val_array[1] = clrBit(val_array[1],0)
        else:               val_array[1] = setBit(val_array[1],0)
        if (dir == 0):      val_array[1] = clrBit(val_array[1],1)
        else:               val_array[1] = setBit(val_array[1],1)
        # send data to first chip
        dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(16), c_uint(val_array[1])) # write 16 bit to MOSI (DIO1)
        sstb_on = 0x70
    elif (bridge == 3):
        if (state == 0):    val_array[1] = clrBit(val_array[1],6)
        else:               val_array[1] = setBit(val_array[1],6)
        if (dir == 0):      val_array[1] = clrBit(val_array[1],7)
        else:               val_array[1] = setBit(val_array[1],7)
        # send data to first chip
        dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(16), c_uint(val_array[1])) # write 16 bit to MOSI (DIO1)
        sstb_on = 0x70    
    elif (bridge == 4):
        if (state == 0):    val_array[2] = clrBit(val_array[2],0)
        else:               val_array[2] = setBit(val_array[2],0)
        if (dir == 0):      val_array[2] = clrBit(val_array[2],1)
        else:               val_array[2] = setBit(val_array[2],1)
        # send data to first chip
        dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(16), c_uint(val_array[2])) # write 16 bit to MOSI (DIO1)
        sstb_on = 0xb0
    elif (bridge == 5):
        if (state == 0):    val_array[2] = clrBit(val_array[2],6)
        else:               val_array[2] = setBit(val_array[2],6)
        if (dir == 0):      val_array[2] = clrBit(val_array[2],7)
        else:               val_array[2] = setBit(val_array[2],7)
        # send data to second chip
        dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(16), c_uint(val_array[2])) # write 16 bit to MOSI (DIO1)
        sstb_on = 0xb0
    elif (bridge == 6):
        if (state == 0):    val_array[3] = clrBit(val_array[3],0)
        else:               val_array[3] = setBit(val_array[3],0)
        if (dir == 0):      val_array[3] = clrBit(val_array[3],1)
        else:               val_array[3] = setBit(val_array[3],1)
        dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(16), c_uint(val_array[3])) # write 16 bit to MOSI (DIO1)
        sstb_on = 0xb0
    elif (bridge == 7):
        if (state == 0):    val_array[3] = clrBit(val_array[3],6)
        else:               val_array[3] = setBit(val_array[3],6)
        if (dir == 0):      val_array[3] = clrBit(val_array[3],7)
        else:               val_array[3] = setBit(val_array[3],7)
        # send data to first chip
        dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(16), c_uint(val_array[3])) # write 16 bit to MOSI (DIO1)
        sstb_on = 0xb0
    # ------ clock the data 
    # set startup value - SSTB1 = x, SSTB0 = x, nRESET = 1, nSLEEP = 1
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(sstb_on)) 
    time.sleep (0.01)
    # set startup value - SSTB1 = 0, SSTB0 = 0, nRESET = 1, nSLEEP = 1
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x30)) 
    return val_array

def openValve (valve, val_array):
    val_array = drv8823_bridge_ctrl (valve,1,0, val_array) #turn desired bridge to state 1 (dir = 0)
    time.sleep (0.020)
    val_array = drv8823_bridge_ctrl (valve,0,0, val_array) #turn desired bridge to state 0 (dir = 0)
    return val_array

def closeValve (valve, val_array):
    val_array = drv8823_bridge_ctrl (valve,1,1, val_array) #turn desired bridge to state 1 (dir = 1)
    time.sleep (0.006)
    val_array = drv8823_bridge_ctrl (valve,0,1, val_array) #turn desired bridge to state 0 (dir = 1)
    return val_array

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

val_array = [0x071c, 0x171c, 0x071c, 0x171c]
#--------------------- Configure SPI -----------------
            #speed_hz,dio_clk,dio_mosi,dio_miso
ConfigureSPI(1e6,0,1,2)

#-------------------- Set digital control signals ----------------------
# nSLEEP = 4    unknown behaviour
# nRESET = 5    active low - set to high at all time
# SSTB0 = 6     set to low to control first chip. End with a high pulse. 
# SSTB1 = 7     set to low to control second chip. End with a high pulse.

# enable output/mask on high nibble of low byte IO pins, from DIO 4 to 7
dwf.FDwfDigitalIOOutputEnableSet(hdwf, c_int(0x00F0)) 

drv8823_reset ()        # reset chip
for i in range (0,8):
    val_array = openValve (i,val_array)
    time.sleep (1)
    val_array = closeValve (i,val_array)
    time.sleep (1)

# ------------------  test bridge 0-1 (P1-P2) ---------------

val_array = drv8823_bridge_ctrl (0,1,0, val_array) #turn bridge 0 to state 1 (dir = 0)
val_array = drv8823_bridge_ctrl (0,1,1, val_array) #turn bridge 0 to state 1 (dir = 1)
val_array = drv8823_bridge_ctrl (1,1,1, val_array) #turn bridge 1 to state 1 (dir = 1)
val_array = drv8823_bridge_ctrl (0,0,0, val_array) #turn bridge 0 to state 0 (dir = 0)
val_array = drv8823_bridge_ctrl (1,0,1, val_array) #turn bridge 1 to state 0 (dir = 1)

# ------------------  test bridge 2-3 (P3-P4) ---------------

val_array = drv8823_bridge_ctrl (2,1,0, val_array) #turn bridge 2 to state 1 (dir = 0)
val_array = drv8823_bridge_ctrl (3,1,1, val_array) #turn bridge 3 to state 1 (dir = 1)
val_array = drv8823_bridge_ctrl (3,0,1, val_array) #turn bridge 3 to state 0 (dir = 1)
val_array = drv8823_bridge_ctrl (2,0,1, val_array) #turn bridge 2 to state 0 (dir = 1)

# ------------------  test bridge 4-5 (P5-P6) ---------------
val_array = drv8823_bridge_ctrl (4,1,0, val_array) #turn bridge 4 to state 1 (dir = 0)
val_array = drv8823_bridge_ctrl (5,1,1, val_array) #turn bridge 5 to state 1 (dir = 1)
val_array = drv8823_bridge_ctrl (5,0,1, val_array) #turn bridge 5 to state 0 (dir = 1)
val_array = drv8823_bridge_ctrl (4,0,1, val_array) #turn bridge 4 to state 0 (dir = 1)


# ------------------  test bridge 6-7 (P7-P8) ---------------

val_array = drv8823_bridge_ctrl (6,1,0, val_array) #turn bridge 6 to state 1 (dir = 0)
val_array = drv8823_bridge_ctrl (7,1,1, val_array) #turn bridge 7 to state 1 (dir = 1)
val_array = drv8823_bridge_ctrl (7,0,1, val_array) #turn bridge 7 to state 0 (dir = 1)
val_array = drv8823_bridge_ctrl (6,0,1, val_array) #turn bridge 6 to state 0 (dir = 1)

# ------------ Turn ALL 


dwf.FDwfDeviceCloseAll()
