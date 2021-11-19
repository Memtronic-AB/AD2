import numpy as np
import csv
from itertools import zip_longest

def print_help(self): 
        '''Returns the help description'''
        print('helper description') 
        


def slopeCalc (x,y):
    ''' Calculates the slope from two lists of values (x and y) using linear curve fit.
    Requires that the length of x and y are the same.'''
    sumx = 0
    sumy = 0
    sumxy = 0
    sumx2 = 0
    length = len(x)
    for i in range(0,length):
        sumx +=x[i]
        sumy += y[i]
        sumxy += x[i] * y[i]
        sumx2 += x[i] * x[i]
    
    return (length * sumxy - sumx * sumy) *100 / (length * sumx2 - sumx * sumx)


y = [13,15,17,18,19,20,21,22,23,24]
x = [0,1,2,3,4,5,6,7,8,9]
for i in range (2,7):
        slope=slopeCalc(x[0:i], y[0:i])
        y.append(slope)
        print (str(i)+':' +str(slope))

print (y)
with open('testcsv.csv', "w") as f:
        writer = csv.writer(f)
        writer.writerow(y)

f.close()