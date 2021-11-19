import Boule


Boule = Boule.Boule()

#correct
print (Boule.CreateSerial ("1121018", "01", 21, 32, 1234))

# wrong year
print (Boule.CreateSerial ("1121018", "01", 20, 32, 1234))

# wrong week
print (Boule.CreateSerial ("1121018", "01", 21, 54, 1234))

Boule.DecodeSerial('11210180121321234')

