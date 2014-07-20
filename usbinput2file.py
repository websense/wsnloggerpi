#python

#get input from usb and add date time stamp 
import serial
from datetime import datetime
import time
import sys

writetoscreen = (len(sys.argv) > 1)  #any char gives option to print to screen instead of file
debug=False

if debug:
	if writetoscreen:
		print "writing to screen"
	else:
		print "writing to file"

datadir="/home/pi/wsnloggerpi/data/"
#if usb not found keep trying for one minute (30*2s
usbstarttimout=1 #1 second
usbtrytimes=5 #60 #number of times to try
#open usb with: 1 second read timeout, 9600 baud
#port=serial.Serial()

def tryusbopen():
        if debug :
                print "USB try to open"
        isopen = False
        tries = 0
        while ((isopen == False) & (tries < usbtrytimes)):
                if debug :
                        print "." #show progress
                try:
                        port = serial.Serial("/dev/ttyUSB0",baudrate=9600)
                        if debug:
				print "try 0 " #+str(port)
                        if port.isOpen():
                                isopen = True
                except serial.SerialException, e: #could not open 0
                        if debug:
                                print "open 0 failed " #+ str(e)
                        try:
                                port = serial.Serial("/dev/ttyUSB1",baudrate=9600)
                                if debug:
					print "try 1 " #+str(port)
                                if port.isOpen():
                                        isopen = True
                        except serial.SerialException, e: #could not open 1 or 0
                                if debug:
                                        print "open 1 failed " #+ str(e)
                                tries = tries+1
                                time.sleep(usbstarttimout) #try again
        if (isopen == False):
                if debug :
                        print "Error: /dev/ttyUSB0 and /dev/ttyUSB1 open ports failed"
                sys.exit(1)
        else:
                if debug:
                        print "success"
        return port
#end tryopen

port = tryusbopen()

if (writetoscreen==False):
	outputfile = datadir+"out-"+datetime.today().strftime("%y-%m-%d-%H-%M")+".txt";

#try:
#	fo = open(outputfile,"w")
#except:
#	if debug:
#		print "Error can not open file "+outputfile
#	sys.exit(1)
	
str = "";
while True:
        try:
                response = port.read(1)
                while (response==0): #poll for input
                        response = port.read(1)
                if ((response!="\r") & (response!="\n")):
                        str += response
                if (response=="\n"):
                        str=datetime.today().strftime("%y-%m-%d %H:%M:%S,") + str
                        if (writetoscreen):
				print(str)
				str=""
                        else:
				try:
                        		with open(outputfile,"a") as fo:
                                		fo.write(str+"\n")
                                		fo.flush()
						str=""
				except:
       					if debug:
						print "Exception: "+outputfile 		
	except : #        except : #serial.SerialException, e : #IOError:
                if debug:
                        print "retry usb"
                port=tryusbopen()

if debug:
        print(port.close())
sys.exit(0)
