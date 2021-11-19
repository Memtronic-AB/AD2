# This routine collects the data from the terminal logfile generated during long-time test of 
# Stegia motor equipped shear valves.

# 2020-12-14

#read 
with open ('stegia_14.log','r') as oldfile, open ('new.csv', 'w') as newfile:
    for row in oldfile:
        if (row.find ('Loop count: ') != -1 ):    # found Loop count
            #handle the meas_text
            count = row.split(":")
            for row_n in meas_text:
                if (row_n.find('State 1') != 1):
                    state1 = row_n[8:].split("'",2)
                elif (row_n.find('State 2') != 1):
                    state2 = row_n[8:].split("'",2)
                elif (row_n.find('State 3') != 1):
                    state3 = row_n[8:].split("'",2)
                elif (row_n.find('State 4') != 1):
                    state4 = row_n[8:].split("'",2)
                elif (row_n.find('Loop time [ms]:') != 1):
                    time = row_n[8:].split(": ")
                newfile.write(count[1]+','+time[1]+','+state1+','+state2+','+state3+','+state4)                

            meas_text =''
        else:
            meas_text += row
    wholefile.close()
print ('%s' %header)

