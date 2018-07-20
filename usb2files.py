#/usr/bin/python3
#read from usb0 and write to file
import time
import serial
from datetime import datetime
import paho.mqtt.client as mqtt
import subprocess
import UWAFarmConfiguration as UWAFarm

subprocess.run(["/usr/bin/nohup","/usr/bin/python3","/home/pi/wsnloggerpi/file2db.py", "&"])
time.sleep(1)

debug = False
writetoscreen = False
MQTTConnected = False

datadir=UWAFarm.UWA_FARM_DATA_DIRECTORY


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
url = UWAFarm.CLOUD_MQTT_BROKER
topic = UWAFarm.CLOUD_MQTT_TOPIC 
mqttc.username_pw_set(UWAFarm.CLOUD_MQTT_USER_NAME,UWAFarm.CLOUD_MQTT_PASSWORD)
mqttc.tls_set()
try:
    mqttc.connect(url, UWAFarm.CLOUD_MQTT_SSL_PORT)
    MQTTConnected = True
except:
    MQTTConnected = False
    print("MQTT Could not connect")

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
                if not MQTTConnected:
                    mqttc.connect(url, UWAFarm.CLOUD_MQTT_SSL_PORT)
                    MQTTConnected = True
                mqttc.publish(topic, tstr)
            except :
                MQTTConnected = False
                if debug:
                    print ("MQTT Exception: ")

#exit gracefully
if debug:
    print(ser.close())
sys.exit(0)
