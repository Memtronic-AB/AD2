"""
   Communicates with a DRV8823 drive circuit for bistable valves. Small CLI for controlling one or all valves.
   Used with patch cables to connect between AD2 and CEVC.
   Author:  Martin Andersson
   Revision:  2020-10-13

   Requires:                       
       Python 3, AnalogDiscovery SDK

    V0.1    2020-10-13  First version - for patch cables
    V0.2    2021-11-19  Updated to work with AD2-CEVC interface hardware 
"""

from ctypes import *
import math
import sys
import time

#global ab_val1
#global cd_val1
global ab_val2 
global cd_val2 

#CONSTANTS
SPI_SPEED = 1E5
SPI_CLK = 5
SPI_MOSI = 3
SPI_MISO = 8    # not used
NSLEEP = 7
NRESET = 2
SSTB0 = 6
SSTB1 = 4



def setBit(int_type, offset):
    '''setBit() returns an integer with the bit at 'offset' set to 1.'''
    mask = 1 << offset
    return(int_type | mask)
  

def clrBit(int_type, offset):
    '''clrBit() returns an integer with the bit at 'offset' cleared.'''
    mask = ~(1 << offset)
    return(int_type & mask)

def ConfigureSPI(speed_hz,dio_clk,dio_mosi,dio_miso):

    print("Configuring SPI...")
    # set the SPI frequency (in Hz)
    dwf.FDwfDigitalSpiFrequencySet(hdwf, c_double(speed_hz))

    # select which pin is SPI clock
    dwf.FDwfDigitalSpiClockSet(hdwf, c_int(dio_clk)) #DIO-0 = SPI_CLK

    # select which pin is SPI data
    dwf.FDwfDigitalSpiDataSet(hdwf, c_int(0), c_int(dio_mosi)) # 0 DQ0_MOSI_SISO 
    dwf.FDwfDigitalSpiDataSet(hdwf, c_int(1), c_int(dio_miso)) # 1 DQ1_MISO 

    # data mode specifies polarities (cpol and cpha)
    dwf.FDwfDigitalSpiModeSet(hdwf, c_int(0))   # mode = 0

    # Sets in which order the data is sent / received
    dwf.FDwfDigitalSpiOrderSet(hdwf, c_int(0)) # 0 LSB first

    # sets the CS pin - not used here 
    #                              DIO       value: 0 low, 1 high, -1 high impedance
    dwf.FDwfDigitalSpiSelect(hdwf, c_int(9), c_int(1)) # CS DIO-8 high
    # cDQ 0 SISO, 1 MOSI/MISO, 2 dual, 4 quad
    #                                cDQ       bits 0    data 0
    dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(0), c_int(0)) # start driving the channels, clock and data

def drv8823_reset ():
    # reset the chip -  SSTB1 = 0, SSTB0 = 0, nRESET = 0, nSLEEP = 1
    SetReset(0) 
    time.sleep(0.1)
    # back to in-active state -  SSTB1 = 0, SSTB0 = 0, nRESET = 1, nSLEEP = 1
    SetReset(1)

def SetSleep (state):
    ''' Controls the nSLEEP pin - state = 0 -> sleep; state = 1 -> awake'''
    temp = c_int()
    dwf.FDwfDigitalIOOutputGet (hdwf, byref(temp))
    if (state == 0):
        temp = temp.value & ~(0x01<<NSLEEP)
    else:
        temp = temp.value | (0x01<<NSLEEP)
    dwf.FDwfDigitalIOOutputSet(hdwf, temp) 

def SetReset (state):
    ''' controls the nRESET signal - state = 0 -> reset, state = 1 -> normal.'''
    temp = c_int()
    dwf.FDwfDigitalIOOutputGet (hdwf, byref(temp))
    if (state == 0):
        temp = temp.value & ~(0x01<<NRESET)
    else:    
        temp = temp.value | (0x01<<NRESET)
    dwf.FDwfDigitalIOOutputSet(hdwf, temp)         

