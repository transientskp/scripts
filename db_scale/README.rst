Simulate long-term observations
===============================
Bart Scheers, May 2013
-------------------------------

These scripts simulate a series of measurements for a given number of
base sources with the goal to monitor long-term query behaviour.

In the main function, you may specify the following:

* ``nbasesources``  := the number of base sources (per image)
* ``basearea``      := the area in which the base sources (and measurements) fall
* ``nimages``       := the number of images in which all base sources are (re)measured
* ``kappa``         := parameter to describe the compactness of the Fisher distribution
* ``freqs``         := the frequencies of an image

This script generates a number of base sources within the specified
area. nimages specifies for how many images we follow the base
sources. For every base source a random postion is drawn from a
Fisher distribution, characterised by its kappa parameter.

Then the main function iterates over all the images and inserts and
associates the sources in the database.

The query execution times are simply measured by wrapping the statement with
python time() functions. The measured query times are then written to log files.
The log files are named accirding to the database version, machine name,
local vs remote execution, and number of sources and images.

When running this script, use the branch ``query_monitor`` at the ``bartscheers/tkp``
repository.

Requires database.
