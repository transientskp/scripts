Data volume estimation
======================
John Swinbank, 2010
-------------------

This provides a quick & dirty estimate of the size of the visibility data
which will be produced by a given LOFAR observation. It takes two parameters
on the command line: the duration of the observation in seconds, and the
number of stations involved::

  $ python data_volume.py <duration> <stations>

Other relevant parameters (number of subbands, channels per subband,
correlator dump time) can be adjusted by editing the script.

Requires ``scipy``.