def ClockSSTB (SSTB_sig):
    ''' clocks the SSTB0 or SSTB1 signal (active high) according to parameter SSTB_sig.'''
    temp = c_int()
    if (SSTB_sig == 0):
        mask = 0x01 << SSTB0
    else:
        mask = 0x01 << SSTB1
    dwf.FDwfDigitalIOOutputGet (hdwf, byref(temp))
    temp = temp.value | mask
    dwf.FDwfDigitalIOOutputSet(hdwf, temp)      # set SSTB
    time.sleep (0.01)
    temp = temp & ~mask
    dwf.FDwfDigitalIOOutputSet(hdwf, temp)      # clear SSTB


def drv8823_bridge_ctrl (bridge, state, dir, val_array):
    '''Sets the state of a bridge (0-7) on a CEVC to state (0/1) and dir(ection) to 0/1 (0=open, 1=close). The val_array is a number which is kept so that only the valve intended is changed and '''
    if (bridge == 0):
        if (state == 0):    val_array[0] = clrBit(val_array[0],0)
        else:               val_array[0] = setBit(val_array[0],0)
        if (dir == 0):      val_array[0] = clrBit(val_array[0],1)
        else:               val_array[0] = setBit(val_array[0],1)
        # send data to first chip
        dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(16), c_uint(val_array[0])) # write 16 bit to MOSI (DIO1)
    elif (bridge == 1):
        if (state == 0):    val_array[0] = clrBit(val_array[0],6)
        else:               val_array[0] = setBit(val_array[0],6)
        if (dir == 0):      val_array[0] = clrBit(val_array[0],7)
        else:               val_array[0] = setBit(val_array[0],7)
        # send data to first chip
        dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(16), c_uint(val_array[0])) # write 16 bit to MOSI (DIO1)
    elif (bridge == 2):
        if (state == 0):    val_array[1] = clrBit(val_array[1],0)
        else:               val_array[1] = setBit(val_array[1],0)
        if (dir == 0):      val_array[1] = clrBit(val_array[1],1)
        else:               val_array[1] = setBit(val_array[1],1)
        # send data to first chip
        dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(16), c_uint(val_array[1])) # write 16 bit to MOSI (DIO1)
    elif (bridge == 3):
        if (state == 0):    val_array[1] = clrBit(val_array[1],6)
        else:               val_array[1] = setBit(val_array[1],6)
        if (dir == 0):      val_array[1] = clrBit(val_array[1],7)
        else:               val_array[1] = setBit(val_array[1],7)
        # send data to first chip
        dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(16), c_uint(val_array[1])) # write 16 bit to MOSI (DIO1)
    elif (bridge == 4):
        if (state == 0):    val_array[2] = clrBit(val_array[2],0)
        else:               val_array[2] = setBit(val_array[2],0)
        if (dir == 0):      val_array[2] = clrBit(val_array[2],1)
        else:               val_array[2] = setBit(val_array[2],1)
        # send data to first chip
        dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(16), c_uint(val_array[2])) # write 16 bit to MOSI (DIO1)
    elif (bridge == 5):
        if (state == 0):    val_array[2] = clrBit(val_array[2],6)
        else:               val_array[2] = setBit(val_array[2],6)
        if (dir == 0):      val_array[2] = clrBit(val_array[2],7)
        else:               val_array[2] = setBit(val_array[2],7)
        # send data to second chip
        dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(16), c_uint(val_array[2])) # write 16 bit to MOSI (DIO1)
    elif (bridge == 6):
        if (state == 0):    val_array[3] = clrBit(val_array[3],0)
        else:               val_array[3] = setBit(val_array[3],0)
        if (dir == 0):      val_array[3] = clrBit(val_array[3],1)
        else:               val_array[3] = setBit(val_array[3],1)
        dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(16), c_uint(val_array[3])) # write 16 bit to MOSI (DIO1)
    elif (bridge == 7):
        if (state == 0):    val_array[3] = clrBit(val_array[3],6)
        else:               val_array[3] = setBit(val_array[3],6)
        if (dir == 0):      val_array[3] = clrBit(val_array[3],7)
        else:               val_array[3] = setBit(val_array[3],7)
        # send data to first chip
        dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(16), c_uint(val_array[3])) # write 16 bit to MOSI (DIO1)
    # ------ clock the data 
    if (bridge <= 3):
        ClockSSTB (0)
    else:
        ClockSSTB (1)        
    return val_array

