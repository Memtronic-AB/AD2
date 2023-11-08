import AD2
import time
from ctypes import *
import numpy

AD=AD2.AD2()
AD.OpenAD2(3)           # initiates the AD2 with configuration 3

rgbTX = (c_ubyte*10)(0,1,2,3,4,5,6,7,8,9)
rgdw = c_uint32()
PARAM_ADR = {'ABS_POS':0x01,'EL_POS':0x02,'MARK':0x03, 'TVAL':0x09,'T_FAST':0x0E,'TON_MIN':0x0f,'TOFF_MIN':0x10,'ADC_OUT':0x12,'OCD_TH':0x13,'STEP_MODE':0x16,'ALARM_EN':0x17,'CONFIG':0x18,'STATUS':0x19}
PARAM_LEN = {'ABS_POS':22,'EL_POS':9,'MARK':22, 'TVAL':7,'T_FAST':8,'TON_MIN':7,'TOFF_MIN':7,'ADC_OUT':5,'OCD_TH':4,'STEP_MODE':8,'ALARM_EN':8,'CONFIG':16,'STATUS':16}

AD.InitSPI(1e3,0,1,2,3,1)
#              CS,CLK,MOSI,MISO
AD.dwf.FDwfDigitalSpiWriteOne(AD.hdwf, c_int(0), c_int(0), c_int(0)) # start driving the channels, clock and data
AD.dwf.FDwfDigitalSpiSelect(AD.hdwf, c_int(0), c_int(1))                # set cs high as default


def GetStatus ():
    ''' Collects the status as 16 bits from the L6474 chip.'''    
    reply1 = c_uint32() 
    reply2 = c_uint32() 
    reply = c_uint32()
    
    print("Getting L6474 status.")
    AD.dwf.FDwfDigitalSpiSelect(AD.hdwf, c_int(0), c_int(0))                # set cs low
    AD.dwf.FDwfDigitalSpiWriteOne(AD.hdwf, c_int(1), c_int(8), c_uint(0xD0)) # write 1 byte to MOSI    
    AD.dwf.FDwfDigitalSpiSelect(AD.hdwf, c_int(0), c_int(1))                # set cs high again as default
    AD.dwf.FDwfDigitalSpiSelect(AD.hdwf, c_int(0), c_int(0))                # set cs low
    AD.dwf.FDwfDigitalSpiReadOne(AD.hdwf, c_int(1), c_int(8), byref(reply1)) # read 8 bits from MISO
    AD.dwf.FDwfDigitalSpiSelect(AD.hdwf, c_int(0), c_int(1))                # set cs high again as default
    AD.dwf.FDwfDigitalSpiSelect(AD.hdwf, c_int(0), c_int(0))                # set cs low
    AD.dwf.FDwfDigitalSpiReadOne(AD.hdwf, c_int(1), c_int(8), byref(reply2)) # read 8 bits from MISO
    AD.dwf.FDwfDigitalSpiSelect(AD.hdwf, c_int(0), c_int(1))                # set cs high again as default
    reply.value = (reply1.value << 8) | reply2.value
    if (reply.value & 0b0001000000000000):     # OCD (Over Current Detection) bit normal 
        print("OCD     = '1' - normal")         #
    else:
        print("OCD     = '0' - overcurrent detection")
    if (reply.value & 0b0000100000000000):     # TH_SD bit thermal shutdown
        print("TH_SD   = '1' - normal")
    else: 
        print("TH_SD   = '0' - thermal shutdown")
    if (reply.value & 0b0000010000000000):     # TH_WRN bit thermal warning
        print("TH_WRN  = '1' - normal")
    else:
        print("TH_WRN  = '0' - thermal warning")
    if (reply.value & 0b0000001000000000):     # UVLO bit undervoltage lockout
        print("UVLO    = '1' - normal")
    else:
        print("UVLO    = '0' - undervoltage lockout")
    if (reply.value & 0b0000000100000000):     # WRONG COMMAND
        print("WRONG   = '1' - Command was unknown")
    else:
        print("WRONG   = '0' - normal")
    if (reply.value & 0b0000000010000000):     # NOTPERFOMED CMD
        print("NOTPERF = '1' - Command not performed")
    else:
        print("NOTPERF = '0' - normal")
    if (reply.value & 0b0000000000010000):     # Direction
        print("DIR     = '1' - Forward")
    else:
        print("DIR     = '0' - Reverse")
    if (reply.value & 0b0000000000000001):     # High-Z
        print("HiZ     = '1' - High-Z")
    else:
        print("HiZ     = '0' - Drive")
    
