########################################################################
#                                                                      #
# This script simulates a series of measurements of a given number of  #
# base sources with the goal to monitor long-term query behaviour.     #
#                                                                      #
# In the main function, you may specify the following:                 #
#                                                                      #
# nbasesources  := the number of base sources                          #
# basearea      := the area in which the base sources (and             #
#                  measurements) fall                                  #
# nimages       := the number of images in which all base source is    #
#                  (re)measured                                        #
# kappa         := parameter to dexcribe the compactness of the Fisher #
#                  istribution                                         #
# freqs         := the frequencies of an image                         #
#                                                                      #
# This script generates a number of base sources within the specified  #
# area. nimages specifies for how many images we follow the base       #
# sources. For every base source a random postion is drawn from a      #
# Fisher distribution, characterised by its kappa parameter.           #
#                                                                      #
# Then the main function iterates over all the images and inserts and  #
# associates the sources in the database.                              #
#                                                                      #
# Accumulative query times are written to log files in the tkp code.   #
#                                                                      #
# TODO: Rigorous way to measure the query times.                       #
#                                                                      #
#                                                         Bart Scheers #
#                                                             May 2013 #
#                                                                      #
########################################################################

from random import *
from math import *
import os, datetime, socket
from collections import namedtuple
#from tkp.database import DataBase
from tkp.config import config
import tkp.database as tkpdb
import tkp.database.utils as dbu
import tkp.database.utils.general as dbgen
import time, sys

ExtractedSourceTuple = namedtuple("ExtractedSourceTuple",
                                ['ra', 'dec' ,
                                 'ra_fit_err' , 'dec_fit_err' ,
                                 'peak' , 'peak_err',
                                 'flux', 'flux_err',
                                 'sigma',
                                 'beam_maj', 'beam_min', 'beam_angle',
                                 'ra_sys_err', 'dec_sys_err'
                                ])

def alpha(theta, decl):
    if abs(decl) + theta > 89.9:
        return 180.0
    else:
        return degrees(abs(atan(sin(radians(theta)) / sqrt(abs(cos(radians(decl - theta)) * cos(radians(decl + theta)))))))