def openValve (valve, val_array):
    '''Used to open the valve {valve} (0-7).'''
    val_array = drv8823_bridge_ctrl (valve,1,0, val_array) #turn desired bridge to state 1 (dir = 0)
    time.sleep (0.006)
    val_array = drv8823_bridge_ctrl (valve,0,0, val_array) #turn desired bridge to state 0 (dir = 0)
    return val_array

def closeValve (valve, val_array):
    '''Used to close the valve {valve} (0-7).'''
    val_array = drv8823_bridge_ctrl (valve,1,1, val_array) #turn desired bridge to state 1 (dir = 1)
    #time.sleep (0.002)
    val_array = drv8823_bridge_ctrl (valve,0,1, val_array) #turn desired bridge to state 0 (dir = 1)
    return val_array

def openAllValves (val_array):
    '''Used to open all eight valves simultaneously. Note these xxxAllValve routines do not handle reset sleep SSTB the same way as the other routines. There was not enough time for that.'''
    val_array = [0x075d, 0x175d, 0x075d, 0x175d]    # to open all bridges for valve open
    dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(16), c_uint(val_array[0])) # write 16 bit to MOSI (DIO1)
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x70))                               # clock data to 1st chip
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x30))
    dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(16), c_uint(val_array[1])) # write 16 bit to MOSI (DIO1)
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x70))                               # clock data to 1st chip
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x30))
    dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(16), c_uint(val_array[2])) # write 16 bit to MOSI (DIO1)
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0xb0))                               # clock data to 2nd chip
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x30)) 
    dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(16), c_uint(val_array[3])) # write 16 bit to MOSI (DIO1)
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0xb0))                               # clock data to 2nd chip
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x30)) 
    time.sleep (0.006)
    val_array = [0x071c, 0x171c, 0x071c, 0x171c]    # close all bridges
    dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(16), c_uint(val_array[0])) # write 16 bit to MOSI (DIO1)
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x70))                               # clock data to 1st chip
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x30))
    dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(16), c_uint(val_array[1])) # write 16 bit to MOSI (DIO1)
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x70))                               # clock data to 1st chip
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x30))
    dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(16), c_uint(val_array[2])) # write 16 bit to MOSI (DIO1)
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0xb0))                               # clock data to 2nd chip
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x30)) 
    dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(16), c_uint(val_array[3])) # write 16 bit to MOSI (DIO1)
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0xb0))                               # clock data to 2nd chip
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x30))
    return val_array    

def closeAllValves (val_array):
    '''Used to close all eight valves simultaneously.'''
    val_array = [0x07df, 0x17df, 0x07df, 0x17df]    # to open all bridges for valve close
    dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(16), c_uint(val_array[0])) # write 16 bit to MOSI (DIO1)
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x70))                               # clock data to 1st chip
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x30))
    dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(16), c_uint(val_array[1])) # write 16 bit to MOSI (DIO1)
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x70))                               # clock data to 1st chip
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x30))
    dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(16), c_uint(val_array[2])) # write 16 bit to MOSI (DIO1)
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0xb0))                               # clock data to 2nd chip
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x30)) 
    dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(16), c_uint(val_array[3])) # write 16 bit to MOSI (DIO1)
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0xb0))                               # clock data to 2nd chip
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x30)) 
    #time.sleep (0.006)
    val_array = [0x079e, 0x179e, 0x079e, 0x179e]    # close all bridges
    dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(16), c_uint(val_array[0])) # write 16 bit to MOSI (DIO1)
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x70))                               # clock data to 1st chip
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x30))
    dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(16), c_uint(val_array[1])) # write 16 bit to MOSI (DIO1)
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x70))                               # clock data to 1st chip
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x30))
    dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(16), c_uint(val_array[2])) # write 16 bit to MOSI (DIO1)
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0xb0))                               # clock data to 2nd chip
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x30)) 
    dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(16), c_uint(val_array[3])) # write 16 bit to MOSI (DIO1)
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0xb0))                               # clock data to 2nd chip
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x30))
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
ConfigureSPI(SPI_SPEED,SPI_CLK,SPI_MOSI,SPI_MISO)

