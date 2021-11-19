"""
   Boule specific functions Lib
   Author:  Martin Andersson
   Revision:  2021-09-20

   Requires:                       
       Python 2.7, 3
"""

class Boule():
    #def __init__ (self):
    #   nope()

   
    

    def CreateSerial (self, article, rev, year, week, serial):
        ''' returns a 17 character long string which is AAAAAAARRYYWWSSSS. A basic check is performed and '-1' is returned if something is wrong.'''        
        if (serial > 9999 or serial < 0 or week > 53 or week < 1 or year < 21 or year > 99 or len(article) != 7 or len(rev) != 2):
            return "-1"
        else:
            total = article + rev + str(year) + str(week).zfill(2) + str(serial).zfill(4)
            return total

    def DecodeSerial(self,serialstring):
        ''' decodes the serial string into article number, revision, year, week and serial number.'''
        print ('Article: '+ serialstring[0:7])
        print ('Rev:     ' + serialstring[7:9])
        print ('Year:    ' + serialstring[9:11])
        print ('Week:    ' + serialstring[11:13])
        print ('Serial:  ' + serialstring[13:17])
    

    def CreateCESIdata (self, pos1, pos2_1, pos2_3, pos3):
        

    #def CreateEEPROM_Header (self, board,):
