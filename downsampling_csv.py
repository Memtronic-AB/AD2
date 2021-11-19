# This routine reads the sampled data (one line per data point and downsamples this by a factor)

# 202-02-05

#read 
with open ('stegia_14.log','r') as oldfile, open ('new.csv', 'w') as newfile:
    for row in oldfile:
        if (row.find ('Time') != -1 and (row.find('(') != -1 ):    # found normal row (not headiing)
            count += 1
            if (count == factor):
                newfile.write(row)           
                count = 0
    oldfile.close()
    newfile.close()

    