#-------------------- Set digital control signals ----------------------
# nSLEEP    unknown behaviour
# nRESET    active low - set to high at all time
# SSTB0     set to low to control first chip. End with a high pulse. 
# SSTB1     set to low to control second chip. End with a high pulse.

# enable output/mask on high nibble of low byte IO pins, from DIO 4 to 7
dwf.FDwfDigitalIOOutputEnableSet(hdwf, c_int(0x00D4)) 

# Power on
dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(0), c_int(1), c_double(+3.3)) 
dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(0), c_int(0), c_double(1))
dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(1), c_int(1), c_double(0))
dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(1), c_int(0), c_double(0))
dwf.FDwfAnalogIOEnableSet(hdwf, c_int(True))

drv8823_reset ()        # reset chip
SetReset (1)
SetSleep (1)
print ("Valve control program. Type 'help' for help.")
while True:
    n=input(">")
    
    if n.strip() == 'q':
        break
    elif n.strip() == 'o':
        val_array = openAllValves(val_array)
    elif n.strip() == 'c':
        val_array = closeAllValves(val_array)   
    elif n.strip() == 'o0':
        val_array = openValve (0, val_array)
    elif n.strip() == 'o1':
        val_array = openValve (1, val_array)
    elif n.strip() == 'o2':
        val_array = openValve (2, val_array)
    elif n.strip() == 'o3':
        val_array = openValve (3, val_array)
    elif n.strip() == 'o4':
        val_array = openValve (4, val_array)
    elif n.strip() == 'o5':
        val_array = openValve (5, val_array)
    elif n.strip() == 'o6':
        val_array = openValve (6, val_array)    
    elif n.strip() == 'o7':
        val_array = openValve (7, val_array)
    elif n.strip() == 'c0':
        val_array = closeValve (0, val_array)
    elif n.strip() == 'c1':
        val_array = closeValve (1, val_array)
    elif n.strip() == 'c2':
        val_array = closeValve (2, val_array)
    elif n.strip() == 'c3':
        val_array = closeValve (3, val_array)
    elif n.strip() == 'c4':
        val_array = closeValve (4, val_array)
    elif n.strip() == 'c5':
        val_array = closeValve (5, val_array)
    elif n.strip() == 'c6':
        val_array = closeValve (6, val_array)    
    elif n.strip() == 'c7':
        val_array = closeValve (7, val_array)
    elif n.strip() == 's0':
        print ("-- sleeping --")
        SetSleep(0)
    elif n.strip() == 's1':
        print ("-- wakeup --")
        SetSleep (1)        
    elif n.strip() == 'r0':
        print ("-- reset --")
        SetReset(0)       
    elif n.strip() == 'r1':
        print ("-- no reset --")
        SetReset(1)        
    elif n.strip() == 'help':
        print ("o     :   open all valves")
        print ("c     :   close all valves")
        print ("o0    :   open valve #0")
        print ("c0    :   close valve #0")
        print ("s0    :   set nSLEEP pin to 0")
        print ("s1    :   set nSLEEP pin to 1")
        print ("r0    :   set nRESET pin to 0 - reset")
        print ("r1    :   set nRESET pin to 1 - normal")
        print ("q     :   quit\n")
    else:
        print ("Unknown command:-(")

dwf.FDwfDeviceCloseAll()
