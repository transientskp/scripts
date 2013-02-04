Calculate the position angle of an observation from the zenith
==============================================================
John Swinbank, October 2012
---------------------------

Given a MeasurementSet name and an antenna ID on the command line, for every
timestep in the MeasurementSet we calculate and print the position angle
between the zenith at the position of the given antenna and the reference
direction of the observation.

Usage::

  python posangle_from_zenity.py <input.MS> <antenna_id>

Requires ``pyrap``.
