wsnloggerpi
===========

Sensor network base station: logs input from usb port to files and a database

From file /home/pi/wsnloggerpi/README
instructions for setting up a sensor network logger on a raspberry pi

0. cd /home/pi/wsnloggerpi

1. (if first time) create the simple data logger database (give yours a unique name)
DATABASE=kal001database.db
sqlite3 $DATABASE < simpleschema.txt
chmod 755 $DATABASE

2. set passwords and other config info in UWAFarmConfiguration.py

3. edit usb2files.py and file2db.py if any changes to packet format for incoming data from the network

4. check the pi clock is working and cron has the same time
sudo date --set 2014-07-19
sudo date --set 21:08:00
sudo /etc/init.d/cron restart

5. check sudo crontab - e and edit if necessary (the distribution version updates the DB every 3 hours)
MAILTO=?"
0 */3 * * *  /home/pi/websensepi/logger.sh

6. plug in a USB delivering messages, reboot the pi, check input is on USB and go

7. to check progress:
plug in an ethernet cable and check the pi's address (eg 192.168.2.2)
ssh pi@192.168.2.2
cd wsnloggerpi
cat data/* | tail -10
ls -l *.db

8. to copy the database or data files to another computer
change to your local data directory
sftp pi@192.168.2.2
Then in the sftp interface:
        cd wsnloggerpi
        get *.db
        mget data/*
        quit

9. for software updates see https://github.com/websense/wsnloggerpi

