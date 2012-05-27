#!/usr/bin/env python

# Copyright Josef Assad 2012
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import urllib2
import BeautifulSoup
import sqlite3
from sqlite3 import IntegrityError
import pdb
from twitter.api import Twitter
from twitter.oauth import OAuth
from optparse import OptionParser


usage= u'''usage: %prog [options] arg

This twitter bot is intended to be run from a task scheduler like cron.
A line in crontab like the following should work:

python /home/user/bin/python3ports/python3ports.py -u

The script has two mutually exclusive switches. The first time the script is run, use -i.
This creates the sqlite3 database and populates it with existing python3 ports.

Subsequently, -u for updating is to be used.
'''


# Obligatory configuration.
# db is the path to the sqlite3 db file
db = u''
# the following four strings are obtained from twitter
# for API usage
twitter_token=u''
twitter_token_secret=u''
twitter_consumer_key=u''
twitter_consumer_secret=u''

def fetch_p3packages():
    python3_pkgs_url = "http://pypi.python.org/pypi?:action=browse&c=533&show=all"
    conn = sqlite3.connect(db)
    c = conn.cursor()
    list_of_package_dics = []

    p3_data = urllib2.urlopen(python3_pkgs_url).read()
    p3_soup = BeautifulSoup.BeautifulSoup(p3_data)
    p3_table = p3_soup.find("table", "list")
    p3_rows = p3_table.findAll("tr")
    for i in p3_rows[1:-1]:
        cells = i.findAll("td")
        package_dict = {}
        package_dict['name'] = cells[0].a.renderContents()
        package_dict['link'] = u'http://www.python.org' + cells[0].a['href']
        list_of_package_dics.append(package_dict)
    return list_of_package_dics

def update():
    twit = Twitter(auth=OAuth(
        token=twitter_token,
        token_secret=twitter_token_secret,
        consumer_key=twitter_consumer_key,
        consumer_secret=twitter_consumer_secret))
    conn = sqlite3.connect(db)
    c = conn.cursor()
    for i in fetch_p3packages():
        try:
            c.execute("INSERT INTO packages(name) values (?)", (i['name'],))
            twit.statuses.update(status="%s has been ported to #python3 %s" % (i['name'], i['link']))
        except IntegrityError:
            pass
            #print "skipping %s" % i['name']
    conn.commit()

def initialise():
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('''CREATE TABLE packages (name text primary key)''')
    for i in fetch_p3packages():
        try:
            c.execute("INSERT INTO packages(name) values (?)", (i['name'],))
        except IntegrityError:
            pass
            #print "skipping %s", i['name']
    conn.commit()

    
def main():
    parser = OptionParser(usage)
    parser.add_option("-i", "--initialise", action="store_true", dest="initialise")
    parser.add_option("-u", "--update", action="store_true", dest="update")
    (options, args) = parser.parse_args()
    if options.initialise: initialise()
    elif options.update: update()
    else: parser.error("bad argument")


if __name__ == "__main__":
    main()
