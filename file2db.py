#!/usr/bin/env python

#reads temp and humidity data from usb that has been saved in a file then write to DB

import sys
import sqlite3

debug = False
if (len(sys.argv) < 2):
        print "file2db.py expects 2 arguments - exit now"
	sys.exit(1)

database = sys.argv[1]
inputfile = sys.argv[2]

try:
        fo = open(inputfile,"r")
        lines = fo.readlines()
        fo.close()
        if debug:
                print "Opened "+inputfile+" len= "+str(len(lines))
except IOError, e:
        if debug:
                print "Error: cannot open "+inputfile+" : error = "+str(e)
        sys.exit(1)

#open database, this creates one if missing
#TODO: find test for no DB (connect param?)
try:
        conn=sqlite3.connect(database)
        curs=conn.cursor()
	if debug:
		print "Opened DB "+database
except:
        if debug:
                print "Error opening database "+database
        sys.exit(1)

for l in lines:
        ss=l.replace('\r\n','').split(',')  #extract fields from csv input string
        if (len(ss)==13):
                timestamp = ss[0]
                name = "th-"+ss[1]
                try:
                        curs.execute("INSERT OR IGNORE INTO measurement VALUES ( (?), (?), (?));",(timestamp,name+"-temperature",ss[2]))
                        curs.execute("INSERT OR IGNORE INTO measurement VALUES ( (?), (?), (?))", (timestamp,name+"-humidity",ss[3]))
                        #ignore historic values - maybe restore from these later
                        curs.execute("INSERT OR IGNORE INTO measurement VALUES ( (?), (?), (?))", (timestamp,name+"-battery",ss[10]))
                        curs.execute("INSERT OR IGNORE INTO measurement VALUES ( (?), (?), (?))", (timestamp,name+"-sigstr",ss[11]))
                        #ignore ss[12] frequency variation
                        conn.commit()
                        #ignore ss[12] frequency variation
                        conn.commit()
                except:
                        if debug:
                                print "Error inserting to DB "+database
        else:
                if debug:
                        print "Wrong input data format len= "+str(len(ss))+ " str ="+str(ss)

try:
        conn.commit()
        conn.close()
	if debug:
		print "Database update completed for "+database+" using "+inputfile
except sqlite3.Error, e:
        if debug:
                print "Error closing database "+database+str(e)





                       
