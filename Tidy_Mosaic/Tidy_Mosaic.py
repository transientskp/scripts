import pyfits
import glob
import os

images = glob.glob(os.path.expanduser("*.fits"))
for fits_img in images:
    fits_file = pyfits.open(fits_img, mode='update')
    header = fits_file[0].header
    header['ANTENNA']=''
    fits_file.flush()
    fits_file.close()
