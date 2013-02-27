#!/usr/bin/python

#
# A script to calculate the elevation of a source from LOFAR (specifically from CS002)
#
# b.a.rowlinson@uva.nl
#

import datetime
import pytz
import ephem
from pyrap.quanta import quantity
from pyrap.measures import measures
from pyrap.tables import table
import time
import sys
import os
import getpass

if len(sys.argv) == 1:
	print "Usage: elevation.py <RA> <Dec> <time>"
        print "RA and Dec are in degrees"
        print "Time is in the format: 2013-02-16T04:00:00"
	sys.exit(0)

o=ephem.Observer()  
o.lat='49'  
o.long='3'  

# Customize these to set the location of your target and obs time
target_ra = float(sys.argv[1])
target_dec = float(sys.argv[2])
time = sys.argv[3]

# This is the IRTF position of CS002
x, y, z = (3826577.066110000, 461022.947639000, 5064892.786)

new_time=time.split('T')
newtime1=new_time[0]
newtime2=new_time[1]
year=int((newtime1.split('-'))[0])
month=int(newtime1.split('-')[1])
day=int(newtime1.split('-')[2])
hour=int(newtime2.split(':')[0])
minute=int(newtime2.split(':')[1])
second=int(newtime2.split(':')[2])
dt=datetime.datetime(year,month,day,hour,minute,second,0, tzinfo=pytz.utc)
jd = ephem.julian_date(ephem.Date(dt))
mjd2=(jd-2400000.5)*24*3600
dm = measures()
dm.do_frame(dm.position("ITRF", "%fm" % (x,), "%fm" % (y,), "%fm" % (z,)))
target_j2000 = dm.direction("J2000", "%fdeg" % (target_ra,), "%fdeg" % (target_dec,))
zenith = dm.direction("AZEL", "0deg", "90deg")
time = dm.epoch("UTC", quantity("%fs" % (mjd2,)))
dm.do_frame(time)
elevation = 90 - dm.separation(zenith, target_j2000).get_value("deg")
print('Elevation = '+str(elevation))
