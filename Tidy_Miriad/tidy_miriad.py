# Corrects the metadata from miriad images in the working folder so that TraP can read them and recognise them as LOFAR fits images
# Following this you will need to add the metadata to the images using the standard tkp-inject.py script (http://docs.transientskp.org/tkp/r1.1/tools/tkp-inject.html)

import pyfits
import glob
import os

images= glob.glob(os.path.expanduser("*.fits"))

for img in images:
    hdulist=pyfits.open(img, mode='update')
    prihdr=hdulist[0].header
    del prihdr['BLANK']
    prihdr.rename_key('EPOCH','EQUINOX')
    prihdr.update('CUNIT1','deg     ')
    prihdr.update('CUNIT2','deg     ')
    prihdr.update('CUNIT3','        ')
    prihdr.update('CUNIT4','m/s     ')
    prihdr.update('ANTENNA','        ')
    hdulist.flush()
