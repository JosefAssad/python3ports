python3ports
============

# Usage #

code for the @python3ports twitter bot

This twitter bot is intended to be run from a task scheduler like cron.
A line in crontab like the following should work:

python /home/user/bin/python3ports/python3ports.py -u

The script has two mutually exclusive switches. The first time the script is run, use -i.
This creates the sqlite3 database and populates it with existing python3 ports.

Subsequently, -u for updating is to be used.

# License #

It's one file and it's Copyright Josef Assad 2012 and distributed under GPLv3 as specified in the file.