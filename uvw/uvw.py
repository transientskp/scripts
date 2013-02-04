# uvw.py :: John Swinbank, November 2012
#
# Calculates the uvw position corresponding to a particular baseline assuming
# we are looking at the zenith.
# This is a demo which takes no arguments -- change the positions of the
# antennae by editing the script. Positions are ITRF2005.

from pyrap.measures import measures

#reference = [3826577.066110000, 461022.947639000, 5064892.786] # Reference position of CS002 from CS002-AntennaField.conf
reference = [3826577.1095, 461022.900196, 5064892.758] # LOFAR_PHASE_REFERENCE from MS
cs002d00 = [3826579.4925, 461005.105196, 5064892.578] # Read from MeasurementSet
cs002d01 = [3826578.0655, 461002.706196, 5064893.866] # Read from MeasurementSet

# The measures object is our interface to casacore
dm = measures()

#
# Set up the reference frame used for the conversion.
#

# The date is required by casacore, but since we are looking at the zenith,
# the value specified isn't important.
dm.do_frame(dm.epoch("UTC", "today"))

# Use the reference position given above.
dm.do_frame(dm.position("ITRF", "%fm" % reference[0], "%fm" % reference[1], "%fm" % reference[2]))

# Reference direction is the zenith.
dm.do_frame(dm.direction("AZEL", "0deg", "90deg"))


#
# Define the baseline to be used for conversion as the difference between the
# ITRF (x,y,z) coordinates of our antennae.
#
baseline = dm.baseline("ITRF",
    "%fm" % (cs002d00[0]-cs002d01[0]),
    "%fm" % (cs002d00[1]-cs002d01[1]),
    "%fm" % (cs002d00[2]-cs002d01[2])
)

#
# Convert our basline to uvw in metres.
#
print dm.to_uvw(baseline)['xyz']