def EnableDrive():
    '''Enable the power stage of the stepper driver.'''
    AD.dwf.FDwfDigitalSpiSelect(AD.hdwf, c_int(0), c_int(0))                # set cs low to indicate start
    AD.dwf.FDwfDigitalSpiWriteOne(AD.hdwf, c_int(1), c_int(8), c_uint(0xB8)) # write 1 byte to MOSI  
    AD.dwf.FDwfDigitalSpiSelect(AD.hdwf, c_int(0), c_int(1))                # set cs high again as default
   
def DisableDrive():
    '''Disable the power stage of the stepper driver.'''
    AD.dwf.FDwfDigitalSpiSelect(AD.hdwf, c_int(0), c_int(0))                # set cs low to indicate start
    AD.dwf.FDwfDigitalSpiWriteOne(AD.hdwf, c_int(1), c_int(8), c_uint(0xA8)) # write 1 byte to MOSI
    AD.dwf.FDwfDigitalSpiSelect(AD.hdwf, c_int(0), c_int(1))                # set cs high as default

def GetParam (param, resplen):
    '''Returns the value of the param-eter. Expected response length (resplen) for the parameter in question must be included. '''
    reply0 = c_uint32() 
    reply1 = c_uint32()
    reply2 = c_uint32() 
    param = param | 0x20                                                    # set bit 5 to create GetParam message
    AD.dwf.FDwfDigitalSpiSelect(AD.hdwf, c_int(0), c_int(0))                # set cs low to indicate start
    AD.dwf.FDwfDigitalSpiWriteOne(AD.hdwf, c_int(1), c_int(8), c_uint(param)) # write 1 byte to MOSI   
    AD.dwf.FDwfDigitalSpiSelect(AD.hdwf, c_int(0), c_int(1))                # set cs high again as default
    AD.dwf.FDwfDigitalSpiSelect(AD.hdwf, c_int(0), c_int(0))                # set cs low
    AD.dwf.FDwfDigitalSpiReadOne(AD.hdwf, c_int(1), c_int(8), byref(reply0)) # read 8 bits from MISO
    AD.dwf.FDwfDigitalSpiSelect(AD.hdwf, c_int(0), c_int(1))                # set cs high again as default
    if (resplen > 1):
        AD.dwf.FDwfDigitalSpiSelect(AD.hdwf, c_int(0), c_int(0))                # set cs low
        AD.dwf.FDwfDigitalSpiReadOne(AD.hdwf, c_int(1), c_int(8), byref(reply1)) # read 8 bits from MISO
        AD.dwf.FDwfDigitalSpiSelect(AD.hdwf, c_int(0), c_int(1))                # set cs high as default
    if (resplen > 2):
        AD.dwf.FDwfDigitalSpiSelect(AD.hdwf, c_int(0), c_int(0))                # set cs low
        AD.dwf.FDwfDigitalSpiReadOne(AD.hdwf, c_int(1), c_int(8), byref(reply2)) # read 8 bits from MISO
        AD.dwf.FDwfDigitalSpiSelect(AD.hdwf, c_int(0), c_int(1))                # set cs high as default
    if (resplen == 1):
        return reply0.value
    elif (resplen==2):    
        return reply0.value << 8 | reply1.value 
    elif (resplen==3):
        return reply0.value << 16 | reply1.value << 8 | reply2.value

