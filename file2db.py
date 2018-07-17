#!/usr/bin/env python
#updated 16 July 2018 for python 3 and uwa farm application
#reads 8 x vmc and temp data from file and write to DB
import sys
import sqlite3

debug = False
#print(len(sys.argv))

if (len(sys.argv) < 2):
    print ("file2db.py expects 2 arguments: database inputfile")
    sys.exit(1)

database = sys.argv[1]
inputfile = sys.argv[2]
#print(database)
#print(inputfile)

try:
    fo = open(inputfile,"r")
    lines = fo.readlines()
    fo.close()
    if debug:
        print ("Opened "+inputfile+" lines= "+str(len(lines)))
except IOError:
    if debug:
        print ("Error: cannot open "+inputfile+" : error = "+str(e))
    sys.exit(1)

try:
    conn=sqlite3.connect(database)
    c=conn.cursor()
    if debug:
        print ("Opened DB "+database)
except:
    if debug:
        print ("Error opening database "+database)
    sys.exit(1)

#Farm text Packet format 3+16+4 = 25 fields
#2 added timestamps
#station, pktid, battery
#water,temp x 8
#checksum, RSSI, noise, SNR
#0001,3,6.6,
#7.20,19.0,4.96,19.0,3.84,19.0,3.76,19.0,3.76,19.0,3.82,19.0,3.63,19.0,3.88,19.0,4429,-42,-96,12

#CREATE TABLE measurement (timestampstr DATE, timestamp DATE, stationid TEXT, sensorid TEXT, watercontent NUMERIC, temperature NUMERIC UNIQUE (timestamp,stationid,sensorid) ON CONFLICT IGNORE);

for l in lines:
    ss=l.split(',')  #extract fields from csv input string
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
