#!/usr/bin/env python

# posangle_from_zenith.py :: John Swinbank, October 2012
#
# Given a MeasurementSet name and an antenna ID on the command line, for every
# timestep in the MeasurementSet we calculate and print the position angle
# between the zenith at the position of the given antenna and the reference
# direction of the observation.
#
# Usage::
#
#   python posangle_from_zenity.py <input.MS> <antenna_id>

import sys
from pyrap.tables import table
from pyrap.measures import measures
from pyrap.quanta import quantity

def radec_to_azel(pointing, time, position):
    # All inputs as measures
    # Returns a measure giving az/el of ra/dec at given time & position
    dm = measures()
    dm.do_frame(time)
    dm.do_frame(position)
    return dm.measure(pointing, 'azel')

def get_times(ms):
    # Returns an array of the unique times in the MS
    timetable = ms.sort('unique TIME')
    return timetable.getcol('TIME')

def get_station_position(ms, antenna):
    # Returns ITRF coordinates of the given antenna ID as a position measure
    fieldtable = table(ms.getkeyword('LOFAR_ANTENNA_FIELD'))
    postable = fieldtable.query('ANTENNA_ID==%d' % (antenna,))
    x, y, z = postable.getcol('POSITION')[0]
    dm = measures()
    return dm.position("itrf", "%fm" % (x,), "%fm" % (y,), "%fm" % (z,))

def get_pointing_direction(ms):
    # Returns J2000 RA, dec of reference direction in radians
    fieldtable = table(ms.getkeyword('FIELD'))
    ra, dec = fieldtable.getcol('REFERENCE_DIR')[0][0]
    dm = measures()
    return dm.direction('j2000', "%frad" % (ra,), "%frad" % (dec,))

if __name__ == "__main__":
    msname = sys.argv[1] # MeasurementSet name provided on command line
    antenna = int(sys.argv[2]) # Antenna ID on command line

    dm = measures()
    ms = table(msname)

    times = get_times(ms)
    position = get_station_position(ms, antenna)
    pointing = get_pointing_direction(ms)
    zenith_azel = dm.direction('azel', '0deg', '90deg')

    for time in times:
        time = dm.epoch("UTC", quantity("%fs" % (time,)))
        target_azel = radec_to_azel(pointing, time, position)
        print time, dm.posangle(zenith_azel, target_azel)