def SetParam (param, value, len):
    '''Sets the "value" of the "param"-eter. Len is the length of the "value" in bytes'''
    value0 = c_uint32()     #LSB
    value1 = c_uint32()
    value2 = c_uint32()     #MSB
    value = c_uint32(value)
    value0 = value.value & 0xff
    
    if (len > 1):                   #minimum 1 byte of data
        value = value.value >> 8
        value1 = value & 0xff
    
    if (len > 2):
        value = value >> 8
        value2 = value & 0xff
    AD.dwf.FDwfDigitalSpiSelect(AD.hdwf, c_int(0), c_int(0))                # set cs low to indicate start
    AD.dwf.FDwfDigitalSpiWriteOne(AD.hdwf, c_int(1), c_int(8), c_uint(param)) # write 8 bit to MOSI
    AD.dwf.FDwfDigitalSpiSelect(AD.hdwf, c_int(0), c_int(1))                # set cs high as default
    if (len >= 3):
        AD.dwf.FDwfDigitalSpiSelect(AD.hdwf, c_int(0), c_int(0))                # set cs low
        AD.dwf.FDwfDigitalSpiWriteOne(AD.hdwf, c_int(1), c_int(8), c_uint(value2)) # write 8 bits to MOSI
        AD.dwf.FDwfDigitalSpiSelect(AD.hdwf, c_int(0), c_int(1))                # set cs high again as default
    if (len >= 2):
        AD.dwf.FDwfDigitalSpiSelect(AD.hdwf, c_int(0), c_int(0))                # set cs low
        AD.dwf.FDwfDigitalSpiWriteOne(AD.hdwf, c_int(1), c_int(8), c_uint(value1)) # write 8 bits to MOSI
        AD.dwf.FDwfDigitalSpiSelect(AD.hdwf, c_int(0), c_int(1))                # set cs high again as default
    AD.dwf.FDwfDigitalSpiSelect(AD.hdwf, c_int(0), c_int(0))                # set cs low
    AD.dwf.FDwfDigitalSpiWriteOne(AD.hdwf, c_int(1), c_int(8), c_uint(value0)) # write 8 bits to MOSI
    AD.dwf.FDwfDigitalSpiSelect(AD.hdwf, c_int(0), c_int(1))                # set cs high again as default

def NumBytes (bits):
    '''Returns the number of full bytes it takes to hold a given number of bits. Only works for bits <= 24.'''
    if (bits > 16):
        return 3
    elif (bits > 8):
        return 2
    else:
        return 1

def RunSteps (dir, steps, step_delay):
    '''Runs the motor a certain number of "steps" in "dir"-ection. "step_delay" as an inverted speed setting given in seconds.
    Only implemented for full-steps and fixed speed.'''
    pos = GetParam(PARAM_ADR.get('EL_POS'),NumBytes(PARAM_LEN.get('EL_POS')))
    pos = (pos & 0x180) >> 7    # only use fullstep bits
    for i in range (steps):
        if (dir != 0):
            pos = pos + 1
            if (pos >=4):
                pos = 0
        else:
            pos = pos - 1
            if (pos <= -1):
                pos = 3
        elpos = pos << 7
        SetParam(PARAM_ADR.get('EL_POS'),elpos, NumBytes(PARAM_LEN.get('EL_POS')))
        time.sleep(step_delay) 
    DisableDrive()
    # frågan är om man bör kontrollera status emellanåt?           

def SetConfig (TOFF, POW_SR, OC_SD):
    '''Sets the config register:
    TOFF: Off time for bridge. Given in us. (4-124)
    POW_SR: Programmable bridge slew rate setting (V/us) (0=320, 1=75, 2=110, 4=260)
    OC_SD: Over current event generates (1=bridge shutdown, 0=no shutdown)
    EN_TQREG: External torque setting is set to internal register (TVAL) 
    EXT_CLK, OSC_SEL: are set to internal oscillator (16MHz) and osc pins unused.'''
    TOFF2 = TOFF>>2             # presented by 5 bits therefore shifted down two steps.
    SetParam(PARAM_ADR.get('CONFIG'),((TOFF2 << 10) & (POW_SR << 8) & (OC_SD << 7)), NumBytes(PARAM_LEN.get('CONFIG')))