def gen_basesources(area, n):
    
    """Function to generate random points from uniform distribution
    """
    
    #print "\ncentre_decl, centre_ra, xtr_radius (deg):", area['centre_decl_deg'], area['centre_ra_deg'], area['xtr_radius_deg']
    
    decl_min_deg = area['centre_decl_deg'] - area['xtr_radius_deg']
    decl_max_deg = area['centre_decl_deg'] + area['xtr_radius_deg']

    # note these are inverted
    theta_min_deg = 90. - decl_max_deg
    theta_max_deg = 90. - decl_min_deg
    theta_min_rad = pi * theta_min_deg / 180.
    theta_max_rad = pi * theta_max_deg / 180.
    
    #alpha_deg = self.alpha(area['xtr_radius_deg'], area['centre_decl_deg'])
    alpha_deg = alpha(area['xtr_radius_deg'], area['centre_decl_deg'])
    #print "alpha_deg =", alpha_deg
    phi_min_deg = area['centre_ra_deg'] - alpha_deg
    phi_max_deg = area['centre_ra_deg'] + alpha_deg
    phi_min_rad = pi * phi_min_deg / 180.
    phi_max_rad = pi * phi_max_deg / 180.
    ra_min_deg = phi_min_deg
    ra_max_deg = phi_max_deg
    
    #print "decl_min_deg - decl_max_deg:",decl_min_deg, decl_max_deg
    #print "theta_min_deg - theta_max_deg:",theta_min_deg, theta_max_deg
    #print "ra_min_deg - ra_max_deg:",ra_min_deg, ra_max_deg
    
    # Generate position and flux from uniform and gaussian distribution, resp.
    bsrc = []
    idecl = int(ceil(sqrt(n)))
    ddecl = (decl_max_deg - decl_min_deg)/idecl 
    res = 120. / 3600.
    if ddecl < res: 
        print "Too dense, choose a wider field"
        sys.exit()
    ira = int(ceil(sqrt(n)))
    for i in range(idecl):
        decl0_deg = decl_min_deg + i * ddecl
        for j in range(ira):
            dalpha = alpha(ddecl, decl0_deg)
            #dalpha = self.alpha(ddecl, decl0_deg)
            dalpha = alpha(ddecl, decl0_deg)
            ra0_deg = ra_min_deg + j * dalpha
            #print "bsrc: (ra0,decl0) =", ra0_deg,decl0_deg
            
            theta0_rad = (90. - decl0_deg) * pi / 180.
            phi0_rad = ra0_deg * pi / 180.
            x0 = sin(theta0_rad) * cos(phi0_rad)
            y0 = sin(theta0_rad) * sin(phi0_rad)
            z0 = cos(theta0_rad) 

            # flux
            flux = uniform(1.,10.)
            peak = uniform(1.,10.)
            sigma = 15.
            flux_err = uniform(0.001,0.01) #flux/sigma
            peak_err = uniform(0.001,0.01) #peak/sigma
            
            bsrc.append({'theta0_rad': theta0_rad, 'phi0_rad': phi0_rad,
                        'x0': x0, 'y0': y0, 'z0': z0,
                        'decl0': decl0_deg, 'ra0': ra0_deg,
                        'peak': peak, 'peak_err': peak_err,
                        'flux': flux, 'flux_err': flux_err,
                        'sigma': sigma})
            if len(bsrc) == n:
                break
        if len(bsrc) == n:
            break
    #for i in range(n):
    #    z0 = uniform(cos(theta_min_rad), cos(theta_max_rad))
    #    theta0_rad = acos(z0)
    #    phi0_rad = uniform(phi_min_rad, phi_max_rad)
    #    x0 = sin(theta0_rad) * cos(phi0_rad)
    #    y0 = sin(theta0_rad) * sin(phi0_rad)
    #    theta0_deg = 180. * theta0_rad / pi
    #    phi0_deg = 180. * phi0_rad / pi
    #    decl0_deg = 90. - theta0_deg
    #    ra0_deg = phi0_deg
    #    
    #    # flux
    #    flux = uniform(1.,10.)
    #    peak = uniform(1.,10.)
    #    sigma = 15.
    #    flux_err = uniform(0.001,0.01) #flux/sigma
    #    peak_err = uniform(0.001,0.01) #peak/sigma
    #    
    #    bsrc.append({'theta0_rad': theta0_rad, 'phi0_rad': phi0_rad,
    #                'x0': x0, 'y0': y0, 'z0': z0,
    #                'decl0': decl0_deg, 'ra0': ra0_deg,
    #                'peak': peak, 'peak_err': peak_err,
    #                'flux': flux, 'flux_err': flux_err,
    #                'sigma': sigma})
    

    #print "\ndecl0_deg, ra0_deg:",decl0_deg, ra0_deg
    #print "theta0_deg, phi0_deg:",theta0_deg, phi0_deg
    #print "P0 (", x0, y0, z0, ")"
    #print "|P0| = ", x0**2 + y0**2 + z0**2
    
    return bsrc

#def gen_fisherpoint(self, kappa, bsrc):
def gen_fisherpoint(kappa, bsrc):
    """Generate random points around north pole in polar coordinates
    See FLE87 2.2a
    """
    
    #kappa = 2.2e8 # ra/decl_err ~ 13"
    Lambda = exp(-2.0 * kappa)
    term1 = uniform(0,1) * (1.0 - Lambda) + Lambda
    theta_rad = 2 * asin ( sqrt ( -log (term1) / (2.0 * kappa) ) )
    phi_rad = 2 * pi * uniform (0,1)
    x = sin(theta_rad) * cos(phi_rad)
    y = sin(theta_rad) * sin(phi_rad)
    z = cos(theta_rad)
    
    fsrc = bsrc.copy()
    fsrc['theta_rad'] = theta_rad
    fsrc['phi_rad'] = phi_rad
    fsrc['x'] = x
    fsrc['y'] = y
    fsrc['z'] = z
    #fsrc['x'] = bsrc['x0']
    #fsrc['y'] = bsrc['y0']
    #fsrc['z'] = bsrc['z0']
    
    #print 

    #theta_deg = 180. * theta_rad / pi
    #phi_deg = 180. * phi_rad / pi

    #print "\ntheta_deg, phi_deg:", theta_deg, phi_deg

    #decl_deg = 90. - theta_deg
    #ra_deg = phi_deg

    #print "decl_deg, ra_deg:", decl_deg, ra_deg

    #print "P (", x,y,z,")"
    #print "|P| =", x**2 + y**2 + z**2
    #print "|P - NP| =", 180*(x**2 + y**2 + (z-1.)**2)*3600./pi, "\""

    return fsrc

