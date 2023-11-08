"""
   Boule specific functions Lib
   Author:  Martin Andersson
   Revision:  2021-09-20

   Requires:                       
       Python 2.7, 3
"""
ARTICLETYPE = {
            "1121033" :"CECC",
            "1121113" :"CECC",
            "1121132" :"CECC",
            "1121076" :"CEDI",
            "1121123" :"CEDI",
            "1121112" :"CEFI",
            "1121125" :"CEFI",
            "1121127" :"CEGC",
            "1121129" :"CEID",
            "1121115" :"CELC",
            "1121134" :"CELC",
            "1121098" :"CELI",
            "1121124" :"CELI",
            "1121126" :"CEOD",
            "1121071" :"CEOI",
            "1121133" :"CEOI",
            "1121034" :"CESC",
            "1121111" :"CESI",
            "1121077" :"CEVC",
            "1121130" :"CEVC",
        }

ARTICLENAME = {
            0x01:   "CECC",
            0x02:   "CEDI",
            0x03:   "CEFI",
            0x04:   "CEGC",
            0x05:   "CEID",
            0x06:   "CELC",
            0x07:   "CELI",
            0x08:   "CEOD",
            0x09:   "CEOI",
            0x0A:   "CESC",
            0x0B:   "CESI",
            0x0C:   "CEVC" }

ARTICLECODE = {
            "1121033" : "01",   # CECC r1, r2
            "1121113" : "01",   # CECC r3
            "1121132" : "01",   # CECC r4
            "1121076" : "02",   # CEDI r1
            "1121123" : "02",   # CEDI r2
            "1121112" : "03",   # CEFI r6
            "1121125" : "03",   # CEFI r7
            "1121127" : "04",   # CEGC r5
            "1121129" : "05",   # CEID r2
            "1121115" : "06",   # CELC r3
            "1121134" : "06",   # CELC r4
            "1121098" : "07",   # CELI r4
            "1121124" : "07",   # CELI r5
            "1121126" : "08",   # CEOD r6
            "1121071" : "09",   # CEOI r1
            "1121133" : "09",   # CEOI r2
            "1121034" : "0A",   # CESC r1
            "1121111" : "0B",   # CESI r4
            "1121077" : "0C",   # CEVC r3, r4
            "1121130" : "0C",   # CEVC r5
        }

class Boule():
    #def __init__ (self):
        

    def barcode2eepromstring(self, s):
        ''' decodes the string read from the barcode to a "hex"-string including crc and all.'''
        # check length
        if (len(s) != 17):
            raise Exception("Incorrect length of barcode string!")

        # first add field version
        final = "11"

        # second add board type
        artcode = ARTICLECODE.get(s[0:7], "--")
        if (artcode != "--") :
            final += artcode
        else:
            raise Exception("Unknown article number!")

        # encode string from barcode
        for i in s:
            temp=bytes.hex(i.encode())
            final += temp

        # add crc	
        crc = 0x00
        for i in range (0,len(final)-1,2):
            crc ^= int(final[i]+final[i+1],16)
        crc ^= 0x5A
        final += ascii(hex(crc))[3:5]

        return (final)