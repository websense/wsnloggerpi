#/usr/bin/python3
#read from usb0 and write to file
import time
import serial
from datetime import datetime
import paho.mqtt.client as mqtt

debug = False
writetoscreen = False

datadir="/home/pi/wsnloggerpi/data/"


#open usb0
usbtrytimes = 5 
isopen = False
tries = 0
while ((isopen==False) and (tries < usbtrytimes)):
    tries = tries+1
    try:
        ser = serial.Serial(
            port='/dev/ttyUSB0',
            baudrate = 9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1)
        isopen = ser.isOpen()
    except:
        if debug:
            print("USB0 exception")
if (not isopen):
    sys.exit(1)

#Setup MQTT
mqttc = mqtt.Client()
url = 'm20.cloudmqtt.com'
topic = 'test1'
mqttc.username_pw_set('UWA','<REPLACEPASSWORD>')
mqttc.connect(url, 17657)

#get data and write to file
if (not writetoscreen):
    outputfile = datadir+"out-"+datetime.today().strftime("%y-%m-%d-%H-%M")+".txt";

while (True):
    dd=ser.readline().decode('UTF-8')
    if (len(dd) > 1):
        tstr=datetime.today().strftime("%Y-%m-%dT%H:%M:%SZ,")+str(int(time.time()))+","+dd
        if (debug or writetoscreen) :
            print(tstr)
        if (not writetoscreen):  # then write to file
            try:
                with open(outputfile,"a") as fo:
                            fo.write(tstr) #+"\n"
                            fo.flush()
            except :
                if debug:
                    print ("File Exception: "+outputfile)
            try:
                mqttc.publish(topic, tstr)
            except :
                if debug:
                    print ("MQTT Exception: ")

#exit gracefully
if debug:
    print(ser.close())
sys.exit(0)