#def rotate(self, bsrc, fsrc):
def rotate(bsrc, fsrc):

    # Rotation matrix R(theta0, phi0) = R_z(phi0) R_y(theta0)
    a11 = cos(bsrc['phi0_rad']) * cos(bsrc['theta0_rad']) 
    a12 = -sin(bsrc['phi0_rad'])
    a13 = cos(bsrc['phi0_rad']) * sin(bsrc['theta0_rad']) 
    a21 = sin(bsrc['phi0_rad']) * cos(bsrc['theta0_rad'])
    a22 = cos(bsrc['phi0_rad'])
    a23 = sin(bsrc['phi0_rad']) * sin(bsrc['theta0_rad'])
    a31 = -sin(bsrc['theta0_rad'])
    a32 = 0.
    a33 = cos(bsrc['theta0_rad'])

    #print "    ", a11, a12, a13
    #print " A =", a21, a22, a23
    #print "    ", a31, a32, a33

    x_prime = a11 * fsrc['x'] + a12 * fsrc['y'] + a13 * fsrc['z']
    y_prime = a21 * fsrc['x'] + a22 * fsrc['y'] + a23 * fsrc['z']
    z_prime = a31 * fsrc['x'] + a32 * fsrc['y'] + a33 * fsrc['z']

    theta_prime_rad = acos(z_prime)
    if y_prime < 0:
        #print "y < 0"
        phi_prime_rad = atan2(y_prime, x_prime) + 2 * pi
    else:
        phi_prime_rad = atan2(y_prime, x_prime)

    theta_prime_deg = 180 * theta_prime_rad / pi
    phi_prime_deg = 180 * phi_prime_rad / pi

    #print "\ntheta_prime_deg, phi_prime_deg:",theta_prime_deg, phi_prime_deg

    decl_prime_deg = 90. - theta_prime_deg
    ra_prime_deg = phi_prime_deg

    rsrc = bsrc.copy()
    rsrc['decl'] = decl_prime_deg
    rsrc['ra'] = ra_prime_deg
    rsrc['x'] = x_prime
    rsrc['y'] = y_prime
    rsrc['z'] = z_prime
    #print "decl_prime_deg, ra_prime_deg:", decl_prime_deg, ra_prime_deg

    #print "bsrc=",bsrc
    #print "bsrc(ra,decl) =", bsrc['ra0'],bsrc['decl0']
    #print "rsrc(ra,decl) =", rsrc['ra'],rsrc['decl']
    #print "dist:", 3600*degrees(2*asin(sqrt((rsrc['x']-bsrc['x0'])**2+(rsrc['y']-bsrc['y0'])**2+(rsrc['z']-bsrc['z0'])**2)/2))

    #print "P' (", x_prime,y_prime,z_prime,")"
    #print "|P'| =", x_prime**2 + y_prime**2 + z_prime**2

    return rsrc

#def gen_dataset(self):
def gen_dataset(database):
    description = 'My generated dataset'
    #dataset = tkpdb.DataSet(database=self.database, 
    dataset = tkpdb.DataSet(database=database, 
                            data={'description': 'My Sim'})
    return dataset

#def gen_freqs(self):
def gen_freqs():
    freqs = [60e6]
    return freqs 

#def gen_image(self, ds, imgprops):
def gen_image(db, ds, imgprops):
    start = time.time()
    #image = tkpdb.Image(database=self.database, dataset=ds, data=imgprops)
    image = tkpdb.Image(database=db, dataset=ds, data=imgprops)
    print "\tinsert_img (",str(image.id),") -> ", str(time.time() - start), "s"
    return image.id

#def gen_xsources(self, kappa, bsrc):
def gen_xsources(kappa, bsrc):
    #fishersources = self.gen_fisherpoint(kappa, bsrc)
    fishersources = gen_fisherpoint(kappa, bsrc)
    #rsrc = self.rotate(bsrc, fishersources)
    rsrc = rotate(bsrc, fishersources)
    #print "rsrc(ra,decl)=",rsrc['ra'],rsrc['decl']
    gflux = gauss(bsrc['flux'], bsrc['flux_err'])
    #print "gauss gen: f_peak =", bsrc['peak'], "; f_peak_err =", bsrc['peak_err']
    gpeak = gauss(bsrc['peak'], bsrc['peak_err'])
    #print "-> gauss gen: gpeak =", gpeak
    #gflux_err = gauss(bsrc['flux_err'], 0.1*bsrc['flux_err'])
    gflux_err = bsrc['flux_err']
    #gpeak_err = gauss(bsrc['peak_err'], 0.1*bsrc['peak_err'])
    gpeak_err = bsrc['peak_err']
    #print "-> gauss gen: gpeak_err =", gpeak_err
    ra_fit_err = 180. / (pi * sqrt(kappa)) # in deg
    decl_fit_err = ra_fit_err
    return ExtractedSourceTuple(ra=rsrc['ra'], dec=rsrc['decl'],
                                ra_fit_err=ra_fit_err, dec_fit_err=decl_fit_err,
                                peak=gpeak, peak_err=gpeak_err,
                                flux=gflux, flux_err=gflux_err,
                                sigma=rsrc['sigma'],
                                beam_maj=100., beam_min=100.,
                                beam_angle=45.,
                                ra_sys_err=10., dec_sys_err=10.
                               )
        