def SetRefCurrent (current): 
    '''Sets the TVAL register for reference torque current (0.3125 - 4 A).'''   
    SetParam(PARAM_ADR.get('TVAL'),int(current/0.03125), NumBytes(PARAM_LEN.get('TVAL')))

def SetOvercurrentThreshold (threshold):
    '''Sets the threshold at which an overcurrent event occurs (0.375 - 6A).'''
    SetParam(PARAM_ADR.get('OCD_TH'),int(threshold/0.375), NumBytes(PARAM_LEN.get('OCD_TH')))

def SetMinOnTime (time):
    '''Sets the minimum on time for the bridge. Given in us (0.5 - 64 us)'''
    SetParam(PARAM_ADR.get('TON_MIN'),int(time/0.5), NumBytes(PARAM_LEN.get('TON_MIN')))

def SetMinOffTime (time):
    '''Sets the minimum off time for the bridge. Given in us (0.5 - 64 us)'''
    SetParam(PARAM_ADR.get('TOFF_MIN'),int(time/0.5), NumBytes(PARAM_LEN.get('TOFF_MIN')))

def SetMaxFastDecayTime (time):
    '''Sets the maximum fast decay time for the bridge. Given in us (2 - 32 us)'''
    val = GetParam(PARAM_ADR.get('T_FAST'),NumBytes(PARAM_LEN.get('T_FAST')))
    SetParam(PARAM_ADR.get('T_FAST'),((val & 0x0f) | (int(time/2) << 4)), NumBytes(PARAM_LEN.get('T_FAST')))

def SetMaxFallStepTime (time):
    '''Sets the maximum fall step time for the bridge. Given in us (2 - 32 us)'''
    val = GetParam(PARAM_ADR.get('T_FAST'),NumBytes(PARAM_LEN.get('T_FAST')))
    SetParam(PARAM_ADR.get('T_FAST'),((val & 0xf0) | (int(time/2))), NumBytes(PARAM_LEN.get('T_FAST')))


GetStatus()
#SetConfig (40,4,1)                  # set config (same as default)
#AD.dwf.FDwfDigitalSpiReadOne(AD.hdwf, c_int(1), c_int(24), byref(rgdw)) # read 24 bits from MISO
#EnableDrive()
#GetStatus()
#DisableDrive()
#GetStatus()
#pos = GetParam(PARAM_ADR.get('TVAL'),NumBytes(PARAM_LEN.get('TVAL')))
#SetRefCurrent(0.5)                  # set reference current to 0.5A
#pos = GetParam(PARAM_ADR.get('TVAL'),NumBytes(PARAM_LEN.get('TVAL')))
#pos = GetParam(PARAM_ADR.get('OCD_TH'),NumBytes(PARAM_LEN.get('OCD_TH')))
#SetOvercurrentThreshold (1.0)       # set overcurrent threshold to 1.0A
#pos = GetParam(PARAM_ADR.get('OCD_TH'),NumBytes(PARAM_LEN.get('OCD_TH')))
EnableDrive()
GetStatus()
pos = GetParam(PARAM_ADR.get('ABS_POS'),NumBytes(PARAM_LEN.get('ABS_POS')))
print ("ABS Position:"+str(pos))
pos = GetParam(PARAM_ADR.get('EL_POS'),NumBytes(PARAM_LEN.get('EL_POS')))
print ("EL Position:"+str(pos))
SetRefCurrent(0.9)                  # set reference current to 0.7A
RunSteps (0, 10, 0.4)
pos = GetParam(PARAM_ADR.get('EL_POS'),NumBytes(PARAM_LEN.get('EL_POS')))
print ("EL Position:"+str(pos))
pos = GetParam(PARAM_ADR.get('ABS_POS'),NumBytes(PARAM_LEN.get('ABS_POS')))
print ("ABS Position:"+str(pos))
#SetMinOnTime (20.5)                 # set min on time (same as default)
#SetMinOffTime (20.5)                # set min off time (same as default)
#SetMaxFallStepTime (5)              # set max fall step time (same as default)
#SetMaxFastDecayTime (1)             # set max fast decay time (same as default)
GetStatus()
AD.dwf.FDwfDeviceCloseAll()