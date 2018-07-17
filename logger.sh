#!/bin/bash 
#run as user pi from crontab -e shell script executed every X hours: 
#restart usb and copy usb filled file to db

#edit these lines with the local database name and logger log file name (txt)
DATABASE=/home/pi/wsnloggerpi/uwafarmdatabase.db
DBSCHEMA=/home/pi/wsnloggerpi/simpleschema.txt #in case we need to create a DB

LOG=/home/pi/wsnloggerpi/mylog.txt
PYTHON=/usr/bin/python3

#sync system time with RTC
#sudo /sbin/hwclock -s
#use network time at UWA farm

if [ ! -f $DATABASE ] ; then
   echo "$DATABASE not found so will create a new one" >> $LOG
   sqlite3 $DATABASE < $DBSCHEMA
   sudo chmod 775 $DATABASE
fi


#stop the usb reading process, ask nicely first, then be tough

sudo pkill -f usb2files && sudo pkill -9 -f usb2files

#restart the usb reading process
$PYTHON /home/pi/wsnloggerpi/usb2files.py &

#write the most recent file to database (ls -t is time ordered)
#TODO if more than one new file ? eg write error will only write most recent

FILE=$(ls -t /home/pi/wsnloggerpi/data/out-*.txt|head -1)
$PYTHON /home/pi/wsnloggerpi/file2db.py $DATABASE $FILE

#log history
date >>  $LOG
echo $FILE >> $LOG
cat $FILE|tail -1  >> $LOG