####################################

def main():

    AUTOCOMMIT = config['database']['autocommit']
    db = tkpdb.DataBase()
    #s = Simul()
    ds = gen_dataset(db)
    freqs = gen_freqs()
    basearea = {'centre_decl_deg': 53., 'centre_ra_deg': 120., 'xtr_radius_deg': 5.}
    nbasesources = 100
    nimages = 100000
    #kappa = 1.e9
    # for 50x1000 we enlarge it to prevent outliers
    kappa = 2.e9
    bs = gen_basesources(basearea, nbasesources)
    #print "\nbasessources =", bs

    im_params = {'tau_time': 300, 'freq_bw': 2e6, 
                 'beam_smaj_pix': float(2.7), 'beam_smin_pix': float(2.3), 'beam_pa_rad': float(1.7),
                 'deltax': float(-0.01111), 'deltay': float(0.01111),
                 'url': "/a/file", 
                 'centre_ra': basearea['centre_ra_deg'], 'centre_decl': basearea['centre_decl_deg'], 
                 'xtr_radius' : basearea['xtr_radius_deg'] }
    starttime = datetime.datetime(2013, 1, 1) #Happy new year
    time_spacing = datetime.timedelta(seconds=600)
    for i in range(nimages):
        print socket.gethostname() + ": dataset.id =", ds.id
        for freq in freqs:
            starttime += time_spacing
            im_params['freq_eff'] = freq
            im_params['taustart_ts'] = starttime
            imgid = gen_image(db, ds, im_params)
            #print "imgid:",imgid
            xsrc = []
            for j in range(nbasesources):
                xtrsrc = gen_xsources(kappa, bs[j])
                #xsrctuple -> db_subs
                xsrc.append(xtrsrc)
            #print "\nxsrcs:", xsrc
            start = time.time()
            dbgen.insert_extracted_sources(imgid, xsrc, 'blind')
            print "\tinsert_xtrsrc -> ", str(time.time() - start), "s"
            logfile = open("/scratch/bscheers/piperun/_associate_extracted_sources.log", "a")
            start = time.time()
            tkpdb.utils.associate_extracted_sources(imgid, deRuiter_r=5.68)
            q_end = time.time() - start
            commit_end = time.time() - start
            logfile.write(str(imgid) + "," + str(q_end) + "," + str(commit_end) + "\n")

            print "\tassoc -> ", str(commit_end), "s"
            #transients = dbu.multi_epoch_transient_search(image_id=imgid, \
            #                                      eta_lim = 1.1,
            #                                      V_lim = 0.2,
            #                                      probability_threshold = 0.75,
            #                                      minpoints = 1)
            #print "\ttransients -> ", str(time.time() - start), "s"
            #print "\t\tlen(transients) =  ", len(transients)
            #mem = os.system("free -k")
            #print "i,j,mem:\n", i,j,"\n",mem
        #conn = tkpdb.DataBase().connection
        #cursor=conn.cursor()
        #cursor.execute("select count(*) from runningcatalog where dataset = %s", (ds.id,))
        #cnt = cursor.fetchall()[0][0]
        #print "cnt =",cnt
        #if cnt > nbasesources:
        #    print "Too many runcats"
        #    sys.exit();
        #if not AUTOCOMMIT:
        #    conn.commit()
        #cursor.close()

    print "\nlen(basessources) =", len(bs)

    #theta0_rad, phi0_rad, x0, y0, z0 = gen_randompoint(53., 120., 5., n=1)
    #theta_rad, phi_rad, x, y, z = gen_fisherpoint(1e7, n=1)
    #theta_prime_rad, phi_prime_rad, x_prime, y_prime, z_prime = rotate(theta0_rad, phi0_rad, x, y, z)
    ##print "|P' - P0| =", 180*((x_prime-x0)**2 + (y_prime-y0)**2 + (z_prime-z0)**2)*3600./pi,"\""
    #for i in range(len(theta_prime_rad)):
    #    print "ra, decl:", str(90. - 180.*theta_prime_rad[i]/pi), 180.*phi_prime_rad[i]/pi

if __name__ == "__main__":
    main()
