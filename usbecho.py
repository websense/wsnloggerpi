#python

#get input from usb, add date time stamp, echo to stdout
import serial
from datetime import datetime
import time
import sys

#flush with sys.stdout.flush()

#step 1: try opening a USB port
port = serial.Serial()
try:
	port = serial.Serial("/dev/ttyUSB0",baudrate=9600)
except serial.SerialException, e: #could not open 1 or 0
	print "open USB0 failed " #+ str(e)
if (port.isOpen() == False):
	try:
		port = serial.Serial("/dev/ttyUSB1",baudrate=9600)
	except serial.SerialException, e: #could not open 1 or 0
		print "open USB1 failed " #+ str(e)
        	sys.exit(1)


#step 2: poll for data	
str = ""
while True:
        try:
                response = port.read(1)
                while (response==0): #poll for input
                        response = port.read(1)
                if ((response!="\r") & (response!="\n")):
                        str += response
                if (response=="\n"):
                        str=datetime.today().strftime("%y-%m-%d %H:%M:%S,") + str
                        print(str)
			str=""
	except : 
		print "USB read exception" #+ str(e)
		sys.exit(1)

#step 3: if loop exit by kill signal then close and exit
port.close()
sys.exit(0)
