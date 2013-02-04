MeasurementSet Differencing
===========================
John Swinbank, January 2013
---------------------------

Given two input MeasurementSets, which must be of the same shape, we
subtract the contents of the DATA column of the second from that of the
first, and write the result out as a new MeasurementSet. The new
MeasurementSet has the union of the flags of the input MeasurementSets, and
all other metadata is directly copied from the first input.

Usage::

  python input1.MS input2.MS output.MS

Requires ``pyrap``.
