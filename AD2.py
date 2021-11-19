"""
   DWF Analog Discovery 2 Lib
   Author:  Martin Andersson
   Revision:  2021-06-01

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *

import time
import sys

class AD2():

    def __init__ (self):
        self.hdwf = c_int()
        self.iNak = c_int()
        self.dwf = c_int()

    def OpenAD2 (self, configuration):    
        '''Initiates and opens the AD2 device with the given configuration\n
        1: 
        2: 
        3:  16kS digital-in/out buffer'''
        if sys.platform.startswith("win"):
            self.dwf = cdll.LoadLibrary("dwf.dll")
        elif sys.platform.startswith("darwin"):
            self.dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
        else:
            self.dwf = cdll.LoadLibrary("libdwf.so")

        print("Opening first device")
        #dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))
        # device configuration of index 3 (4th) for Analog Discovery has 16kS digital-in/out buffer
        self.dwf.FDwfDeviceConfigOpen(c_int(-1), c_int(configuration), byref(self.hdwf)) 

        if self.hdwf.value == 0:
            print("failed to open device")
            szerr = create_string_buffer(512)
            self.dwf.FDwfGetLastErrorMsg(szerr)
            print(str(szerr.value))
            quit()    
        version = create_string_buffer(16)
        self.dwf.FDwfGetVersion(version)
        print("DWF Version: "+str(version.value))

    def PowerCtrl (self, posvalue, pos_on, negvalue, neg_on):
        '''posvalue: voltage on positive feed, 
        pos_on: True|False, 
        negvalue: voltage on negative feed, 
        neg_on: True|False'''   
        # set positive voltage
        self.dwf.FDwfAnalogIOChannelNodeSet(self.hdwf, c_int(0), c_int(1), c_double(posvalue)) 
        # enable positive supply
        self.dwf.FDwfAnalogIOChannelNodeSet(self.hdwf, c_int(0), c_int(0), c_double(pos_on))
        
        # set negative voltage
        self.dwf.FDwfAnalogIOChannelNodeSet(self.hdwf, c_int(1), c_int(1), c_double(negvalue))
        # enable negative supply
        self.dwf.FDwfAnalogIOChannelNodeSet(self.hdwf, c_int(1), c_int(0), c_double(neg_on))

        if (pos_on == True or neg_on == True):
            print ("Powering up....")
            # master enable
            self.dwf.FDwfAnalogIOEnableSet(self.hdwf, c_int(True))
        else:
            # master enable
            self.dwf.FDwfAnalogIOEnableSet(self.hdwf, c_int(False))
        

    def InitI2C (self, speed, SCL, SDA):
        '''Sets up I2C communication with:\n 
        speed = transmission speed in Hz\n
        SCL = pin number for the I2C clock line\n
        SDA = pin number for the I2C data line\n'''
        # ------------ Setup I2C communication --------------
        print("Configuring I2C...")
        self.dwf.FDwfDigitalI2cRateSet(self.hdwf, c_double(speed)) # 100kHz
        self.dwf.FDwfDigitalI2cSclSet(self.hdwf, c_int(SCL)) # SCL
        self.dwf.FDwfDigitalI2cSdaSet(self.hdwf, c_int(SDA)) # SDA
        self.dwf.FDwfDigitalI2cClear(self.hdwf, byref(self.iNak))
        if self.iNak.value == 0:
            print("I2C bus error. Check the pull-ups.")
            quit()
        #time.sleep(1)

    def InitVoltmeter(self):
        self.dwf.FDwfAnalogInChannelEnableSet(self.hdwf, c_int(0), c_bool(True)) 
        self.dwf.FDwfAnalogInChannelOffsetSet(self.hdwf, c_int(0), c_double(0)) 
        self.dwf.FDwfAnalogInChannelRangeSet(self.hdwf, c_int(0), c_double(5)) 
        self.dwf.FDwfAnalogInConfigure(self.hdwf, c_bool(False), c_bool(False)) 


    def CloseAD2 (self):
        '''Switches off the power and closes the AD2 session'''
        # master disable power
        self.dwf.FDwfAnalogIOEnableSet(self.hdwf, c_int(False))

        #This function closes devices opened by the calling process
        print ("Closing Analog Discovery connection.")
        self.dwf.FDwfDeviceCloseAll()