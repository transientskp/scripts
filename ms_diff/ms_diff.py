# ms_diff.py :: John Swinbank, 2013-01-23
#
# Given two input MeasurementSets, which must be of the same shape, we
# subtract the contents of the DATA column of the second from that of the
# first, and write the result out as a new MeasurementSet. The new
# MeasurementSet has the union of the flags of the input MeasurementSets, and
# all other metadata is directly copied from the first input.
#
# Usage::
#
#   python input1.MS input2.MS output.MS

import sys
from pyrap.tables import table

if __name__ == "__main__":
    in1, in2, out = sys.argv[1], sys.argv[2], sys.argv[3]

    t1 = table(in1).sort("TIME, ANTENNA1, ANTENNA2")
    t2 = table(in2).sort("TIME, ANTENNA1, ANTENNA2")
    t3 = t1.copy(out, deep=True)
    t3.close()
    tout = table(out, readonly=False).sort("TIME, ANTENNA1, ANTENNA2")

    tout.putcol("DATA", t1.getcol("DATA") - t2.getcol("DATA"))
    tout.putcol("FLAG", t1.getcol("FLAG") & t2.getcol("FLAG"))
    tout.putcol("FLAG_ROW", t1.getcol("FLAG_ROW") & t2.getcol("FLAG_ROW"))
    tout.flush()
    tout.close()
    t1.close()
    t2.close()
