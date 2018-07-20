import paho.mqtt.client as mqtt
import time
import json
import os#, urlparse
import sqlite3
import UWAFarmConfiguration as UWAFarm

broker_address = UWAFarm.CLOUD_MQTT_BROKER
database = UWAFarm.UWA_FARM_DB_NAME
debug = False

# Define event callbacks
def on_connect(client, userdata, flags, rc):
    print("rc: " + str(rc))

def on_message(client, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    try:
        conn=sqlite3.connect(database)
        c=conn.cursor()
        if debug:
            print ("Opened DB "+database)
    except:
        if debug:
            print ("Error opening database "+database)
        sys.exit(1)
    ss=str(msg.payload.decode("utf-8")).split(',')  #extract fields from csv input string
    pktlen = len(ss)
    if debug:
        print("fields="+str(pktlen))
    #save channel info from full packets
    if (pktlen == 25):
        timestampStr = str(ss[0])
        timestampUnix = int(ss[1])
        stationID = str(ss[2])
        packetID = int(ss[3])
        rssi = int(ss[pktlen-3])
        noise = int(ss[pktlen-2])
        ssn = int(ss[pktlen-1])
        try:
            c.execute("INSERT OR IGNORE INTO channel VALUES (?,?, ?,?, ?,?,?);",(timestampStr,timestampUnix,stationID,packetID,rssi,noise,ssn))
            conn.commit()
        except:
            #error writing to DB
            if (debug):
                print ("Error writing channel info to DB "+database)

    if (pktlen == 25): ##==25 for uwafarm 8 sensors
        pos=5
        for sensorID in range(1,9):
            watercontent = float(ss[pos])
            temperature = float(ss[pos+1])
            pos=pos+2
            try:
                c.execute("INSERT OR IGNORE INTO measurement VALUES (?,?,?,?, ?,?);",(timestampStr,timestampUnix,stationID,sensorID,watercontent,temperature))
                conn.commit()
            except:
                if debug:
                    print ("Error inserting measurement info to DB "+database)
    else:
        if debug:
            print ("No soil data "+str(pktlen))

    try:
        c.close()
        conn.commit()
        conn.close()
        if debug:
            print ("Database update completed for "+database+" using "+inputfile)
    except:
        if debug:
            print ("Error closing database "+database)




def on_publish(client, obj, mid):
    print("mid: " + str(mid))

def on_subscribe(client, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(client, obj, level, string):
    print(string)

mqttc = mqtt.Client()
# Assign event callbacks
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe

# Uncomment to enable debug messages
#mqttc.on_log = on_log

# Parse CLOUDMQTT_URL (or fallback to localhost)
url = UWAFarm.CLOUD_MQTT_BROKER
topic = UWAFarm.CLOUD_MQTT_TOPIC

# Connect
mqttc.username_pw_set(UWAFarm.CLOUD_MQTT_USER_NAME,UWAFarm.CLOUD_MQTT_PASSWORD)
mqttc.tls_set()
mqttc.connect(url, UWAFarm.CLOUD_MQTT_SSL_PORT)

# Start subscribe, with QoS level 0
mqttc.subscribe(topic, 0)

# Publish a message

# Continue the network loop, exit when an error occurs
rc = 0
while rc == 0:
    rc = mqttc.loop()
print("rc: " + str(rc))
